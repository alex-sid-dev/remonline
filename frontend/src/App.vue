<template>
  <div class="shell">
    <header class="shell-header">
      <div class="brand">
        <div class="brand-mark" />
        <div>
          <div class="brand-title">RemOnline</div>
          <div class="brand-subtitle">панель управления сервисом</div>
        </div>
      </div>
      <div class="user-controls">
        <template v-if="isAuthenticated">
          <span>{{ lastLoginEmail || 'Пользователь' }}</span>
          <button class="btn btn-ghost" type="button" @click="onLogout">Выйти</button>
        </template>
        <template v-else>
          <button class="btn btn-primary" type="button" @click="openLoginModal">Войти</button>
        </template>
      </div>
    </header>

    <section class="shell-body">
      <aside class="side-panel">
        <h2 class="side-title">Разделы</h2>
        <p class="side-description">Выберите, с чем работать сейчас.</p>
        <div class="divider" />
        <nav class="side-nav">
          <button
            class="btn side-nav-item"
            :class="{ 'side-nav-item--active': activeTab === 'orders' }"
            type="button"
            @click="() => changeTab('orders')"
          >Заказы</button>
          <button
            v-if="canManageEmployees(userRole)"
            class="btn side-nav-item"
            :class="{ 'side-nav-item--active': activeTab === 'employees' }"
            type="button"
            @click="() => changeTab('employees')"
          >Сотрудники</button>
          <button
            class="btn side-nav-item"
            :class="{ 'side-nav-item--active': activeTab === 'parts' }"
            type="button"
            @click="() => changeTab('parts')"
          >Запчасти</button>
          <button
            class="btn side-nav-item"
            :class="{ 'side-nav-item--active': activeTab === 'statistics' }"
            type="button"
            @click="() => changeTab('statistics')"
          >Статистика</button>
        </nav>
      </aside>

      <main class="main-panel">
        <section class="table-shell">
          <header
            v-if="!(activeTab === 'orders' && orderDetails.data) && !(activeTab === 'employees' && editingEmployee) && activeTab !== 'statistics'"
            class="table-header"
          >
            <div class="table-title">
              <span v-if="activeTab === 'orders'">Заказы</span>
              <span v-else-if="activeTab === 'employees'">Сотрудники</span>
              <span v-else-if="activeTab === 'parts'">Запчасти</span>
            </div>
            <div class="table-meta">
              <span v-if="!isAuthenticated">Чтобы работать с API, авторизуйтесь.</span>
              <span v-else-if="isLoading">Загрузка данных…</span>
              <span v-else-if="loadError">Ошибка: {{ loadError }}</span>
              <span v-else>{{ currentCount }} записей</span>
            </div>
          </header>
          <header
            v-else-if="activeTab === 'orders' && orderDetails.data"
            class="order-detail-header"
          >
            <button class="btn btn-ghost" type="button" @click="closeOrderDetails">← Назад</button>
            <button class="btn btn-ghost" type="button" @click="$refs.orderDetailRef?.printAct()">🖨 Печать акта</button>
            <h1 class="order-detail-title">Заказ {{ orderDetails.data.id }}</h1>
            <button
              v-if="canManageEmployees(userRole)"
              class="btn btn-primary btn-danger"
              type="button"
              @click="removeCurrentOrder"
            >Удалить заказ</button>
          </header>
          <header
            v-else-if="activeTab === 'employees' && editingEmployee"
            class="order-detail-header"
          >
            <button class="btn btn-ghost" type="button" @click="closeEmployeeForm">← Назад</button>
            <h1 class="order-detail-title">
              {{ editingEmployee.uuid ? editingEmployee.full_name : 'Новый сотрудник' }}
            </h1>
          </header>

          <div class="table-wrapper">
            <div v-if="!isAuthenticated" class="empty-state">Войдите, чтобы получить доступ к REST API.</div>
            <div v-else-if="isLoading" class="empty-state">
              <span class="loader">
                <span class="loader-dot" />
                <span class="loader-dot" />
                <span class="loader-dot" />
              </span>
            </div>
            <div v-else-if="loadError" class="empty-state">{{ loadError }}</div>
            <template v-else>
              <OrderList
                v-if="activeTab === 'orders' && !orderDetails.data"
                :orders="orders"
                :employees="employees"
                :clients="clients"
                :user-role="userRole"
                :current-employee-name="currentEmployeeName"
                :order-form="orderForm"
                :pending-order-device="pendingOrderDevice"
                @open-details="openOrderDetails"
                @submit-order-form="submitOrderForm"
                @start-create-order="startCreateOrder"
                @create-client-for-order="clientModalOpen = true"
                @create-device-for-order="startCreateDeviceForOrder"
              />
              <OrderDetail
                v-else-if="activeTab === 'orders' && orderDetails.data"
                ref="orderDetailRef"
                :order-details="orderDetails"
                :employees="employees"
                :parts="parts"
                :user-role="userRole"
                @add-work="workModalOpen = true"
                @add-part="orderPartModalOpen = true"
                @error="handleChildError"
                @update:parts="handlePartsUpdate"
                @update:order="handleOrderUpdate"
              />
              <EmployeeForm
                v-else-if="activeTab === 'employees' && editingEmployee"
                :employee="editingEmployee.uuid ? editingEmployee : null"
                :user-role="userRole"
                :validation-rules="validationRules"
                @saved="handleEmployeeSaved"
                @deleted="handleEmployeeDeleted"
                @error="handleChildError"
              />
              <EmployeeList
                v-else-if="activeTab === 'employees'"
                :employees="employees"
                :user-role="userRole"
                @create-employee="openCreateEmployee"
                @edit-employee="openEditEmployee"
              />
              <PartsList
                v-else-if="activeTab === 'parts'"
                :parts="parts"
                :user-role="userRole"
                @create-part="openNewPartModal"
                @edit-part="openEditPartModal"
              />
              <StatisticsView
                v-else-if="activeTab === 'statistics' && statisticsData"
                :data="statisticsData"
              />
            </template>
          </div>
        </section>
      </main>
    </section>

    <LoginModal v-model="loginModalOpen" @login-success="loadData" />

    <ClientModal
      :open="clientModalOpen"
      @close="clientModalOpen = false"
      @submit="submitOrderClientModal"
    />

    <DeviceModal
      :open="deviceModalOpen"
      :device-types="deviceTypes"
      :initial-data="pendingOrderDevice"
      @close="deviceModalOpen = false"
      @submit="submitOrderDeviceModal"
    />

    <PartModal
      :open="partModalOpen"
      :edit-mode="!!editPartUuid"
      :initial-data="partModalData"
      @close="closePartModal"
      @submit="submitPartModal"
    />

    <WorkModal
      :open="workModalOpen"
      @close="workModalOpen = false"
      @submit="addWorkToOrder"
    />

    <OrderPartModal
      :open="orderPartModalOpen"
      :parts="parts"
      @close="orderPartModalOpen = false"
      @submit="addPartToOrder"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { useAuth } from './composables/useAuth';
import { extractErrorMessage } from './utils/errorHelpers';
import { canManageEmployees, canManageParts } from './constants/roles';
import LoginModal from './components/LoginModal.vue';
import OrderList from './components/OrderList.vue';
import OrderDetail from './components/OrderDetail.vue';
import EmployeeList from './components/EmployeeList.vue';
import EmployeeForm from './components/EmployeeForm.vue';
import PartsList from './components/PartsList.vue';
import StatisticsView from './components/StatisticsView.vue';
import ClientModal from './components/ClientModal.vue';
import DeviceModal from './components/DeviceModal.vue';
import PartModal from './components/PartModal.vue';
import WorkModal from './components/WorkModal.vue';
import OrderPartModal from './components/OrderPartModal.vue';
import {
  createClient,
  createDevice,
  createOrder,
  createOrderPart,
  createPart,
  createWork,
  deleteOrder,
  getClients,
  getDevices,
  getDeviceTypes,
  getEmployees,
  getOrderDetails,
  getOrders,
  getParts,
  getStatistics,
  getValidationRules,
  updateOrder,
  updatePart,
} from './services/api';

const {
  accessToken,
  lastLoginEmail,
  loginModalOpen,
  userRole,
  currentEmployeeName,
  isAuthenticated,
  handleLogout,
  openLoginModal,
  refreshUserRole,
  initAuth,
} = useAuth();

const activeTab = ref('orders');
const clients = ref([]);
const orders = ref([]);
const devices = ref([]);
const deviceTypes = ref([]);
const parts = ref([]);
const employees = ref([]);
const isLoading = ref(false);
const loadError = ref('');
const validationRules = ref(null);

const statisticsData = ref(null);
const editingEmployee = ref(null);
const orderDetails = ref({ loading: false, data: null });
const orderForm = ref({
  open: false,
  editMode: false,
  uuid: null,
  data: {
    client_uuid: '',
    device_uuid: '',
    manager_uuid: '',
    assigned_employee_uuid: '',
    status: 'new',
    price: null,
    problem_description: '',
    comment: '',
  },
});
const pendingOrderDevice = ref(null);

const clientModalOpen = ref(false);
const deviceModalOpen = ref(false);
const workModalOpen = ref(false);
const orderPartModalOpen = ref(false);
const partModalOpen = ref(false);
const editPartUuid = ref(null);
const partModalData = ref(null);

const currentCount = computed(() => {
  switch (activeTab.value) {
    case 'orders': return orders.value.length;
    case 'employees': return employees.value.length;
    case 'parts': return parts.value.length;
    default: return 0;
  }
});

async function loadData() {
  if (!isAuthenticated.value) return;
  isLoading.value = true;
  loadError.value = '';
  try {
    switch (activeTab.value) {
      case 'orders': {
        if (canManageEmployees(userRole.value)) {
          const [ordersRes, clientsRes, devicesData, employeesRes] = await Promise.all([
            getOrders(), getClients(), getDevices(), getEmployees(),
          ]);
          orders.value = ordersRes.items;
          clients.value = clientsRes.items;
          devices.value = devicesData;
          employees.value = employeesRes.items;
        } else {
          const [ordersRes, clientsRes, devicesData] = await Promise.all([
            getOrders(), getClients(), getDevices(),
          ]);
          orders.value = ordersRes.items;
          clients.value = clientsRes.items;
          devices.value = devicesData;
          employees.value = [];
        }
        break;
      }
      case 'employees':
        employees.value = (await getEmployees()).items;
        break;
      case 'parts':
        parts.value = (await getParts()).items;
        break;
      case 'statistics':
        statisticsData.value = await getStatistics();
        break;
      default:
        break;
    }
  } catch (e) {
    loadError.value = extractErrorMessage(e, 'Не удалось загрузить данные.');
  } finally {
    isLoading.value = false;
  }
}

async function onLogout() {
  await handleLogout();
  clients.value = [];
  orders.value = [];
  devices.value = [];
  deviceTypes.value = [];
  parts.value = [];
  employees.value = [];
}

function changeTab(tab) {
  sessionStorage.removeItem('openOrderUuid');
  if (tab === 'orders' && activeTab.value === 'orders' && orderDetails.value.data) {
    orderDetails.value = { loading: false, data: null };
    loadData();
    return;
  }
  if (tab === 'employees' && activeTab.value === 'employees' && editingEmployee.value) {
    editingEmployee.value = null;
    loadData();
    return;
  }
  orderDetails.value = { loading: false, data: null };
  editingEmployee.value = null;
  activeTab.value = tab;
  loadData();
}

function handleChildError(message) {
  loadError.value = message;
}

function openCreateEmployee() {
  editingEmployee.value = { uuid: null, full_name: '' };
}

function openEditEmployee(emp) {
  editingEmployee.value = { ...emp };
}

function closeEmployeeForm() {
  editingEmployee.value = null;
}

function handleEmployeeSaved(updated) {
  employees.value = updated;
  editingEmployee.value = null;
}

function handleEmployeeDeleted(updated) {
  employees.value = updated;
  editingEmployee.value = null;
}

function handlePartsUpdate(updated) {
  parts.value = updated;
}

function handleOrderUpdate(updated) {
  orderDetails.value.data = updated;
}

function closeAllModals() {
  loginModalOpen.value = false;
  clientModalOpen.value = false;
  deviceModalOpen.value = false;
  partModalOpen.value = false;
  workModalOpen.value = false;
  orderPartModalOpen.value = false;
}

function handleKeydown(event) {
  if (event.key === 'Escape') {
    if (loginModalOpen.value || clientModalOpen.value || deviceModalOpen.value
      || partModalOpen.value || workModalOpen.value || orderPartModalOpen.value) {
      event.preventDefault();
      closeAllModals();
    }
  }
}

async function ensureOrderReferences() {
  try {
    if (!clients.value.length) {
      clients.value = (await getClients()).items;
    }
  } catch (e) {
    loadError.value = extractErrorMessage(e, 'Не удалось загрузить справочные данные.');
  }
}

async function startCreateOrder() {
  await ensureOrderReferences();
  orderForm.value.open = true;
  orderForm.value.editMode = false;
  orderForm.value.uuid = null;
  pendingOrderDevice.value = null;
  orderForm.value.data = {
    client_uuid: '',
    device_uuid: '',
    manager_uuid: '',
    assigned_employee_uuid: '',
    status: 'new',
    price: null,
    problem_description: '',
    comment: '',
  };
}

async function submitOrderForm() {
  try {
    if (orderForm.value.editMode && orderForm.value.uuid) {
      await updateOrder(orderForm.value.uuid, {
        status: orderForm.value.data.status,
        price: orderForm.value.data.price,
        problem_description: orderForm.value.data.problem_description,
        comment: orderForm.value.data.comment,
      });
    } else {
      let deviceUuid = orderForm.value.data.device_uuid;
      if (!deviceUuid && pendingOrderDevice.value) {
        const devicePayload = {
          client_uuid: orderForm.value.data.client_uuid,
          type_uuid: pendingOrderDevice.value.type_uuid,
          brand: pendingOrderDevice.value.brand,
          model: pendingOrderDevice.value.model,
          serial_number: pendingOrderDevice.value.serial_number,
          description: pendingOrderDevice.value.description,
        };
        const createdDevice = await createDevice(devicePayload);
        devices.value = await getDevices();
        deviceUuid = createdDevice?.uuid;
        orderForm.value.data.device_uuid = deviceUuid || '';
      }
      const payload = { ...orderForm.value.data, device_uuid: deviceUuid };
      if (!payload.assigned_employee_uuid) delete payload.assigned_employee_uuid;
      if (!payload.manager_uuid) delete payload.manager_uuid;
      if (userRole.value === 'manager') delete payload.manager_uuid;
      delete payload.comment;
      await createOrder(payload);
    }
    await loadData();
    pendingOrderDevice.value = null;
    orderForm.value.open = false;
  } catch (e) {
    loadError.value = extractErrorMessage(e, 'Ошибка сохранения заказа.');
  }
}

async function removeCurrentOrder() {
  if (!orderDetails.value.data) return;
  if (!window.confirm(`Удалить заказ #${orderDetails.value.data.id}? Это действие невозможно отменить.`)) return;
  try {
    await deleteOrder(orderDetails.value.data.uuid);
    closeOrderDetails();
    await loadData();
  } catch (e) {
    loadError.value = extractErrorMessage(e, 'Ошибка удаления заказа.');
  }
}

async function openOrderDetails(order) {
  const uuid = order.uuid || order;
  try {
    orderDetails.value.loading = true;
    activeTab.value = 'orders';
    sessionStorage.setItem('openOrderUuid', uuid);
    if (canManageEmployees(userRole.value)) {
      const [details, partsRes, employeesRes] = await Promise.all([
        getOrderDetails(uuid), getParts(), getEmployees(),
      ]);
      orderDetails.value.data = details;
      parts.value = partsRes.items;
      employees.value = employeesRes.items;
    } else {
      const [details, partsRes] = await Promise.all([
        getOrderDetails(uuid), getParts(),
      ]);
      orderDetails.value.data = details;
      parts.value = partsRes.items;
    }
  } catch (e) {
    loadError.value = extractErrorMessage(e, 'Не удалось загрузить детали заказа.');
    sessionStorage.removeItem('openOrderUuid');
  } finally {
    orderDetails.value.loading = false;
  }
}

function closeOrderDetails() {
  orderDetails.value.data = null;
  sessionStorage.removeItem('openOrderUuid');
}

async function submitOrderClientModal(formData) {
  try {
    const created = await createClient(formData);
    clients.value = (await getClients()).items;
    if (created?.uuid) {
      orderForm.value.data.client_uuid = created.uuid;
    }
    clientModalOpen.value = false;
  } catch (e) {
    loadError.value = extractErrorMessage(e, 'Ошибка создания клиента.');
  }
}

async function startCreateDeviceForOrder() {
  if (!orderForm.value.data.client_uuid) {
    loadError.value = 'Сначала выберите клиента для заказа.';
    return;
  }
  try {
    if (!deviceTypes.value.length) {
      deviceTypes.value = await getDeviceTypes();
    }
  } catch (e) {
    loadError.value = extractErrorMessage(e, 'Не удалось загрузить типы устройств.');
    return;
  }
  deviceModalOpen.value = true;
}

function submitOrderDeviceModal(formData) {
  pendingOrderDevice.value = { ...formData };
  deviceModalOpen.value = false;
}

function openNewPartModal() {
  editPartUuid.value = null;
  partModalData.value = null;
  partModalOpen.value = true;
}

function openEditPartModal(part) {
  if (!canManageParts(userRole.value)) return;
  editPartUuid.value = part.uuid;
  partModalData.value = { name: part.name, sku: part.sku, price: part.price, stock_qty: part.stock_qty };
  partModalOpen.value = true;
}

function closePartModal() {
  partModalOpen.value = false;
  editPartUuid.value = null;
  partModalData.value = null;
}

async function submitPartModal(formData) {
  try {
    if (editPartUuid.value) {
      await updatePart(editPartUuid.value, formData);
    } else {
      await createPart(formData);
    }
    parts.value = (await getParts()).items;
    closePartModal();
  } catch (e) {
    loadError.value = extractErrorMessage(e, 'Ошибка сохранения запчасти.');
  }
}

async function addWorkToOrder(formData) {
  if (!orderDetails.value.data || !formData.title) return;
  try {
    const payload = {
      order_uuid: orderDetails.value.data.uuid,
      title: formData.title,
      description: formData.description || undefined,
      price: formData.price || undefined,
      employee_uuid: orderDetails.value.data.assigned_employee?.uuid || undefined,
    };
    await createWork(payload);
    const updated = await getOrderDetails(orderDetails.value.data.uuid);
    orderDetails.value.data = updated;
    workModalOpen.value = false;
  } catch (e) {
    loadError.value = extractErrorMessage(e, 'Не удалось добавить работу.');
  }
}

async function addPartToOrder(formData) {
  if (!orderDetails.value.data || !formData.part_uuid || !formData.qty) return;
  try {
    const payload = {
      order_uuid: orderDetails.value.data.uuid,
      part_uuid: formData.part_uuid,
      qty: formData.qty,
      price: formData.price || undefined,
    };
    await createOrderPart(payload);
    const [updatedOrder, partsRes] = await Promise.all([
      getOrderDetails(orderDetails.value.data.uuid),
      getParts(),
    ]);
    orderDetails.value.data = updatedOrder;
    parts.value = partsRes.items;
    orderPartModalOpen.value = false;
  } catch (e) {
    loadError.value = extractErrorMessage(e, 'Не удалось добавить запчасть.');
  }
}

onMounted(async () => {
  initAuth();
  getValidationRules()
    .then((rules) => { validationRules.value = rules; })
    .catch(() => {});
  if (isAuthenticated.value) {
    await refreshUserRole();
    await loadData();
    const savedUuid = sessionStorage.getItem('openOrderUuid');
    if (savedUuid) {
      await openOrderDetails(savedUuid);
    }
  }
  window.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown);
});
</script>
