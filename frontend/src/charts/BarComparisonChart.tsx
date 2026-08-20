import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Cell,
} from 'recharts';
import { categorical } from '../theme/tokens';
import ChartTooltip from './ChartTooltip';

interface BarComparisonChartProps {
  data: { label: string; value: number }[];
  height?: number;
  seriesName?: string;
}

/**
 * Single-series categorical bar chart (e.g. revenue by product line). Mark
 * spec: bar capped at 24px thickness, 4px rounded top / square baseline,
 * 2px surface gap between neighbors (barCategoryGap). Single series -> no
 * legend box (dataviz-skill rule); each category is its own fixed slot so
 * hue still encodes identity when the widget is later faceted.
 */
export default function BarComparisonChart({ data, height = 280, seriesName = 'Значение' }: BarComparisonChartProps) {
  const colors = categorical.light;

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: 0 }} barCategoryGap="24%">
        <CartesianGrid stroke="var(--border-hairline)" vertical={false} />
        <XAxis
          dataKey="label"
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
        <Tooltip content={<ChartTooltip />} cursor={{ fill: 'var(--surface-card-hover)' }} />
        <Bar dataKey="value" name={seriesName} radius={[4, 4, 0, 0]} maxBarSize={24}>
          {data.map((_, i) => (
            <Cell key={i} fill={colors[i % colors.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
