<template>
  <div class="statistics-page">
    <h2 class="form-title" style="margin-bottom: 16px;">Статистика (закрытые заказы)</h2>

    <div class="stats-cards">
      <div class="stats-card">
        <div class="stats-card-label">Закрытых заказов</div>
        <div class="stats-card-value">{{ data.total_orders }}</div>
      </div>
      <div class="stats-card">
        <div class="stats-card-label">Общий оборот</div>
        <div class="stats-card-value">{{ fmt(data.total_revenue) }}</div>
      </div>
      <div class="stats-card">
        <div class="stats-card-label">Расходы (запчасти)</div>
        <div class="stats-card-value">{{ fmt(data.total_expenses) }}</div>
      </div>
      <div class="stats-card stats-card--profit">
        <div class="stats-card-label">Чистая прибыль</div>
        <div class="stats-card-value">{{ fmt(data.net_profit) }}</div>
      </div>
    </div>

    <h3 class="form-title" style="margin: 24px 0 12px;">Сотрудники</h3>

    <div v-if="data.employees.length" class="order-detail-table-wrap">
      <table>
        <thead>
          <tr>
            <th>ФИО</th>
            <th>Роль</th>
            <th>Заказов</th>
            <th>Оборот</th>
            <th>Расходы</th>
            <th>Чистая прибыль</th>
            <th>Ставка</th>
            <th>% прибыли</th>
            <th>Бонус</th>
            <th>Итого ЗП</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="e in data.employees" :key="e.uuid">
            <td>{{ e.full_name }}</td>
            <td>{{ roleLabel(e.position) }}</td>
            <td>{{ e.orders_count }}</td>
            <td>{{ fmt(e.revenue) }}</td>
            <td>{{ fmt(e.expenses) }}</td>
            <td>{{ fmt(e.net_profit) }}</td>
            <td>{{ fmt(e.base_salary) }}</td>
            <td>{{ e.profit_percent }}%</td>
            <td>{{ fmt(e.bonus) }}</td>
            <td class="stats-salary-total">{{ fmt(e.total_salary) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else class="empty-state">
      Нет данных по сотрудникам.
    </div>
  </div>
</template>

<script setup>
defineProps({
  data: { type: Object, required: true },
});

const ROLE_LABELS = {
  supervisor: 'Супервайзер',
  admin: 'Админ',
  manager: 'Менеджер',
  master: 'Мастер',
};

function roleLabel(pos) {
  return ROLE_LABELS[pos] || pos;
}

function fmt(v) {
  if (v == null) return '—';
  return Number(v).toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
</script>

<style scoped>
.statistics-page {
  padding: 0;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.stats-card {
  background: var(--bg-panel, #1e293b);
  border: 1px solid var(--border, #334155);
  border-radius: 10px;
  padding: 16px;
}

.stats-card--profit {
  border-color: #22c55e;
}

.stats-card-label {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  opacity: 0.6;
  margin-bottom: 4px;
}

.stats-card-value {
  font-size: 1.4rem;
  font-weight: 700;
}

.stats-salary-total {
  font-weight: 700;
}
</style>
