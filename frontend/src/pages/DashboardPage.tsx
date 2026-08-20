import Card from '../components/ui/Card';
import KpiTile from '../components/ui/KpiTile';
import Badge from '../components/ui/Badge';
import Button from '../components/ui/Button';
import LineTrendChart from '../charts/LineTrendChart';
import BarComparisonChart from '../charts/BarComparisonChart';
import DonutBreakdownChart from '../charts/DonutBreakdownChart';

// Demo data shaped like what GET /dashboards/{id}/widgets/{id}/data returns
// (columns/rows), pre-shaped here for the chart components. Wire up
// @tanstack/react-query + `api.getWidgetData` per widget to replace this.
const revenueTrend = [
  { month: 'Янв', выручка: 4200, расходы: 3100 },
  { month: 'Фев', выручка: 4800, расходы: 3300 },
  { month: 'Мар', выручка: 5100, расходы: 3600 },
  { month: 'Апр', выручка: 4950, расходы: 3500 },
  { month: 'Май', выручка: 5600, расходы: 3800 },
  { month: 'Июн', выручка: 6200, расходы: 4100 },
];

const revenueByProduct = [
  { label: 'Эквайринг', value: 3200 },
  { label: 'РКО', value: 2450 },
  { label: 'Кредитование', value: 1980 },
  { label: 'Зарплатный проект', value: 1300 },
  { label: 'Депозиты', value: 890 },
];

const channelBreakdown = [
  { label: 'Мобильное приложение', value: 4400 },
  { label: 'Интернет-банк', value: 2600 },
  { label: 'Отделения', value: 1200 },
  { label: 'Партнёры', value: 700 },
];

export default function DashboardPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 32, fontWeight: 700, color: 'var(--text-primary)' }}>
            Обзор для малого бизнеса
          </h1>
          <p style={{ margin: '4px 0 0', color: 'var(--text-secondary)', fontSize: 15 }}>
            Ключевые показатели за текущий квартал
          </p>
        </div>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <Badge status="good" />
          <Button variant="secondary">Экспорт</Button>
          <Button variant="primary">+ Виджет</Button>
        </div>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: 16,
        }}
      >
        <KpiTile label="Выручка (мес.)" value="6,2 млн ₽" deltaPct={10.7} deltaLabel="к пред. месяцу" />
        <KpiTile label="Активные клиенты" value="18 430" deltaPct={3.2} deltaLabel="к пред. месяцу" />
        <KpiTile label="Средний чек" value="3 260 ₽" deltaPct={-1.4} deltaLabel="к пред. месяцу" />
        <KpiTile label="Отток клиентов" value="2,1%" deltaPct={-0.6} deltaLabel="к пред. месяцу" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16 }}>
        <Card title="Выручка и расходы" subtitle="Помесячная динамика, млн ₽">
          <LineTrendChart
            data={revenueTrend}
            xKey="month"
            series={[
              { key: 'выручка', label: 'Выручка' },
              { key: 'расходы', label: 'Расходы' },
            ]}
          />
        </Card>
        <Card title="Каналы привлечения" subtitle="Доля выручки">
          <DonutBreakdownChart data={channelBreakdown} height={280} />
        </Card>
      </div>

      <Card title="Выручка по продуктам" subtitle="Топ-5 продуктовых линий, тыс. ₽">
        <BarComparisonChart data={revenueByProduct} seriesName="Выручка" />
      </Card>
    </div>
  );
}
