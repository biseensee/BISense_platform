import { type ButtonHTMLAttributes, type CSSProperties, type MouseEvent } from 'react';
import { brand } from '../../theme/tokens';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
}

const variantStyles: Record<NonNullable<ButtonProps['variant']>, CSSProperties> = {
  primary: { background: brand.green, color: brand.white, border: '1px solid transparent' },
  secondary: {
    background: 'var(--surface-card)',
    color: 'var(--text-primary)',
    border: '1px solid var(--border-hairline)',
  },
  ghost: { background: 'transparent', color: brand.green, border: '1px solid transparent' },
};

export default function Button({ variant = 'primary', style, children, ...rest }: ButtonProps) {
  return (
    <button
      {...rest}
      style={{
        fontFamily: 'inherit',
        fontWeight: 600,
        fontSize: 14,
        padding: '10px 18px',
        borderRadius: 'var(--radius-button)',
        cursor: 'pointer',
        transition: 'opacity 120ms ease, transform 120ms ease',
        ...variantStyles[variant],
        ...style,
      }}
      onMouseDown={(e: MouseEvent<HTMLButtonElement>) => (e.currentTarget.style.transform = 'scale(0.98)')}
      onMouseUp={(e: MouseEvent<HTMLButtonElement>) => (e.currentTarget.style.transform = 'scale(1)')}
    >
      {children}
    </button>
  );
}
