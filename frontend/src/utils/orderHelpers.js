export const ORDER_STATUS_OPTIONS = [
  { value: 'new', label: 'Новый' },
  { value: 'accepted', label: 'Принят в работу' },
  { value: 'diagnostics', label: 'На диагностике' },
  { value: 'on_approval', label: 'На согласовании' },
  { value: 'waiting_parts', label: 'Ждём запчасти' },
  { value: 'in_repair', label: 'В ремонте' },
  { value: 'paid', label: 'Оплачен' },
  { value: 'closed', label: 'Закрыт' },
  { value: 'rejected', label: 'Отказ' },
];

export function orderStatusLabel(value) {
  const found = ORDER_STATUS_OPTIONS.find((s) => s.value === value);
  return found ? found.label : (value || '—');
}

export function orderStatusClass(value) {
  switch (value) {
    case 'new':
    case 'accepted':
    case 'diagnostics':
      return 'badge--status-green';
    case 'on_approval':
    case 'waiting_parts':
    case 'in_repair':
      return 'badge--status-yellow';
    case 'paid':
      return 'badge--status-blue';
    case 'closed':
      return 'badge--status-red';
    case 'rejected':
      return 'badge--status-black';
    default:
      return 'badge--status-muted';
  }
}

export function tableStatusFilterClass(value) {
  switch (value) {
    case 'new':
    case 'accepted':
    case 'diagnostics':
      return 'table-status-filter-pill--green';
    case 'on_approval':
    case 'waiting_parts':
    case 'in_repair':
      return 'table-status-filter-pill--yellow';
    case 'paid':
      return 'table-status-filter-pill--blue';
    case 'closed':
      return 'table-status-filter-pill--red';
    case 'rejected':
      return 'table-status-filter-pill--black';
    default:
      return '';
  }
}

export function formatDate(value) {
  if (!value) return '—';
  try {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return String(value);
    return date.toLocaleString('ru-RU', {
      year: '2-digit',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return String(value);
  }
}

export function formatCommentDate(value) {
  if (!value) return '—';
  try {
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return String(value);
    return d.toLocaleString('ru-RU', { dateStyle: 'short', timeStyle: 'short' });
  } catch {
    return String(value);
  }
}
