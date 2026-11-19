// Pure helpers for dhv-band: no `$`, so the tests can call them directly.
import type { Lang, Warm } from '../types'

export const MINUTE = 60_000
export const DEFAULT_TTL_MIN = 60
/** Refresh this long before the cache would run out. */
export const REFRESH_LEAD_MS = 45_000
/** Wait this long between two refresh tries. */
export const RETRY_GAP_MS = 10_000
export const MAX_REFRESHES = 12
export const MAX_FAILURES = 3
export const MAX_ON_MS = 2 * 60 * MINUTE

export const WORDS = {
  en: {
    warm: 'warm',
    cold: 'cold',
    min: 'min',
    chat: 'chat',
    keepWarm: 'Keep warm',
    keepWarmOn: 'Keep warm: on',
    handoff: 'Notes + new chat',
    noHandoff: 'The /handoff command is not set up on this computer.',
    hidden: 'The band is hidden. Type /band show to bring it back.',
    shown: 'The band is shown.',
    usage: 'Use /band hide or /band show.',
  },
  he: {
    warm: 'חם',
    cold: 'קר',
    min: "דק'",
    chat: "צ'אט",
    keepWarm: 'שמור חם',
    keepWarmOn: 'שמור חם: פועל',
    handoff: "סיכום + צ'אט חדש",
    noHandoff: 'הפקודה /handoff לא מותקנת במחשב הזה.',
    hidden: 'השורה מוסתרת. כדי להחזיר אותה: /band show',
    shown: 'השורה מוצגת.',
    usage: 'אפשר /band hide או /band show.',
  },
} as const

export type Tone = 'calm' | 'warning' | 'cold'

export const WARM_OFF: Warm = {
  isOn: false,
  startedAt: 0,
  refreshes: 0,
  failures: 0,
  lastTryAt: 0,
}

/**
 * The cache lifetime a reply's `cache_creation` breakdown shows: 60 when it
 * wrote one-hour entries, 5 when it wrote five-minute ones, null when it
 * shows neither.
 */
export function lifetimeFromBreakdown(breakdown: unknown): 5 | 60 | null {
  if (typeof breakdown !== 'object' || breakdown === null) return null
  const b = breakdown as Record<string, unknown>
  const long = Number(b.ephemeral_1h_input_tokens ?? 0)
  const short = Number(b.ephemeral_5m_input_tokens ?? 0)
  if (long > 0) return 60
  if (short > 0) return 5
  return null
}

/**
 * Reads the lifetime from a session transcript (JSON lines): the newest
 * main-thread assistant reply whose breakdown shows one. Lines that do not
 * parse are skipped. A reply that wrote nothing to the cache (all of it read)
 * says nothing, so the scan goes on to the one before it, up to 50 replies.
 */
export function lifetimeFromTranscript(text: string): 5 | 60 | null {
  const lines = text.split('\n')
  let looked = 0
  for (let i = lines.length - 1; i >= 0 && looked < 50; i--) {
    const line = lines[i]
    if (line === undefined || !line.includes('ephemeral_')) continue
    let row: unknown
    try {
      row = JSON.parse(line)
    } catch {
      continue
    }
    if (typeof row !== 'object' || row === null) continue
    const r = row as Record<string, unknown>
    if (r.type !== 'assistant' || r.isSidechain === true) continue
    looked += 1
    const message = r.message as Record<string, unknown> | undefined
    const usage = message?.usage as Record<string, unknown> | undefined
    const found = lifetimeFromBreakdown(usage?.cache_creation)
    if (found !== null) return found
  }
  return null
}

/** The language a dhv-kit.json text names; Hebrew unless it says "en". Throws on bad JSON. */
export function langFromSettings(text: string): Lang {
  const parsed: unknown = JSON.parse(text)
  if (typeof parsed !== 'object' || parsed === null) return 'he'
  return (parsed as Record<string, unknown>).language === 'en' ? 'en' : 'he'
}

/** Milliseconds of warmth left (negative once cold). */
export function remainingMs(now: number, replyAt: number, ttlMin: number | null): number {
  const ttl = ttlMin ?? DEFAULT_TTL_MIN
  return replyAt + ttl * MINUTE - now
}

/** The clock's words and tone: "warm 42:10" while warm, "cold 12 min" after. */
export function clockText(
  lang: Lang,
  now: number,
  replyAt: number,
  ttlMin: number | null,
): { text: string; tone: Tone } {
  const w = WORDS[lang]
  const ttl = ttlMin ?? DEFAULT_TTL_MIN
  const left = remainingMs(now, replyAt, ttl)
  if (left > 0) {
    const secs = Math.ceil(left / 1000)
    const mm = Math.floor(secs / 60)
    const ss = String(secs % 60).padStart(2, '0')
    // the last fifth of the lifetime gets the warning tone
    const tone: Tone = left <= (ttl * MINUTE) / 5 ? 'warning' : 'calm'
    return { text: `${w.warm} ${mm}:${ss}`, tone }
  }
  const mins = Math.max(1, Math.ceil(-left / MINUTE))
  return { text: `${w.cold} ${mins} ${w.min}`, tone: 'cold' }
}

/** "chat 31%". */
export function chatText(lang: Lang, percent: number): string {
  const p = Math.min(100, Math.max(0, Math.round(percent)))
  return `${WORDS[lang].chat} ${p}%`
}

/** Why keep-warm should switch itself off now, or null to keep going. */
export function warmStopReason(warm: Warm, now: number, left: number): string | null {
  if (!warm.isOn) return null
  if (warm.refreshes >= MAX_REFRESHES) return 'refreshes'
  if (warm.failures >= MAX_FAILURES) return 'failures'
  if (now - warm.startedAt >= MAX_ON_MS) return 'time'
  if (left <= 0) return 'cold'
  return null
}

/** Whether a refresh is due: inside the lead window and not tried too recently. */
export function isRefreshDue(warm: Warm, now: number, left: number): boolean {
  return (
    warm.isOn &&
    left > 0 &&
    left <= REFRESH_LEAD_MS &&
    now - warm.lastTryAt >= RETRY_GAP_MS
  )
}
