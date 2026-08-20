/**
 * Design tokens — Sber-style visual identity.
 *
 * Source: docs/DESIGN_SYSTEM.md at the repo root. This file is the single
 * source of truth consumed by theme.ts (MUI-less CSS-vars theme) and by the
 * chart components in src/charts/*. Do not hardcode hex values anywhere else
 * in the app — import from here.
 */

export const brand = {
  green: '#21A038',
  greenDark: '#168029',
  blue: '#0098F8',
  yellow: '#F1E813',
  black: '#000000',
  white: '#FFFFFF',
} as const;

export const surface = {
  light: {
    page: '#F7F8F7',
    card: '#FFFFFF',
    cardHover: '#F2F6F3',
    border: 'rgba(11,11,11,0.08)',
    textPrimary: '#0B0B0B',
    textSecondary: '#54564F',
    textMuted: '#8B8D86',
    chartSurface: '#fcfcfb',
  },
  dark: {
    page: '#0D0F0D',
    card: '#161816',
    cardHover: '#1E211E',
    border: 'rgba(255,255,255,0.10)',
    textPrimary: '#FFFFFF',
    textSecondary: '#C3C2B7',
    textMuted: '#8B8D86',
    chartSurface: '#1a1a19',
  },
} as const;

/**
 * Categorical chart palette. Fixed slot order — validated with
 * `dataviz` skill's validate_palette.js (see docs/DESIGN_SYSTEM.md §4).
 * NEVER reorder or cycle extra hues past slot 8; fold overflow series into
 * "Other" or facet instead.
 */
export const categorical = {
  light: [
    '#2a78d6', // 1 blue
    '#eb6834', // 2 orange
    '#1baf7a', // 3 aqua
    '#eda100', // 4 yellow
    '#e87ba4', // 5 magenta
    '#21A038', // 6 Sber green (brand)
    '#4a3aa7', // 7 violet
    '#e34948', // 8 red
  ],
  dark: [
    '#3987e5',
    '#d95926',
    '#199e70',
    '#c98500',
    '#d55181',
    '#21A038',
    '#9085e9',
    '#e66767',
  ],
} as const;

/** Slots whose contrast against the chart surface is sub-3:1 — relief rule:
 * these series MUST ship visible direct labels / legend, never rely on fill alone. */
export const categoricalReliefSlots = [2, 3, 4] as const; // aqua, yellow, magenta (0-indexed)

/** Sequential (magnitude) ramp anchored on the brand green at step 550. */
export const sequentialGreen = {
  100: '#dff6e3',
  200: '#bfeec7',
  300: '#99e6a7',
  400: '#65dc7b',
  500: '#2dd24b',
  550: '#21A038', // brand anchor
  600: '#18812c',
  700: '#0f5c1d',
} as const;

/** Diverging pair for polarity encodings (e.g. plan vs. actual variance). */
export const diverging = {
  negative: '#e34948', // red
  positive: '#2a78d6', // blue
  midpoint: { light: '#f0efec', dark: '#383835' },
} as const;

/** Status palette — fixed, never themed, never reused as a categorical series. */
export const status = {
  good: '#0ca30c',
  warning: '#fab219',
  serious: '#ec835a',
  critical: '#d03b3b',
} as const;

export const radius = {
  card: 20,
  button: 12,
  chip: 999,
  input: 10,
} as const;

export const shadow = {
  card: '0 2px 8px rgba(11,11,11,0.06)',
  cardHover: '0 6px 20px rgba(33,160,56,0.12)',
  popover: '0 12px 32px rgba(11,11,11,0.14)',
} as const;

export const font = {
  family: '"Golos Text", system-ui, -apple-system, "Segoe UI", sans-serif',
  weight: { regular: 400, medium: 500, semibold: 600, bold: 700 },
} as const;

export const type = {
  h1: { size: 32, lineHeight: 40, weight: 700 },
  h2: { size: 24, lineHeight: 32, weight: 700 },
  h3: { size: 18, lineHeight: 24, weight: 600 },
  body: { size: 15, lineHeight: 22, weight: 400 },
  caption: { size: 13, lineHeight: 18, weight: 500 },
  kpiValue: { size: 40, lineHeight: 44, weight: 700 },
} as const;

export type ThemeMode = 'light' | 'dark';
