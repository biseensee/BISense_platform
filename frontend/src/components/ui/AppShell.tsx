import { type ReactNode } from 'react';
import { brand } from '../../theme/tokens';

/**
 * Top-level page chrome — Sber-style: dark logo mark on a clean white top
 * bar, a thin brand-gradient accent line, generous page padding. No sidebar
 * in this skeleton (single dashboard route); add one here when the page
 * count grows past a top-nav's comfortable width.
 */
export default function AppShell({ children }: { children: ReactNode }) {
  return (
    <div style={{ minHeight: '100%', display: 'flex', flexDirection: 'column' }}>
      <header
        style={{
          background: 'var(--surface-card)',
          borderBottom: '1px solid var(--border-hairline)',
        }}
      >
        <div
          style={{
            height: 3,
            background: `linear-gradient(90deg, ${brand.blue}, ${brand.green}, ${brand.yellow})`,
          }}
        />
        <div
          style={{
            maxWidth: 1280,
            margin: '0 auto',
            padding: '16px 24px',
            display: 'flex',
            alignItems: 'center',
            gap: 12,
          }}
        >
          <div
            aria-hidden
            style={{
              width: 32,
              height: 32,
              borderRadius: 10,
              background: brand.green,
              display: 'grid',
              placeItems: 'center',
              color: brand.white,
              fontWeight: 700,
              fontSize: 16,
            }}
          >
            Б
          </div>
          <span style={{ fontWeight: 700, fontSize: 18, color: 'var(--text-primary)' }}>
            BI Platform
          </span>
        </div>
      </header>
      <main style={{ flex: 1, background: 'var(--surface-page)' }}>
        <div style={{ maxWidth: 1280, margin: '0 auto', padding: '24px' }}>{children}</div>
      </main>
    </div>
  );
}
