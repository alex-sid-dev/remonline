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
      <!-- Блок данных клиента прямо в форме заказа -->
      <div class="field">
        <label class="field-label" for="order-client-phone">Телефон клиента *</label>
        <input
          id="order-client-phone"
          v-model="orderForm.newClient.phone"
          class="field-input"
          type="text"
          placeholder="+78008008000"
        >
        <div class="hint">
          Формат: +7 и 10 цифр, например +78008008000
        </div>

        <div
          v-if="phoneMatches.length"
          class="autocomplete-list mt-8"
        >
          <div class="autocomplete-empty">
            Найдены клиенты с таким телефоном:
          </div>
          <button
            v-for="c in phoneMatches"
            :key="c.uuid"
            type="button"
            class="autocomplete-item"
            @click="pickClientFromPhone(c)"
          >
            <div class="autocomplete-item-main">
              {{ c.full_name || 'Без имени' }}
            </div>
            <div class="autocomplete-item-sub">
              {{ c.phone || '—' }}
              <span v-if="c.address"> · {{ c.address }}</span>
            </div>
          </button>
        </div>
      </div>

      <div class="field">
        <label class="field-label" for="order-client-name">ФИО клиента *</label>
        <input
          id="order-client-name"
          v-model="orderForm.newClient.full_name"
          class="field-input"
          type="text"
          placeholder="ФИО клиента"
        >
      </div>

      <div class="field">
        <label class="field-label" for="order-client-address">Адрес</label>
        <input
          id="order-client-address"
          v-model="orderForm.newClient.address"
          class="field-input"
          type="text"
        >
      </div>

      <div class="field">
        <label class="field-label" for="order-client-email">Email</label>
        <input
          id="order-client-email"
          v-model="orderForm.newClient.email"
          class="field-input"
          type="email"
        >
      </div>

      <div class="field">
        <label class="field-label" for="order-client-telegram">Telegram</label>
        <input
          id="order-client-telegram"
          v-model="orderForm.newClient.telegram_nick"
          class="field-input"
          type="text"
        >
      </div>
      <div class="field">
        <label class="field-label" for="order-device-type">Тип устройства *</label>
        <select
          id="order-device-type"
          v-model="orderForm.newDevice.type_uuid"
          class="field-input"
        >
          <option disabled value="">Выберите тип</option>
          <option
            v-for="dt in deviceTypes"
            :key="dt.uuid"
            :value="dt.uuid"
          >
            {{ dt.name }}
          </option>
        </select>
      </div>

      <div class="field">
        <label class="field-label" for="order-device-brand">Бренд *</label>
        <select
          id="order-device-brand"
          v-model="orderForm.newDevice.brand_uuid"
          class="field-input"
        >
          <option disabled value="">Выберите бренд</option>
          <option
            v-for="b in brands"
            :key="b.uuid"
            :value="b.uuid"
          >
            {{ b.name }}
          </option>
        </select>
      </div>

      <div class="field">
        <label class="field-label" for="order-device-model">Модель *</label>
        <input
          id="order-device-model"
          v-model="orderForm.newDevice.model"
          class="field-input"
          type="text"
        >
      </div>

      <div class="field">
        <label class="field-label" for="order-device-serial">Серийный номер</label>
        <input
          id="order-device-serial"
          v-model="orderForm.newDevice.serial_number"
          class="field-input"
          type="text"
        >

        <div
          v-if="deviceMatches.length"
          class="autocomplete-list mt-8"
        >
          <div class="autocomplete-empty">
            Найдены устройства с таким серийным номером:
          </div>
          <button
            v-for="d in deviceMatches"
            :key="d.uuid"
            type="button"
            class="autocomplete-item"
            @click="pickDeviceFromSearch(d)"
          >
            <div class="autocomplete-item-main">
              {{ (d.brand && d.brand.name) || d.brand || 'Устройство' }} {{ d.model || '' }}
            </div>
            <div class="autocomplete-item-sub">
              SN: {{ d.serial_number || '—' }}
            </div>
          </button>
        </div>
      </div>

      <div class="field">
        <label class="field-label" for="order-device-description">Внешнее состояние</label>
        <input
          id="order-device-description"
          v-model="orderForm.newDevice.description"
          class="field-input"
          type="text"
        >
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
        <label class="field-label" for="order-problem">Неисправность</label>
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
      <div class="field field-row gap-8">
        <button
          class="btn btn-ghost"
          type="button"
          @click="$emit('cancel-order-form')"
        >
          ← Назад к списку
        </button>
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
      <div
        ref="filterBarRef"
        class="table-header"
      >
        <div class="table-meta table-filter-bar">
          <div class="filter-dropdown-wrap">
            <button
              type="button"
              class="btn btn-ghost filter-trigger"
              :class="{ 'filter-trigger--active': openFilter === 'status' || orderStatusFilter.length }"
              @click.stop="toggleFilterDropdown('status')"
            >
              Статусы
              <span v-if="orderStatusFilter.length" class="filter-count">{{ orderStatusFilter.length }}</span>
              <span class="filter-chevron">▾</span>
            </button>
            <div
              v-show="openFilter === 'status'"
              class="filter-panel"
              @click.stop
            >
              <button
                type="button"
                class="filter-panel-all"
                @click="toggleAllStatuses"
              >
                {{ orderStatusFilter.length === statusOptionsForFilter.length ? 'Снять все' : 'Выбрать все' }}
              </button>
              <label
                v-for="s in statusOptionsForFilter"
                :key="s.value"
                class="filter-panel-item"
              >
                <input
                  v-model="orderStatusFilter"
                  type="checkbox"
                  :value="s.value"
                >
                <span>{{ s.label }}</span>
              </label>
            </div>
          </div>
          <div class="filter-dropdown-wrap">
            <button
              type="button"
              class="btn btn-ghost filter-trigger"
              :class="{ 'filter-trigger--active': openFilter === 'manager' || managerFilter.length }"
              @click.stop="toggleFilterDropdown('manager')"
            >
              Менеджеры
              <span v-if="managerFilter.length" class="filter-count">{{ managerFilter.length }}</span>
              <span class="filter-chevron">▾</span>
            </button>
            <div
              v-show="openFilter === 'manager'"
              class="filter-panel"
              @click.stop
            >
              <button
                type="button"
                class="filter-panel-all"
                @click="toggleAllManagers"
              >
                {{ managerFilter.length === managerEmployees.length ? 'Снять все' : 'Выбрать все' }}
              </button>
              <label
                v-for="m in managerEmployees"
                :key="m.uuid"
                class="filter-panel-item"
              >
                <input
                  v-model="managerFilter"
                  type="checkbox"
                  :value="m.full_name"
                >
                <span>{{ m.full_name }}</span>
              </label>
            </div>
          </div>
          <div class="filter-dropdown-wrap">
            <button
              type="button"
              class="btn btn-ghost filter-trigger"
              :class="{ 'filter-trigger--active': openFilter === 'master' || masterFilter.length }"
              @click.stop="toggleFilterDropdown('master')"
            >
              Мастера
              <span v-if="masterFilter.length" class="filter-count">{{ masterFilter.length }}</span>
              <span class="filter-chevron">▾</span>
            </button>
            <div
              v-show="openFilter === 'master'"
              class="filter-panel"
              @click.stop
            >
              <button
                type="button"
                class="filter-panel-all"
                @click="toggleAllMasters"
              >
                {{ masterFilter.length === masters.length ? 'Снять все' : 'Выбрать все' }}
              </button>
              <label
                v-for="m in masters"
                :key="m.uuid"
                class="filter-panel-item"
              >
                <input
                  v-model="masterFilter"
                  type="checkbox"
                  :value="m.full_name"
                >
                <span>{{ m.full_name }}</span>
              </label>
            </div>
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
            <th>Тип</th>
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
            <td>{{ order.device_type_name || '—' }}</td>
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
          <label class="field-label" for="order-problem">Неисправность</label>
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
import { computed, onMounted, onUnmounted, ref } from 'vue';
import {
  ORDER_STATUS_OPTIONS,
  orderStatusLabel,
  orderStatusClass,
  formatDate,
} from '../utils/orderHelpers';
import { blockNonNumeric } from '../utils/inputHelpers';
import { canManageEmployees, canCreateOrders } from '../constants/roles';

const props = defineProps({
  orders: { type: Array, required: true },
  employees: { type: Array, required: true },
  clients: { type: Array, required: true },
  devices: { type: Array, required: true },
  deviceTypes: { type: Array, required: true },
  brands: { type: Array, default: () => [] },
  userRole: { type: String, required: true },
  currentEmployeeName: { type: String, default: '' },
  orderForm: { type: Object, required: true },
});

defineEmits([
  'open-details',
  'submit-order-form',
  'start-create-order',
  'cancel-order-form',
]);

const filterBarRef = ref(null);
const openFilter = ref(null);

const orderStatusFilter = ref([]);
const managerFilter = ref([]);
const masterFilter = ref([]);

const statusOptionsForFilter = computed(() => {
  if (props.userRole === 'supervisor') return ORDER_STATUS_OPTIONS;
  return ORDER_STATUS_OPTIONS.filter((s) => s.value !== 'closed');
});

const filteredOrders = computed(() => {
  return props.orders.filter((o) => {
    const statusOk =
      !orderStatusFilter.value.length || orderStatusFilter.value.includes(o.status);
    const managerOk =
      !managerFilter.value.length || managerFilter.value.includes(o.creator_name);
    const masterOk =
      !masterFilter.value.length || masterFilter.value.includes(o.assigned_employee_name);
    return statusOk && managerOk && masterOk;
  });
});

const availableStatuses = computed(() => {
  if (props.userRole === 'supervisor') return ORDER_STATUS_OPTIONS;
  return ORDER_STATUS_OPTIONS.filter((s) => s.value !== 'closed');
});

const masters = computed(() => props.employees.filter((e) => e.position === 'master'));

const managerEmployees = computed(() => {
  return props.employees.filter((e) =>
    ['manager', 'admin', 'supervisor'].includes(e.position),
  );
});

function toggleFilterDropdown(name) {
  openFilter.value = openFilter.value === name ? null : name;
}

function toggleAllStatuses() {
  if (orderStatusFilter.value.length === statusOptionsForFilter.value.length) {
    orderStatusFilter.value = [];
  } else {
    orderStatusFilter.value = statusOptionsForFilter.value.map((s) => s.value);
  }
}

function toggleAllManagers() {
  if (managerFilter.value.length === managerEmployees.value.length) {
    managerFilter.value = [];
  } else {
    managerFilter.value = managerEmployees.value.map((m) => m.full_name);
  }
}

function toggleAllMasters() {
  if (masterFilter.value.length === masters.value.length) {
    masterFilter.value = [];
  } else {
    masterFilter.value = masters.value.map((m) => m.full_name);
  }
}

function closeFilterOnClickOutside(e) {
  if (filterBarRef.value && !filterBarRef.value.contains(e.target)) {
    openFilter.value = null;
  }
}

onMounted(() => {
  document.addEventListener('click', closeFilterOnClickOutside);
});
onUnmounted(() => {
  document.removeEventListener('click', closeFilterOnClickOutside);
});

const phoneMatches = computed(() => {
  const raw = (props.orderForm.newClient?.phone || '').replace(/\D/g, '');
  if (raw.length < 5) return [];
  return props.clients.filter((c) => {
    const phone = (c.phone || '').replace(/\D/g, '');
    return phone.includes(raw);
  });
});

const deviceMatches = computed(() => {
  const q = (props.orderForm.newDevice?.serial_number || '').trim().toLowerCase();
  if (q.length < 3) return [];
  return props.devices.filter((d) => {
    const sn = (d.serial_number || '').toLowerCase();
    return sn.includes(q);
  });
});

const orderFormValid = computed(() => {
  if (!props.orderForm.open) return false;
  const data = props.orderForm.data;
  if (props.orderForm.editMode) return !!data.status;
  // Для нового заказа требуем телефон и ФИО клиента + обязательные поля устройства
  const nc = props.orderForm.newClient || {};
  const nd = props.orderForm.newDevice || {};
  const hasClient = !!nc.phone && !!nc.full_name;
  const hasDevice = !!nd.type_uuid && !!nd.brand_uuid && !!nd.model;
  return hasClient && hasDevice;
});

function pickClientFromPhone(client) {
  if (!props.orderForm.newClient) return;
  props.orderForm.newClient.uuid = client.uuid || null;
  props.orderForm.newClient.full_name = client.full_name || '';
  props.orderForm.newClient.phone = client.phone || '';
  props.orderForm.newClient.email = client.email || '';
  props.orderForm.newClient.telegram_nick = client.telegram_nick || '';
  props.orderForm.newClient.address = client.address || '';
}

function pickDeviceFromSearch(device) {
  if (!props.orderForm.newDevice) return;
  props.orderForm.newDevice.type_uuid = device.type_uuid || '';
  props.orderForm.newDevice.brand_uuid = device.brand_uuid || (device.brand && device.brand.uuid) || '';
  props.orderForm.newDevice.model = device.model || '';
  props.orderForm.newDevice.serial_number = device.serial_number || '';
  props.orderForm.newDevice.description = device.description || '';
}

</script>
