import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { categorical } from '../theme/tokens';
import ChartTooltip from './ChartTooltip';

export interface Series {
  key: string;
  label: string;
}

interface LineTrendChartProps {
  data: Record<string, string | number>[];
  xKey: string;
  series: Series[]; // fixed categorical slot order — pass in the order series should map to colors
  height?: number;
}

/**
 * Time-series line chart. Mark spec: 2px line, round join/cap, ≥8px end
 * markers with a surface ring (dot stroke = chart surface). Legend always
 * present for 2+ series per dataviz-skill rule; a single series gets no
 * legend box (identity is already in the card title).
 */
export default function LineTrendChart({ data, xKey, series, height = 280 }: LineTrendChartProps) {
  const colors = categorical.light; // swap to categorical.dark under a dark theme toggle

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
        <CartesianGrid stroke="var(--border-hairline)" vertical={false} />
        <XAxis
          dataKey={xKey}
          stroke="var(--text-muted)"
          tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
          tickLine={false}
          axisLine={{ stroke: 'var(--border-hairline)' }}
        />
        <YAxis
          stroke="var(--text-muted)"
          tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
          tickLine={false}
          axisLine={false}
          width={48}
        />
        <Tooltip content={<ChartTooltip />} cursor={{ stroke: 'var(--border-hairline)' }} />
        {series.length > 1 && (
          <Legend
            verticalAlign="top"
            align="right"
            iconType="circle"
            wrapperStyle={{ fontSize: 13, color: 'var(--text-secondary)' }}
          />
        )}
        {series.map((s, i) => (
          <Line
            key={s.key}
            type="monotone"
            dataKey={s.key}
            name={s.label}
            stroke={colors[i % colors.length]}
            strokeWidth={2}
            dot={{ r: 4, fill: colors[i % colors.length], stroke: 'var(--surface-card)', strokeWidth: 2 }}
            activeDot={{ r: 5, stroke: 'var(--surface-card)', strokeWidth: 2 }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
