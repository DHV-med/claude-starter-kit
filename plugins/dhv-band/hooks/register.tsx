// dhv-band: one quiet row above the prompt.
// 1. how long the chat's short-term memory (the prompt cache) stays warm,
// 2. how full the chat is, 3. a keep-warm switch, 4. a notes + new chat button.
// Every reader fails soft: an error leaves the row empty, never the chat broken.
import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register, Timer } from 'claude-code'

import type { Lang, Reply, Warm } from '../types'
import {
  WARM_OFF,
  WORDS,
  chatText,
  clockText,
  isRefreshDue,
  langFromSettings,
  lifetimeFromTranscript,
  remainingMs,
  warmStopReason,
} from './logic'

const reply = atom({ plugin: 'dhv-band', key: 'reply' } as const, null as Reply | null, {
  shape: 'reply-1',
})
const ttl = atom({ plugin: 'dhv-band', key: 'ttl' } as const, null as number | null)
const percent = atom({ plugin: 'dhv-band', key: 'percent' } as const, null as number | null)
const nowAtom = atom({ plugin: 'dhv-band', key: 'now' } as const, 0)
const lang = atom({ plugin: 'dhv-band', key: 'lang' } as const, 'he' as Lang | null)
const isBroken = atom({ plugin: 'dhv-band', key: 'isBroken' } as const, false)
const isHidden = atom({ plugin: 'dhv-band', key: 'isHidden' } as const, false)
const warm = atom({ plugin: 'dhv-band', key: 'warm' } as const, WARM_OFF as Warm, {
  shape: 'warm-1',
})

// Who counts as the person sending a message (keep-warm stops then).
const PERSON = new Set(['composer', 'bridge', 'sdk', 'slack-ping'])
// Kept as short as possible: the fork re-reads the cached chat, adds nothing to it.
const KEEP_WARM_PROMPT =
  'Cache keep-alive check. You have no tools. Reply with the single word OK straight away, without thinking it over.'
const MAX_TRANSCRIPT_BYTES = 50 * 1024 * 1024

type $ = EngineInterface

// Module variables start over on a reload; they hold nothing a drawing reads.
// (Helpers that take `$` must be top-level function declarations: validate
// follows `$` only into those.)
const mod = {
  stopTicker: undefined as Timer | undefined,
  isWorking: false,
  isForking: false,
  transcriptPath: '',
  ttlTries: 0,
}

async function loadLanguage($: $): Promise<void> {
  try {
    const home = (await $.env.get('USERPROFILE')) ?? (await $.env.get('HOME'))
    if (home === undefined) {
      await update($, lang, () => 'he')
      return
    }
    const path = `${home.replace(/[\\/]+$/, '')}/.claude/dhv-kit.json`
    if (!(await $.fs.exists(path))) {
      await update($, lang, () => 'he')
      return
    }
    const text = await $.fs.read(path)
    await update($, lang, () => langFromSettings(text))
  } catch {
    // unreadable or malformed settings: the row stays empty
    await update($, lang, () => null).catch(() => undefined)
  }
}

async function learnLifetime($: $): Promise<void> {
  if (mod.transcriptPath === '' || mod.ttlTries >= 3) return
  mod.ttlTries += 1
  try {
    const stat = await $.fs.stat(mod.transcriptPath)
    if (stat.kind !== 'file' || stat.size > MAX_TRANSCRIPT_BYTES) return
    const found = lifetimeFromTranscript(await $.fs.read(mod.transcriptPath))
    if (found !== null) await update($, ttl, () => found)
  } catch {
    await update($, isBroken, () => true).catch(() => undefined)
  }
}

async function keepWarm($: $, now: number, left: number): Promise<void> {
  const state = await read($, warm)
  if (!state.isOn) return
  if (warmStopReason(state, now, left) !== null) {
    await update($, warm, () => WARM_OFF)
    return
  }
  if (mod.isWorking || mod.isForking || !isRefreshDue(state, now, left)) return
  mod.isForking = true
  try {
    await update($, warm, w => ({ ...w, lastTryAt: now }))
    const r = await $.model.fork({ prompt: KEEP_WARM_PROMPT })
    // A refresh counts only when the cache actually served the chat.
    const isServed = r.isAnswered && r.usage.cache_read_input_tokens > 0
    const after = await $.clock.now()
    const current = await read($, warm)
    if (!current.isOn) return // switched off meanwhile (the person typed)
    if (isServed) {
      await update($, reply, () => ({ at: after }))
      await update($, warm, w => ({ ...w, refreshes: w.refreshes + 1, failures: 0 }))
    } else {
      await update($, warm, w => ({ ...w, failures: w.failures + 1 }))
    }
    const next = await read($, warm)
    if (warmStopReason(next, after, 1) !== null) await update($, warm, () => WARM_OFF)
  } catch {
    await update($, warm, w => ({ ...w, failures: w.failures + 1 })).catch(() => undefined)
  } finally {
    mod.isForking = false
  }
}

async function tick($: $): Promise<void> {
  const now = await $.clock.now()
  const last = await read($, reply)
  if (last === null) return
  await update($, nowAtom, () => now)
  if ((await read($, ttl)) === null) await learnLifetime($)
  const left = remainingMs(now, last.at, await read($, ttl))
  await keepWarm($, now, left)
}

async function switchWarmOff($: $): Promise<void> {
  const state = await read($, warm)
  if (state.isOn) await update($, warm, () => WARM_OFF)
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    try {
      await $.command.register({
        name: 'band',
        description: 'Hide or show the row above the prompt',
        argumentHint: 'hide | show',
      })
      const stored = await $.store.get('isHidden')
      await update($, isHidden, () => stored === true)
      await loadLanguage($)
      const usage = await $.session.usage()
      if (usage.context.percent !== undefined) {
        const p = usage.context.percent
        await update($, percent, () => p)
      }
    } catch {
      await update($, isBroken, () => true).catch(() => undefined)
    }
    mod.stopTicker?.cancel()
    mod.stopTicker = $.clock.every(1000, () => {
      void tick($).catch(() => undefined)
    })

    return next(e)
  })

  on('session.end', async ($, e, next) => {
    if (e.reason === 'clear') {
      // a new chat: nothing of the old one's clock carries over
      try {
        await update($, reply, () => null)
        await update($, ttl, () => null)
        await update($, percent, () => null)
        await update($, warm, () => WARM_OFF)
        await update($, isBroken, () => false)
        mod.transcriptPath = ''
        mod.ttlTries = 0
      } catch {
        // nothing to undo
      }
    }

    return next(e)
  })

  on('command.run', { command: 'band' }, async ($, e) => {
    const words = WORDS[(await read($, lang)) ?? 'he']
    const arg = e.args.trim().toLowerCase()
    if (arg === 'hide' || arg === 'show') {
      const hide = arg === 'hide'
      await update($, isHidden, () => hide)
      await $.store.set('isHidden', hide)

      return { text: hide ? words.hidden : words.shown }
    }

    return { text: words.usage }
  })

  on('turn.start', async ($, e, next) => {
    if (e.agentId === undefined) mod.isWorking = true

    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    if (e.agentId === undefined) mod.isWorking = false

    return next(e)
  })

  // Each main-thread model response restarts the clock.
  on('turn.step', async function* ($, e, next) {
    const r = yield* next(e)
    if (e.agentId !== undefined || r.usage === null) return
    try {
      const at = await $.clock.now()
      await update($, reply, () => ({ at }))
      await update($, nowAtom, () => at)
      await update($, isBroken, () => false)
    } catch {
      await update($, isBroken, () => true).catch(() => undefined)
    }
  })

  // The usage breakdown (one-hour or five-minute lifetime) is only in the
  // transcript; the Stop event says where it is. Read later, from the ticker.
  on('classic.Stop', async ($, e, next) => {
    if (typeof e.transcript_path === 'string' && e.transcript_path !== mod.transcriptPath) {
      mod.transcriptPath = e.transcript_path
      mod.ttlTries = 0
    }

    return next(e)
  }).catch(($, e, next) => next(e))

  on('session.measure', async ($, e, next) => {
    try {
      const p = e.context.percent
      if (p !== undefined) await update($, percent, () => p)
    } catch {
      await update($, isBroken, () => true).catch(() => undefined)
    }

    return next(e)
  })

  on('prompt.submit', async ($, e, next) => {
    if (PERSON.has(e.origin.kind)) await switchWarmOff($).catch(() => undefined)

    return next(e)
  }).catch(($, e, next) => next(e))

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey) return next(e)
    if (await read($, isHidden)) return next(e)
    const language = await read($, lang)
    if (language === null || (await read($, isBroken))) return next(e)
    const last = await read($, reply)
    const fill = await read($, percent)
    if (last === null && fill === null) return next(e)

    const words = WORDS[language]
    const now = Math.max(await read($, nowAtom), last?.at ?? 0)
    const lifetime = await read($, ttl)
    const keep = await read($, warm)
    const clock = last === null ? null : clockText(language, now, last.at, lifetime)
    const isWarm = clock !== null && clock.tone !== 'cold'
    const dir = language === 'he' ? 'rtl' : 'ltr'
    const { Box, Button, Text } = $.ui.resolve(e)

    return (
      <Box flexDirection="row" gap={2}>
        {clock !== null && (
          <Text
            dir={dir}
            color={clock.tone === 'warning' ? 'warning' : clock.tone === 'calm' ? 'success' : undefined}
            dimColor={clock.tone === 'cold'}
          >
            {clock.text}
          </Text>
        )}
        {fill !== null && (
          <Text dir={dir} dimColor>
            {chatText(language, fill)}
          </Text>
        )}
        {(isWarm || keep.isOn) && (
          <Button
            key="keep-warm"
            label={keep.isOn ? words.keepWarmOn : words.keepWarm}
            variant={keep.isOn ? 'primary' : undefined}
            dimColor={!keep.isOn}
            onPress={async () => {
              const at = await $.clock.now()
              await update($, warm, w =>
                w.isOn ? WARM_OFF : { ...WARM_OFF, isOn: true, startedAt: at },
              )
            }}
          />
        )}
        <Button
          key="handoff"
          label={words.handoff}
          dimColor
          onPress={async () => {
            await switchWarmOff($)
            const commands = await $.command.list()
            if (!commands.some(c => c.name === 'handoff')) {
              $.ui.toast(words.noHandoff)
              return
            }
            void $.command.run({ command: 'handoff' }).catch(() => $.ui.toast(words.noHandoff))
          }}
        />
      </Box>
    )
  })
}
