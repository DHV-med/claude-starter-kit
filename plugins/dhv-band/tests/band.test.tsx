import { expect, mock, test } from 'claude-code/testing'
import type { Engine } from 'claude-code/testing'
import type { On } from 'claude-code'

import {
  MINUTE,
  chatText,
  clockText,
  langFromSettings,
  lifetimeFromTranscript,
} from '../hooks/logic'

const T0 = 1_000_000_000

const BAND = {
  plugin: 'dhv-band',
  component: 'AbovePrompt',
  props: {
    hasSurvey: false,
    isCollapsed: false,
    isWorking: false,
    maxRows: 10,
    bodyColumns: 100,
    scroll: { offset: 0, bodyRows: 10 },
    view: {},
  },
} as const

const SURFACES = ['terminal', 'desktop', 'vscode', 'mobile'] as const

/** One transcript line of a main-thread reply with this cache-write breakdown. */
function replyLine(oneHour: number, fiveMin: number): string {
  return JSON.stringify({
    type: 'assistant',
    isSidechain: false,
    message: {
      usage: {
        cache_creation: {
          ephemeral_1h_input_tokens: oneHour,
          ephemeral_5m_input_tokens: fiveMin,
        },
      },
    },
  })
}

type World = {
  /** dhv-kit.json text; undefined = no file. */
  settings?: string
  transcript?: string
  store?: Record<string, unknown>
  /** cache tokens the keep-warm fork reports reading. */
  forkReads?: number
}

/** The engine beneath the plugin, then a session start. */
async function boot($: Engine, on: On, w: World) {
  const clock = mock.clock(on, { now: T0 })
  mock.store(on, w.store ?? {})
  mock.env(on, { USERPROFILE: '/home/someone' })
  const forks: string[] = []
  on('command.register', () => ({ value: { command: 'band' } }))
  on('command.list', () => ({ value: [] }))
  on('session.usage', () => ({
    value: { startedAt: T0, context: { window: 200_000, tokens: 62_000, percent: 31 }, rateLimits: [] },
  }))
  on('fs.exists', (_, e) => ({
    value: e.path.endsWith('dhv-kit.json') ? w.settings !== undefined : true,
  }))
  on('fs.read', (_, e) => ({
    value: e.path.endsWith('dhv-kit.json') ? (w.settings ?? '') : (w.transcript ?? ''),
  }))
  on('fs.stat', () => ({ value: { kind: 'file', size: 100, mtimeMs: 0, isLink: false } }))
  on('model.fork', (_, e) => {
    forks.push(e.prompt)
    const usage = {
      input_tokens: 5,
      output_tokens: 1,
      cache_read_input_tokens: w.forkReads ?? 50_000,
      cache_creation_input_tokens: 0,
    }
    return { value: { isAnswered: true, text: 'OK', usage } }
  })
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('prompt.submit', (_, e) => ({ text: e.text }))
  on('classic.Stop', () => ({}))
  on('turn.step', async function* (_, e) {
    return {
      turnId: e.turnId,
      index: e.index,
      answer: 'hi',
      toolUses: [],
      stopReason: 'end_turn',
      usage: {
        input_tokens: 1,
        output_tokens: 1,
        cache_read_input_tokens: 0,
        cache_creation_input_tokens: 10,
        model: 'm',
      },
    }
  })
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  return { clock, forks }
}

/** One main-thread model reply, then the Stop that names the transcript. */
async function reply($: Engine) {
  const stream = $.turn.step({ turnId: 't1', index: 0, model: 'm', messageCount: 1 })
  for await (const _ of stream) {
    // drain
  }
  await $.classic.Stop({ stop_hook_active: false, transcript_path: '/t/chat.jsonl' })
}

async function allText(ui: { findAll: (q: object) => Promise<ReadonlyArray<{ text?: string }>> }) {
  const found = await ui.findAll({})

  return found.map(f => f.text ?? '').join(' | ')
}

// ---- pure text -------------------------------------------------------------

test('warm countdown text, English and Hebrew', () => {
  const at = T0
  const now = at + 17 * MINUTE + 50_000 // 42:10 left of 60
  expect(clockText('en', now, at, 60)).toEqual({ text: 'warm 42:10', tone: 'calm' })
  expect(clockText('he', now, at, 60).text).toBe('חם 42:10')
})

test('warning tone in the last fifth only', () => {
  expect(clockText('en', T0 + 48 * MINUTE + 1000, T0, 60).tone).toBe('warning')
  expect(clockText('en', T0 + 47 * MINUTE, T0, 60).tone).toBe('calm')
  expect(clockText('en', T0 + 4 * MINUTE + 1000, T0, 5).tone).toBe('warning')
})

test('cold text', () => {
  expect(clockText('en', T0 + 72 * MINUTE, T0, 60)).toEqual({ text: 'cold 12 min', tone: 'cold' })
  expect(clockText('he', T0 + 72 * MINUTE, T0, 60).text).toBe("קר 12 דק'")
})

test('5-minute vs 60-minute lifetime from the reply usage', () => {
  expect(lifetimeFromTranscript([replyLine(0, 900), replyLine(1200, 0)].join('\n'))).toBe(60)
  expect(lifetimeFromTranscript([replyLine(1200, 0), replyLine(0, 900)].join('\n'))).toBe(5)
  // the newest reply wrote nothing new: the one before it decides
  expect(lifetimeFromTranscript([replyLine(0, 900), replyLine(0, 0)].join('\n'))).toBe(5)
  expect(lifetimeFromTranscript('not json\n')).toBe(null)
  // unknown counts as 60
  expect(clockText('en', T0 + 10 * MINUTE, T0, null).text).toBe('warm 50:00')
  expect(clockText('en', T0 + 1 * MINUTE, T0, 5).text).toBe('warm 4:00')
})

test('percentage', () => {
  expect(chatText('en', 31.4)).toBe('chat 31%')
  expect(chatText('he', 31.6)).toBe("צ'אט 32%")
  expect(chatText('en', 140)).toBe('chat 100%')
})

test('language setting', () => {
  expect(langFromSettings('{"language":"en"}')).toBe('en')
  expect(langFromSettings('{"language":"he"}')).toBe('he')
  expect(langFromSettings('{}')).toBe('he')
  expect(() => langFromSettings('{oops')).toThrow()
})

// ---- the band, mounted -----------------------------------------------------

test('English band counts down, then turns cold, on every surface', async ($, on) => {
  const { clock } = await boot($, on, {
    settings: '{"language":"en"}',
    transcript: replyLine(1200, 0),
  })
  await reply($)
  await clock.advance(17 * MINUTE + 50_000)
  for (const surface of SURFACES) {
    const ui = await $.ui.mount({ ...BAND, surface })
    expect((await ui.find({ type: 'Text', text: /^warm/ }))?.text).toBe('warm 42:10')
    expect((await ui.find({ type: 'Text', text: /^chat/ }))?.text).toBe('chat 31%')
    expect(await ui.find({ type: 'Button', key: 'handoff' })).toBeDefined()
    await ui.unmount()
  }
  await clock.advance(54 * MINUTE + 10_000) // 12 minutes past the hour
  const ui = await $.ui.mount({ ...BAND, surface: 'terminal' })
  expect((await ui.find({ type: 'Text', text: /^cold/ }))?.text).toBe('cold 12 min')
  expect(await ui.find({ type: 'Button', key: 'keep-warm' })).toBeUndefined()
  await ui.unmount()
})

test('a five-minute reply gives a five-minute clock', async ($, on) => {
  const { clock } = await boot($, on, {
    settings: '{"language":"en"}',
    transcript: replyLine(0, 900),
  })
  await reply($)
  await clock.advance(61_000)
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  expect((await ui.find({ type: 'Text', text: /^warm/ }))?.text).toBe('warm 3:59')
  await ui.unmount()
})

test('Hebrew by default when there is no settings file', async ($, on) => {
  const { clock } = await boot($, on, { transcript: replyLine(1200, 0) })
  await reply($)
  await clock.advance(1000)
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  expect((await ui.find({ type: 'Text', text: /^חם/ }))?.text).toBe('חם 59:59')
  expect((await ui.find({ type: 'Text', text: /%/ }))?.text).toBe("צ'אט 31%")
  expect((await ui.find({ type: 'Button', key: 'handoff' }))?.text).toBe("סיכום + צ'אט חדש")
  await ui.unmount()
})

test('nothing before the first reply but the chat fill', async ($, on) => {
  await boot($, on, { settings: '{"language":"en"}' })
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  expect(await ui.find({ type: 'Text', text: /warm|cold/ })).toBeUndefined()
  expect((await ui.find({ type: 'Text', text: /^chat/ }))?.text).toBe('chat 31%')
  await ui.unmount()
})

test('a broken settings file leaves the row empty', async ($, on) => {
  await boot($, on, { settings: '{oops', transcript: replyLine(1200, 0) })
  await reply($)
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  expect(await ui.find({ type: 'Text' })).toBeUndefined()
  expect(await ui.find({ type: 'Button' })).toBeUndefined()
  await ui.unmount()
})

test('/band hide hides the row and is remembered; /band show brings it back', async ($, on) => {
  await boot($, on, { settings: '{"language":"en"}', transcript: replyLine(1200, 0) })
  await reply($)
  const run = (args: string) =>
    $.command.run({
      command: 'band',
      args,
      origin: { kind: 'composer' },
      presentation: { isFullscreen: false, columns: 80 },
    })
  expect((await run('hide')).text).toMatch(/hidden/)
  let ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  expect(await ui.find({ type: 'Text' })).toBeUndefined()
  await ui.unmount()
  await run('show')
  ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  expect(await ui.find({ type: 'Text', text: /^warm/ })).toBeDefined()
  await ui.unmount()
})

test('hidden from an earlier session stays hidden', async ($, on) => {
  await boot($, on, {
    settings: '{"language":"en"}',
    transcript: replyLine(1200, 0),
    store: { isHidden: true },
  })
  await reply($)
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  expect(await ui.find({ type: 'Text' })).toBeUndefined()
  await ui.unmount()
})

test('no dollar sign anywhere in the drawn text', async ($, on) => {
  const { clock } = await boot($, on, { settings: '{"language":"en"}', transcript: replyLine(1200, 0) })
  await reply($)
  for (const step of [1000, 50 * MINUTE, 20 * MINUTE]) {
    await clock.advance(step)
    for (const surface of SURFACES) {
      const ui = await $.ui.mount({ ...BAND, surface })
      const text = await allText(ui)
      expect(text.length > 0).toBe(true)
      expect(text.includes('$')).toBe(false)
      await ui.unmount()
    }
  }
})

test('no dollar sign in the Hebrew band', async ($, on) => {
  await boot($, on, { transcript: replyLine(1200, 0) })
  await reply($)
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const text = await allText(ui)
  expect(text.includes('חם')).toBe(true)
  expect(text.includes('$')).toBe(false)
  await ui.unmount()
})

test('keep warm refreshes 45 seconds before the end and stops when the person types', async ($, on) => {
  const { clock, forks } = await boot($, on, {
    settings: '{"language":"en"}',
    transcript: replyLine(0, 900),
  })
  await reply($)
  await clock.advance(1000)
  let ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'keep-warm' })
  expect((await ui.find({ type: 'Button', key: 'keep-warm' }))?.text).toBe('Keep warm: on')
  await ui.unmount()

  await clock.advance(4 * MINUTE) // 4:01 in: 59 s left, nothing yet
  expect(forks.length).toBe(0)
  await clock.advance(20_000) // under 45 s left: one refresh
  expect(forks.length).toBe(1)
  ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  expect((await ui.find({ type: 'Text', text: /^warm/ }))?.text).toMatch(/^warm 4:5\d$/)
  await ui.unmount()

  await $.prompt.submit({ text: 'next question', wait: false, origin: { kind: 'composer' } })
  ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  expect((await ui.find({ type: 'Button', key: 'keep-warm' }))?.text).toBe('Keep warm')
  await ui.unmount()
})

test('keep warm gives up after 3 failed refreshes in a row', async ($, on) => {
  const { clock, forks } = await boot($, on, {
    settings: '{"language":"en"}',
    transcript: replyLine(0, 900),
    forkReads: 0,
  })
  await reply($)
  await clock.advance(1000)
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'keep-warm' })
  await ui.unmount()
  await clock.advance(4 * MINUTE + 59_000) // through the whole lead window
  expect(forks.length).toBe(3)
  const after = await $.ui.mount({ ...BAND, surface: 'desktop' })
  expect(await after.find({ type: 'Text', text: /^cold/ })).toBeDefined()
  expect(await after.find({ type: 'Button', key: 'keep-warm' })).toBeUndefined()
  await after.unmount()
})
