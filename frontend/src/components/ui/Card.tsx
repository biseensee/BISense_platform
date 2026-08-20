import { type CSSProperties, type ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  title?: string;
  subtitle?: string;
  actions?: ReactNode;
  style?: CSSProperties;
  padded?: boolean;
}

/**
 * Base surface for all dashboard content — mirrors the large-radius,
 * soft-shadow card pattern from sberbank.ru/ru/s_m_business: generous
 * radius, hairline border, subtle brand-green glow on hover.
 */
export default function Card({ children, title, subtitle, actions, style, padded = true }: CardProps) {
  return (
    <section
      style={{
        background: 'var(--surface-card)',
        border: '1px solid var(--border-hairline)',
        borderRadius: 'var(--radius-card)',
        boxShadow: 'var(--shadow-card)',
        transition: 'box-shadow 160ms ease, transform 160ms ease',
        ...style,
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.boxShadow = 'var(--shadow-card-hover)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = 'var(--shadow-card)';
      }}
    >
      {(title || actions) && (
        <div
          style={{
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            padding: padded ? '20px 24px 0' : undefined,
          }}
        >
          <div>
            {title && (
              <h3 style={{ margin: 0, fontSize: 18, fontWeight: 600, color: 'var(--text-primary)' }}>
                {title}
              </h3>
            )}
            {subtitle && (
              <p style={{ margin: '4px 0 0', fontSize: 13, color: 'var(--text-secondary)' }}>
                {subtitle}
              </p>
            )}
          </div>
          {actions}
        </div>
      )}
      <div style={{ padding: padded ? 24 : 0 }}>{children}</div>
    </section>
  );
}
