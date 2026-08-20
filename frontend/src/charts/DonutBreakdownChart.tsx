import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';
import { categorical } from '../theme/tokens';
import ChartTooltip from './ChartTooltip';

interface DonutBreakdownChartProps {
  data: { label: string; value: number }[];
  height?: number;
}

/**
 * Composition breakdown (e.g. traffic by channel). Categorical slots 1-3
 * validate all-pairs (see docs/DESIGN_SYSTEM.md) so a donut with up to 3
 * segments never risks a CVD-ambiguous adjacent pair; beyond 3 segments,
 * fold the smallest into "Other" per the skill's overflow rule rather than
 * cycling extra hues.
 */
export default function DonutBreakdownChart({ data, height = 280 }: DonutBreakdownChartProps) {
  const colors = categorical.light;
  const MAX_SLICES = 8;
  const shown = data.length > MAX_SLICES ? foldOther(data, MAX_SLICES) : data;

  return (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Tooltip content={<ChartTooltip />} />
        <Legend
          verticalAlign="bottom"
          iconType="circle"
          wrapperStyle={{ fontSize: 13, color: 'var(--text-secondary)' }}
        />
        <Pie
          data={shown}
          dataKey="value"
          nameKey="label"
          innerRadius="55%"
          outerRadius="80%"
          paddingAngle={2}
          stroke="var(--surface-card)"
          strokeWidth={2}
        >
          {shown.map((_, i) => (
            <Cell key={i} fill={colors[i % colors.length]} />
          ))}
        </Pie>
      </PieChart>
    </ResponsiveContainer>
  );
}

function foldOther(data: { label: string; value: number }[], max: number) {
  const sorted = [...data].sort((a, b) => b.value - a.value);
  const head = sorted.slice(0, max - 1);
  const rest = sorted.slice(max - 1);
  const otherTotal = rest.reduce((sum, d) => sum + d.value, 0);
  return [...head, { label: 'Другое', value: otherTotal }];
}
