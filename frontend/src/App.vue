<template>
  <div class="shell">
    <header class="shell-header">
      <div class="brand">
        <div class="brand-mark" />
        <div class="brand-title">CRM</div>
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
            :class="{ 'side-nav-item--active': activeTab === 'brands' }"
            type="button"
            @click="() => changeTab('brands')"
          >Бренды</button>
          <button
            class="btn side-nav-item"
            :class="{ 'side-nav-item--active': activeTab === 'deviceTypes' }"
            type="button"
            @click="() => changeTab('deviceTypes')"
          >Типы устройств</button>
          <button
            class="btn side-nav-item"
            :class="{ 'side-nav-item--active': activeTab === 'statistics' }"
            type="button"
            @click="() => changeTab('statistics')"
          >Статистика</button>
          <button
            class="btn side-nav-item"
            :class="{ 'side-nav-item--active': activeTab === 'info' }"
            type="button"
            @click="() => changeTab('info')"
          >Справка</button>
        </nav>
      </aside>

      <main class="main-panel">
        <section class="table-shell">
          <header
            v-if="!(activeTab === 'orders' && orderDetails.data) && !(activeTab === 'employees' && editingEmployee) && activeTab !== 'statistics' && activeTab !== 'info'"
            class="table-header"
          >
            <div class="table-title">
              <span v-if="activeTab === 'orders'">Заказы</span>
              <span v-else-if="activeTab === 'employees'">Сотрудники</span>
              <span v-else-if="activeTab === 'parts'">Запчасти</span>
              <span v-else-if="activeTab === 'brands'">Бренды</span>
              <span v-else-if="activeTab === 'deviceTypes'">Типы устройств</span>
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
            <button class="btn btn-ghost" type="button" @click="$refs.orderDetailRef?.printReceipt()">🖨 Квитанция о сдаче</button>
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
            <button
              v-if="userRole === ROLES.SUPERVISOR && editingEmployee.uuid && editingEmployee.position === ROLES.SUPERVISOR"
              class="btn btn-secondary"
              type="button"
              :disabled="backupInProgress"
              @click="handleBackupDatabase"
            >
              {{ backupInProgress ? 'Архивация…' : 'Архивация' }}
            </button>
            <button
              v-if="userRole === ROLES.SUPERVISOR"
              class="btn btn-secondary"
              type="button"
              @click="organizationModalOpen = true"
            >
              Ввести данные организации
            </button>
            <h1 class="order-detail-title">
              {{ editingEmployee.uuid ? editingEmployee.full_name : 'Новый сотрудник' }}
            </h1>
            <button
              v-if="userRole === ROLES.SUPERVISOR && editingEmployee.uuid && editingEmployee.position === ROLES.SUPERVISOR"
              class="btn btn-secondary"
              type="button"
              :disabled="restoreInProgress"
              @click="$refs.restoreFileInput.click()"
            >
              {{ restoreInProgress ? 'Восстановление…' : 'Загрузить БД из архива' }}
            </button>
            <input
              ref="restoreFileInput"
              type="file"
              accept=".sql,.gz,.sql.gz"
              style="display: none"
              @change="handleRestoreDatabase"
            >
            <button
              v-if="userRole === ROLES.SUPERVISOR && editingEmployee.uuid && editingEmployee.position === ROLES.SUPERVISOR"
              class="btn btn-primary btn-danger"
              type="button"
              :disabled="purgeInProgress"
              @click="handlePurgeDatabase"
            >
              {{ purgeInProgress ? 'Очистка…' : 'Очистить БД' }}
            </button>
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
                :devices="devices"
                :device-types="deviceTypes"
                :brands="brands"
                :user-role="userRole"
                :current-employee-name="currentEmployeeName"
                :order-form="orderForm"
                @open-details="openOrderDetails"
                @submit-order-form="submitOrderForm"
                @start-create-order="startCreateOrder"
                @cancel-order-form="orderForm.open = false"
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
              <BrandList
                v-else-if="activeTab === 'brands'"
                :brands="brands"
                :user-role="userRole"
                @create-brand="openBrandModal"
                @edit-brand="editBrandModal"
                @delete-brand="handleDeleteBrand"
              />
              <DeviceTypeList
                v-else-if="activeTab === 'deviceTypes'"
                :device-types="deviceTypes"
                :user-role="userRole"
                @create-device-type="openDeviceTypeModal"
                @edit-device-type="editDeviceTypeModal"
                @delete-device-type="handleDeleteDeviceType"
              />
              <StatisticsView
                v-else-if="activeTab === 'statistics' && statisticsData"
                :data="statisticsData"
              />
              <InfoView
                v-else-if="activeTab === 'info'"
              />
            </template>
          </div>
        </section>
      </main>
    </section>

    <LoginModal v-model="loginModalOpen" @login-success="loadData" />

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

    <OrganizationModal
      :open="organizationModalOpen"
      @close="organizationModalOpen = false"
      @saved="organizationModalOpen = false"
    />

    <BrandModal
      :open="brandModalOpen"
      :edit-brand="editingBrand"
      @close="closeBrandModal"
      @submit="submitBrandModal"
    />

    <DeviceTypeModal
      :open="deviceTypeModalOpen"
      :edit-device-type="editingDeviceType"
      @close="closeDeviceTypeModal"
      @submit="submitDeviceTypeModal"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { useAuth } from './composables/useAuth';
import { extractErrorMessage } from './utils/errorHelpers';
import { canManageEmployees, canManageParts, ROLES } from './constants/roles';
import LoginModal from './components/LoginModal.vue';
import OrganizationModal from './components/OrganizationModal.vue';
import OrderList from './components/OrderList.vue';
import OrderDetail from './components/OrderDetail.vue';
import EmployeeList from './components/EmployeeList.vue';
import EmployeeForm from './components/EmployeeForm.vue';
import PartsList from './components/PartsList.vue';
import BrandList from './components/BrandList.vue';
import BrandModal from './components/BrandModal.vue';
import DeviceTypeList from './components/DeviceTypeList.vue';
import DeviceTypeModal from './components/DeviceTypeModal.vue';
import StatisticsView from './components/StatisticsView.vue';
import InfoView from './components/InfoView.vue';
import ClientModal from './components/ClientModal.vue';
import PartModal from './components/PartModal.vue';
import WorkModal from './components/WorkModal.vue';
import OrderPartModal from './components/OrderPartModal.vue';
import {
  createClient,
  createDevice,
  createOrderWithClientAndDevice,
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
  getBrands,
  getStatistics,
  getValidationRules,
  createBrand,
  updateBrand,
  deleteBrand,
  createDeviceType,
  updateDeviceType,
  deleteDeviceType,
  updateOrder,
  updatePart,
  purgeDatabase,
  backupDatabase,
  restoreDatabase,
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
const brands = ref([]);
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
  newClient: {
    uuid: null,
    full_name: '',
    phone: '',
    email: '',
    telegram_nick: '',
    address: '',
  },
  newDevice: {
    type_uuid: '',
    brand_uuid: '',
    model: '',
    serial_number: '',
    description: '',
  },
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

const workModalOpen = ref(false);
const orderPartModalOpen = ref(false);
const organizationModalOpen = ref(false);
const partModalOpen = ref(false);
const editPartUuid = ref(null);
const partModalData = ref(null);
const brandModalOpen = ref(false);
const editingBrand = ref(null);
const deviceTypeModalOpen = ref(false);
const editingDeviceType = ref(null);
const purgeInProgress = ref(false);
const backupInProgress = ref(false);
const restoreInProgress = ref(false);
const restoreFileInput = ref(null);

const currentCount = computed(() => {
  switch (activeTab.value) {
    case 'orders': return orders.value.length;
    case 'employees': return employees.value.length;
    case 'parts': return parts.value.length;
    case 'brands': return brands.value.length;
    case 'deviceTypes': return deviceTypes.value.length;
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
          const [ordersRes, clientsRes, devicesData, employeesRes, brandsData] = await Promise.all([
            getOrders(), getClients(), getDevices(), getEmployees(), getBrands(),
          ]);
          orders.value = ordersRes.items;
          clients.value = clientsRes.items;
          devices.value = devicesData;
          employees.value = employeesRes.items;
          brands.value = brandsData;
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
      case 'brands':
        brands.value = await getBrands();
        break;
      case 'deviceTypes':
        deviceTypes.value = await getDeviceTypes();
        break;
      case 'statistics':
        statisticsData.value = await getStatistics();
        break;
      case 'info':
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
  brands.value = [];
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

async function handlePurgeDatabase() {
  if (!window.confirm('Вы уверены? Все данные кроме учётной записи супервизора будут удалены. Это действие невозможно отменить!')) return;
  purgeInProgress.value = true;
  try {
    await purgeDatabase();
    window.alert('База данных успешно очищена.');
    await loadData();
  } catch (e) {
    loadError.value = extractErrorMessage(e, 'Ошибка очистки базы данных.');
  } finally {
    purgeInProgress.value = false;
  }
}

async function handleBackupDatabase() {
  backupInProgress.value = true;
  try {
    const blob = await backupDatabase();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `remonline_backup_${new Date().toISOString().slice(0, 19).replace(/[:-]/g, '')}.sql.gz`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } catch (e) {
    loadError.value = extractErrorMessage(e, 'Ошибка создания резервной копии.');
  } finally {
    backupInProgress.value = false;
  }
}

async function handleRestoreDatabase(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  event.target.value = '';

  if (!window.confirm(
    'Вы уверены? Текущая база данных будет полностью заменена данными из архива. Это действие невозможно отменить!'
  )) return;

  restoreInProgress.value = true;
  try {
    await restoreDatabase(file);
    window.alert('База данных успешно восстановлена из архива.');
    await loadData();
  } catch (e) {
    loadError.value = extractErrorMessage(e, 'Ошибка восстановления базы данных из архива.');
  } finally {
    restoreInProgress.value = false;
  }
}

function handlePartsUpdate(updated) {
  parts.value = updated;
}

function handleOrderUpdate(updated) {
  orderDetails.value.data = updated;
}

function closeAllModals() {
  loginModalOpen.value = false;
  partModalOpen.value = false;
  workModalOpen.value = false;
  orderPartModalOpen.value = false;
}

function handleKeydown(event) {
  if (event.key === 'Escape') {
    if (loginModalOpen.value || partModalOpen.value || workModalOpen.value || orderPartModalOpen.value || organizationModalOpen.value) {
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

async function ensureDeviceTypes() {
  try {
    if (!deviceTypes.value.length) {
      deviceTypes.value = await getDeviceTypes();
    }
  } catch (e) {
    loadError.value = extractErrorMessage(e, 'Не удалось загрузить типы устройств.');
  }
}

async function ensureBrands() {
  try {
    if (!brands.value.length) {
      brands.value = await getBrands();
    }
  } catch (e) {
    loadError.value = extractErrorMessage(e, 'Не удалось загрузить бренды.');
  }
}

async function startCreateOrder() {
  await ensureOrderReferences();
  await ensureDeviceTypes();
  await ensureBrands();
  orderForm.value.open = true;
  orderForm.value.editMode = false;
  orderForm.value.uuid = null;
  orderForm.value.newClient = {
    uuid: null,
    full_name: '',
    phone: '',
    email: '',
    telegram_nick: '',
    address: '',
  };
  orderForm.value.newDevice = {
    type_uuid: '',
    brand_uuid: '',
    model: '',
    serial_number: '',
    description: '',
  };
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
      // Новый заказ: агрегированный вызов — клиент + устройство + заказ за один запрос
      const nc = orderForm.value.newClient;
      const nd = orderForm.value.newDevice;
      const data = orderForm.value.data;

      const payload = {
        existing_client_uuid: nc.uuid || null,
        client_full_name: nc.full_name || null,
        client_phone: nc.phone || null,
        client_email: nc.email || null,
        client_telegram_nick: nc.telegram_nick || null,
        client_comment: data.comment || null,
        client_address: nc.address || null,

        device_type_uuid: nd.type_uuid,
        device_brand_uuid: nd.brand_uuid || null,
        device_model: nd.model,
        device_serial_number: nd.serial_number || null,
        device_description: nd.description || null,

        assigned_employee_uuid: data.assigned_employee_uuid || null,
        manager_uuid: data.manager_uuid || null,
        status: data.status,
        problem_description: data.problem_description || null,
        price: data.price,
      };

      if (userRole.value === 'manager') {
        payload.manager_uuid = null;
      }

      await createOrderWithClientAndDevice(payload);
      // После успешного создания перезагружаем справочники, чтобы подтянуть нового клиента/устройство
      clients.value = (await getClients()).items;
      devices.value = await getDevices();
    }
    await loadData();
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

// submitOrderClientModal больше не используется после переноса формы клиента в OrderList

function openBrandModal() {
  editingBrand.value = null;
  brandModalOpen.value = true;
}

function editBrandModal(brand) {
  editingBrand.value = brand;
  brandModalOpen.value = true;
}

function closeBrandModal() {
  brandModalOpen.value = false;
  editingBrand.value = null;
}

async function submitBrandModal(payload) {
  try {
    if (editingBrand.value) {
      await updateBrand(editingBrand.value.uuid, payload);
    } else {
      await createBrand(payload);
    }
    brands.value = await getBrands();
    closeBrandModal();
  } catch (e) {
    loadError.value = extractErrorMessage(e, 'Ошибка сохранения бренда.');
  }
}

async function handleDeleteBrand(brand) {
  if (!window.confirm(`Удалить бренд «${brand.name}»?`)) return;
  try {
    await deleteBrand(brand.uuid);
    brands.value = await getBrands();
  } catch (e) {
    loadError.value = extractErrorMessage(e, 'Не удалось удалить бренд.');
  }
}

function openDeviceTypeModal() {
  editingDeviceType.value = null;
  deviceTypeModalOpen.value = true;
}

function editDeviceTypeModal(deviceType) {
  editingDeviceType.value = deviceType;
  deviceTypeModalOpen.value = true;
}

function closeDeviceTypeModal() {
  deviceTypeModalOpen.value = false;
  editingDeviceType.value = null;
}

async function submitDeviceTypeModal(payload) {
  try {
    if (editingDeviceType.value) {
      await updateDeviceType(editingDeviceType.value.uuid, payload);
    } else {
      await createDeviceType(payload);
    }
    deviceTypes.value = await getDeviceTypes();
    closeDeviceTypeModal();
  } catch (e) {
    loadError.value = extractErrorMessage(e, 'Ошибка сохранения типа устройства.');
  }
}

async function handleDeleteDeviceType(deviceType) {
  if (!window.confirm(`Удалить тип «${deviceType.name}»?`)) return;
  try {
    await deleteDeviceType(deviceType.uuid);
    deviceTypes.value = await getDeviceTypes();
  } catch (e) {
    loadError.value = extractErrorMessage(e, 'Не удалось удалить тип устройства.');
  }
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
