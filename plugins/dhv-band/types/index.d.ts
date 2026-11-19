// The values dhv-band keeps in $.state for the session.

/** The last main-thread model reply: when it arrived, in $.clock.now() ms. */
export type Reply = { at: number }

/** The keep-warm switch and its counters. */
export type Warm = {
  isOn: boolean
  /** When it was switched on (ms); it switches off 2 hours later. */
  startedAt: number
  /** Successful refreshes since it was switched on (max 12). */
  refreshes: number
  /** Failed refreshes in a row (max 3). */
  failures: number
  /** When the last refresh was tried (ms), so retries are spaced out. */
  lastTryAt: number
}

export type Lang = 'he' | 'en'

declare module 'claude-code' {
  interface PluginState {
    'dhv-band': {
      reply: Shaped<Reply | null>
      /** Cache lifetime in minutes as learned from the reply usage; null = unknown (treated as 60). */
      ttl: number | null
      /** Context used, 0-100; null before the engine measured it. */
      percent: number | null
      /** The ticker's time (ms), written every second so the countdown redraws. */
      now: number
      /** The person's language; null when the settings file could not be read. */
      lang: Lang | null
      /** True after an error reading usage: the row stays empty. */
      isBroken: boolean
      isHidden: boolean
      /** True until the person finished a first /start stage: the band offers a Start button. */
      needsStart: boolean
      warm: Shaped<Warm>
    }
  }
}
