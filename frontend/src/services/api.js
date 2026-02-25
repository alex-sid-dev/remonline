import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

api.interceptors.request.use((config) => {
  const token = window.localStorage.getItem('access_token');
  if (token) {
    // Backend expects a Bearer token issued by Keycloak
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const status = error?.response?.status;

    // Try to refresh access token on 401 once
    if (status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = window.localStorage.getItem('refresh_token');

      if (!refreshToken) {
        window.localStorage.removeItem('access_token');
        return Promise.reject(error);
      }

      try {
        const refreshResponse = await axios.post('/api/auth/refresh', {
          refresh_token: refreshToken,
        });
        const data = refreshResponse.data;

        window.localStorage.setItem('access_token', data.access_token);
        window.localStorage.setItem('refresh_token', data.refresh_token);

        originalRequest.headers = {
          ...(originalRequest.headers || {}),
          Authorization: `Bearer ${data.access_token}`,
        };

        return api.request(originalRequest);
      } catch (refreshError) {
        window.localStorage.removeItem('access_token');
        window.localStorage.removeItem('refresh_token');
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  },
);

export async function login(email, password) {
  const response = await api.post('/auth/login', {
    email,
    password,
  });

  const data = response.data;

  window.localStorage.setItem('access_token', data.access_token);
  window.localStorage.setItem('refresh_token', data.refresh_token);
  window.localStorage.setItem('last_login_email', email);

  return data;
}

export async function logout() {
  const refreshToken = window.localStorage.getItem('refresh_token');

  if (refreshToken) {
    try {
      await api.post('/auth/logout', { refresh_token: refreshToken });
    } catch {
      // ignore backend errors on logout for UX simplicity
    }
  }

  window.localStorage.removeItem('access_token');
  window.localStorage.removeItem('refresh_token');
}

export async function getClients() {
  const response = await api.get('/client/all');
  return response.data;
}

export async function getOrders() {
  const response = await api.get('/order/all');
  return response.data;
}

export async function getOrderDetails(uuid) {
  const response = await api.get(`/order/${uuid}`);
  return response.data;
}

// Clients CRUD
export async function createClient(payload) {
  const response = await api.post('/client/create', payload);
  return response.data;
}

export async function updateClient(uuid, payload) {
  await api.patch(`/client/update/${uuid}`, payload);
}

export async function deleteClient(uuid) {
  await api.delete(`/client/${uuid}`);
}

// Orders CRUD
export async function createOrder(payload) {
  const response = await api.post('/order/create', payload);
  return response.data;
}

export async function createOrderWithClientAndDevice(payload) {
  const response = await api.post('/order/create-aggregate', payload);
  return response.data;
}

export async function updateOrder(uuid, payload) {
  await api.patch(`/order/update/${uuid}`, payload);
}

export async function deleteOrder(uuid) {
  await api.delete(`/order/${uuid}`);
}

// Device types CRUD
export async function getDeviceTypes() {
  const response = await api.get('/device_type/all');
  return response.data;
}

export async function createDeviceType(payload) {
  const response = await api.post('/device_type/create', payload);
  return response.data;
}

export async function updateDeviceType(uuid, payload) {
  await api.patch(`/device_type/update/${uuid}`, payload);
}

export async function deleteDeviceType(uuid) {
  await api.delete(`/device_type/${uuid}`);
}

// Brands CRUD
export async function getBrands() {
  const response = await api.get('/brand/all');
  return response.data;
}

export async function createBrand(payload) {
  const response = await api.post('/brand/create', payload);
  return response.data;
}

export async function updateBrand(uuid, payload) {
  await api.patch(`/brand/update/${uuid}`, payload);
}

export async function deleteBrand(uuid) {
  await api.delete(`/brand/${uuid}`);
}

// Devices CRUD
export async function getDevices() {
  const response = await api.get('/device/all');
  return response.data;
}

export async function createDevice(payload) {
  const response = await api.post('/device/create', payload);
  return response.data;
}

export async function updateDevice(uuid, payload) {
  await api.patch(`/device/update/${uuid}`, payload);
}

export async function deleteDevice(uuid) {
  await api.delete(`/device/${uuid}`);
}

// Parts CRUD
export async function getParts() {
  const response = await api.get('/part/all');
  return response.data;
}

export async function createPart(payload) {
  const response = await api.post('/part/create', payload);
  return response.data;
}

export async function updatePart(uuid, payload) {
  await api.patch(`/part/update/${uuid}`, payload);
}

export async function deletePart(uuid) {
  await api.delete(`/part/${uuid}`);
}

// Works CRUD
export async function getWorks() {
  const response = await api.get('/work/all');
  return response.data;
}

export async function createWork(payload) {
  const response = await api.post('/work/create', payload);
  return response.data;
}

export async function updateWork(uuid, payload) {
  await api.patch(`/work/update/${uuid}`, payload);
}

export async function deleteWork(uuid) {
  await api.delete(`/work/${uuid}`);
}

// Payments CRUD
export async function getPayments() {
  const response = await api.get('/payment/all');
  return response.data;
}

export async function createPayment(payload) {
  const response = await api.post('/payment/create', payload);
  return response.data;
}

export async function updatePayment(uuid, payload) {
  await api.patch(`/payment/update/${uuid}`, payload);
}

export async function deletePayment(uuid) {
  await api.delete(`/payment/${uuid}`);
}

// Order parts CRUD
export async function getOrderParts() {
  const response = await api.get('/order_part/all');
  return response.data;
}

export async function createOrderPart(payload) {
  const response = await api.post('/order_part/create', payload);
  return response.data;
}

export async function updateOrderPart(uuid, payload) {
  await api.patch(`/order_part/update/${uuid}`, payload);
}

export async function deleteOrderPart(uuid) {
  await api.delete(`/order_part/${uuid}`);
}

// Employees CRUD
export async function getEmployees() {
  const response = await api.get('/employee/all');
  return response.data;
}

/** Текущий авторизованный сотрудник (id, full_name, position и т.д.) — для определения роли на фронте */
export async function getCurrentEmployee() {
  const response = await api.get('/employee/me');
  return response.data;
}

export async function createEmployee(payload) {
  const response = await api.post('/employee/create', payload);
  return response.data;
}

export async function updateEmployee(uuid, payload) {
  await api.patch(`/employee/update/${uuid}`, payload);
}

export async function deleteEmployee(uuid) {
  await api.delete(`/employee/${uuid}`);
}

export async function changeEmployeePassword(uuid, newPassword) {
  await api.post(`/employee/${uuid}/change-password`, { new_password: newPassword });
}

export async function registerUser(email, password) {
  const response = await api.post('/auth/register', {
    email,
    password,
  });
  return response.data;
}

export async function getOrderActHtml(uuid) {
  const response = await api.get(`/order/${uuid}/act`, {
    responseType: 'blob',
  });
  return response.data;
}

export async function getOrderReceiptHtml(uuid) {
  const response = await api.get(`/order/${uuid}/receipt`, {
    responseType: 'blob',
  });
  return response.data;
}

export async function createOrderComment(payload) {
  const response = await api.post('/order_comment/create', payload);
  return response.data;
}

// Organization (singleton)
export async function getOrganization() {
  const response = await api.get('/organization');
  return response.data;
}

export async function createOrganization(payload) {
  const response = await api.post('/organization', payload);
  return response.data;
}

export async function updateOrganization(payload) {
  await api.put('/organization', payload);
}

export async function deleteOrganization() {
  await api.delete('/organization');
}

/** Правила валидации с бэкенда (из Pydantic-схем) — для форм сотрудника, логина и т.д. */
export async function getValidationRules() {
  const response = await api.get('/validation-rules');
  return response.data;
}

export async function getStatistics() {
  const response = await api.get('/statistics');
  return response.data;
}

// Admin (supervisor only)
export async function purgeDatabase() {
  const response = await api.delete('/admin/purge');
  return response.data;
}

export async function backupDatabase() {
  const response = await api.get('/admin/backup', { responseType: 'blob' });
  return response.data;
}

export async function restoreDatabase(file) {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/admin/restore', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

export default api;

