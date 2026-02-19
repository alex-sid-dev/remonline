<template>
  <div>
    <!-- Create order form -->
    <div
      v-if="orderForm.open && !orderForm.editMode"
      class="login-card mt-16"
    >
      <div class="field">
        <div class="field-label">
          Новый заказ
        </div>
      </div>
      <div class="field">
        <label class="field-label" for="order-client">Клиент</label>
        <div
          v-if="selectedClient"
          class="field-row gap-8"
        >
          <div class="order-info-value">
            {{ selectedClient.full_name }} · {{ selectedClient.phone || '—' }}
          </div>
          <button
            class="btn btn-ghost"
            type="button"
            @click="clearSelectedClient"
          >
            Изменить
          </button>
        </div>
        <template v-else>
          <div class="field-row">
            <input
              v-model="orderClientSearch"
              class="field-input"
              type="text"
              placeholder="Поиск по ФИО или телефону (от 3 символов)"
              @input="handleOrderClientSearchInput"
              @focus="handleOrderClientSearchInput"
            >
            <button
              class="btn btn-ghost"
              type="button"
              @click="$emit('create-client-for-order')"
            >
              + Новый
            </button>
          </div>
          <div
            v-if="orderClientSuggestionsOpen && orderClientSearch.length >= 3"
            class="autocomplete-list"
          >
            <button
              v-for="c in clientsForOrder"
              :key="c.uuid"
              type="button"
              class="autocomplete-item"
              @click="selectOrderClient(c)"
            >
              <div class="autocomplete-item-main">
                {{ c.full_name }}
              </div>
              <div class="autocomplete-item-sub">
                {{ c.phone || '—' }}
              </div>
            </button>
            <div
              v-if="!clientsForOrder.length"
              class="autocomplete-empty"
            >
              Ничего не найдено
            </div>
          </div>
          <div class="hint">
            Клиент подставится автоматически. Если клиента нет в списке — создайте его через «+ Новый».
          </div>
        </template>
      </div>
      <div class="field">
        <label class="field-label" for="order-device">Устройство</label>
        <div class="field-row gap-8">
          <div v-if="pendingOrderDevice">
            <div class="order-info-value">
              {{ pendingOrderDevice.brand || 'Устройство' }} {{ pendingOrderDevice.model || '' }}
              <span v-if="pendingOrderDevice.serial_number">
                · SN: {{ pendingOrderDevice.serial_number }}
              </span>
            </div>
          </div>
          <button
            class="btn btn-ghost"
            type="button"
            :disabled="!orderForm.data.client_uuid"
            @click="$emit('create-device-for-order')"
          >
            {{ pendingOrderDevice ? 'Изменить' : '+ Новое' }}
          </button>
        </div>
        <div class="hint">
          Для нового заказа всегда создаётся новое устройство. Нажмите «+ Новое», чтобы заполнить данные устройства для выбранного клиента.
        </div>
      </div>
      <div
        v-if="canManageEmployees(props.userRole)"
        class="field"
      >
        <label class="field-label" for="order-engineer">Инженер</label>
        <select
          id="order-engineer"
          v-model="orderForm.data.assigned_employee_uuid"
          class="field-input"
        >
          <option value="">Не назначен</option>
          <option
            v-for="e in masters"
            :key="e.uuid"
            :value="e.uuid"
          >
            {{ e.full_name }}
          </option>
        </select>
      </div>
      <div
        v-if="canManageEmployees(props.userRole)"
        class="field"
      >
        <label class="field-label" for="order-manager">Менеджер</label>
        <select
          id="order-manager"
          v-model="orderForm.data.manager_uuid"
          class="field-input"
        >
          <option value="">Текущий менеджер (по умолчанию)</option>
          <option
            v-for="e in employees.filter((e) => ['manager', 'admin', 'supervisor'].includes(e.position))"
            :key="e.uuid"
            :value="e.uuid"
          >
            {{ e.full_name }}
          </option>
        </select>
      </div>
      <div
        v-else
        class="field"
      >
        <label class="field-label">Менеджер</label>
        <div class="order-info-value">
          {{ currentEmployeeName || 'Текущий пользователь' }}
        </div>
      </div>
      <div class="field">
        <label class="field-label" for="order-status">Статус</label>
        <select
          id="order-status"
          v-model="orderForm.data.status"
          class="field-input"
        >
          <option
            v-for="s in availableStatuses"
            :key="s.value"
            :value="s.value"
          >
            {{ s.label }}
          </option>
        </select>
      </div>
      <div class="field">
        <label class="field-label" for="order-problem">Проблема</label>
        <input
          id="order-problem"
          v-model="orderForm.data.problem_description"
          class="field-input"
          type="text"
        >
      </div>
      <div class="field">
        <label class="field-label" for="order-comment">Комментарий</label>
        <input
          id="order-comment"
          v-model="orderForm.data.comment"
          class="field-input"
          type="text"
        >
      </div>
      <div class="field">
        <button
          class="btn btn-primary"
          type="button"
          :disabled="!orderFormValid"
          @click="$emit('submit-order-form')"
        >
          Сохранить
        </button>
      </div>
    </div>

    <!-- Orders list + edit form -->
    <div v-else>
      <div class="table-header">
        <div class="table-meta">
          Заказы: выбор клиента и устройства из существующих сущностей, изменение статуса и цены.
          <div class="table-status-filters">
            <button
              v-for="s in ORDER_STATUS_OPTIONS"
              :key="s.value"
              class="btn btn-ghost table-status-filter-pill"
              :class="[
                tableStatusFilterClass(s.value),
                { 'table-status-filter-pill--active': orderStatusFilter.includes(s.value) },
              ]"
              type="button"
              @click.stop="toggleOrderStatusFilter(s.value)"
            >
              {{ s.label }}
            </button>
            <button
              v-if="orderStatusFilter.length"
              class="btn btn-ghost table-status-filter-clear"
              type="button"
              @click.stop="clearOrderStatusFilter"
            >
              Сбросить
            </button>
          </div>
        </div>
        <button
          v-if="canCreateOrders(props.userRole)"
          class="btn btn-primary"
          type="button"
          @click="$emit('start-create-order')"
        >
          Новый заказ
        </button>
      </div>
      <table v-if="orders.length">
        <thead>
          <tr>
            <th>№</th>
            <th>Клиент</th>
            <th>Устройство</th>
            <th>Менеджер</th>
            <th>Инженер</th>
            <th>Статус</th>
            <th>Цена</th>
            <th>Создано</th>
            <th>Обновлено</th>
            <th />
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="order in filteredOrders"
            :key="order.uuid"
            @click="$emit('open-details', order)"
          >
            <td>{{ order.id }}</td>
            <td>{{ order.client_name }}</td>
            <td>{{ order.device_label }}</td>
            <td>{{ order.creator_name }}</td>
            <td>{{ order.assigned_employee_name }}</td>
            <td>
              <span
                class="badge badge--status"
                :class="orderStatusClass(order.status)"
              >
                {{ orderStatusLabel(order.status) }}
              </span>
            </td>
            <td>{{ order.price ?? '—' }}</td>
            <td>{{ formatDate(order.created_at) }}</td>
            <td>{{ formatDate(order.updated_at) }}</td>
            <td />
          </tr>
        </tbody>
      </table>
      <div v-else class="empty-state">
        Заказов пока нет.
      </div>

      <div
        v-if="orderForm.open && orderForm.editMode"
        class="login-card mt-16"
      >
        <div class="field">
          <div class="field-label">
            {{ orderForm.editMode ? 'Редактирование заказа' : 'Новый заказ' }}
          </div>
        </div>
        <div
          v-if="canManageEmployees(props.userRole)"
          class="field"
        >
          <label class="field-label" for="order-engineer">Инженер</label>
          <select
            id="order-engineer"
            v-model="orderForm.data.assigned_employee_uuid"
            class="field-input"
          >
            <option value="">Не назначен</option>
            <option
              v-for="e in masters"
              :key="e.uuid"
              :value="e.uuid"
            >
              {{ e.full_name }}
            </option>
          </select>
        </div>
        <div class="field">
          <label class="field-label" for="order-status">Статус</label>
          <select
            id="order-status"
            v-model="orderForm.data.status"
            class="field-input"
          >
            <option
              v-for="s in availableStatuses"
              :key="s.value"
              :value="s.value"
            >
              {{ s.label }}
            </option>
          </select>
        </div>
        <div class="field">
          <label class="field-label" for="order-price">Цена</label>
          <input
            id="order-price"
            v-model.number="orderForm.data.price"
            class="field-input"
            type="number"
            @keydown="blockNonNumeric"
            step="0.01"
          >
        </div>
        <div class="field">
          <label class="field-label" for="order-problem">Проблема</label>
          <input
            id="order-problem"
            v-model="orderForm.data.problem_description"
            class="field-input"
            type="text"
          >
        </div>
        <div class="field">
          <label class="field-label" for="order-comment">Комментарий</label>
          <input
            id="order-comment"
            v-model="orderForm.data.comment"
            class="field-input"
            type="text"
          >
        </div>
        <div class="field">
          <button
            class="btn btn-primary"
            type="button"
            :disabled="!orderFormValid"
            @click="$emit('submit-order-form')"
          >
            Сохранить
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import {
  ORDER_STATUS_OPTIONS,
  orderStatusLabel,
  orderStatusClass,
  tableStatusFilterClass,
  formatDate,
} from '../utils/orderHelpers';
import { blockNonNumeric } from '../utils/inputHelpers';
import { debounce } from '../utils/debounce';
import { canManageEmployees, canCreateOrders } from '../constants/roles';

const props = defineProps({
  orders: { type: Array, required: true },
  employees: { type: Array, required: true },
  clients: { type: Array, required: true },
  userRole: { type: String, required: true },
  currentEmployeeName: { type: String, default: '' },
  orderForm: { type: Object, required: true },
  pendingOrderDevice: { type: Object, default: null },
});

defineEmits([
  'open-details',
  'submit-order-form',
  'start-create-order',
  'create-client-for-order',
  'create-device-for-order',
]);

const orderStatusFilter = ref([]);
const orderClientSearch = ref('');
const orderClientSuggestionsOpen = ref(false);

const filteredOrders = computed(() => {
  if (!orderStatusFilter.value.length) return props.orders;
  return props.orders.filter((o) => orderStatusFilter.value.includes(o.status));
});

const availableStatuses = computed(() => {
  if (props.userRole === 'supervisor') return ORDER_STATUS_OPTIONS;
  return ORDER_STATUS_OPTIONS.filter((s) => s.value !== 'closed');
});

const masters = computed(() => {
  return props.employees.filter((e) => e.position === 'master');
});

const selectedClient = computed(() => {
  const uuid = props.orderForm.data.client_uuid;
  if (!uuid) return null;
  return props.clients.find((c) => c.uuid === uuid) || null;
});

const clientsForOrder = computed(() => {
  const q = orderClientSearch.value.trim().toLowerCase();
  if (q.length < 3) return props.clients;
  return props.clients.filter((c) => {
    const name = (c.full_name || '').toLowerCase();
    const phone = (c.phone || '').toLowerCase();
    return name.includes(q) || phone.includes(q);
  });
});

const orderFormValid = computed(() => {
  if (!props.orderForm.open) return false;
  const data = props.orderForm.data;
  if (props.orderForm.editMode) return !!data.status;
  return !!data.client_uuid && (!!data.device_uuid || !!props.pendingOrderDevice);
});

const handleOrderClientSearchInput = debounce(() => {
  const q = orderClientSearch.value.trim();
  orderClientSuggestionsOpen.value = q.length >= 3;
  props.orderForm.data.client_uuid = '';
}, 300);

function selectOrderClient(client) {
  props.orderForm.data.client_uuid = client.uuid;
  orderClientSearch.value = '';
  orderClientSuggestionsOpen.value = false;
}

function clearSelectedClient() {
  props.orderForm.data.client_uuid = '';
  orderClientSearch.value = '';
  orderClientSuggestionsOpen.value = false;
}

function toggleOrderStatusFilter(value) {
  const idx = orderStatusFilter.value.indexOf(value);
  if (idx === -1) {
    orderStatusFilter.value = [...orderStatusFilter.value, value];
  } else {
    orderStatusFilter.value = orderStatusFilter.value.filter((v) => v !== value);
  }
}

function clearOrderStatusFilter() {
  orderStatusFilter.value = [];
}
</script>
