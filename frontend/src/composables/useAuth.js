import { ref, computed } from 'vue';
import { login, logout, getCurrentEmployee } from '../services/api';
import { ROLES } from '../constants/roles';

const email = ref('');
const password = ref('');
const isLoggingIn = ref(false);
const loginError = ref('');
const loginSuccess = ref(false);
const accessToken = ref('');
const lastLoginEmail = ref('');
const loginModalOpen = ref(false);
const userRole = ref('other');
const currentEmployeeName = ref('');

const isAuthenticated = computed(() => !!accessToken.value);

async function handleLogin() {
  loginError.value = '';
  loginSuccess.value = false;
  isLoggingIn.value = true;

  try {
    const data = await login(email.value, password.value);
    accessToken.value = data.access_token;
    lastLoginEmail.value = email.value;
    await refreshUserRole();
    loginSuccess.value = true;
    loginModalOpen.value = false;
    return true;
  } catch (e) {
    const message = e?.response?.data?.detail || e?.message || 'Ошибка авторизации.';
    loginError.value = typeof message === 'string' ? message : 'Ошибка авторизации.';
    return false;
  } finally {
    isLoggingIn.value = false;
  }
}

async function handleLogout() {
  await logout();
  accessToken.value = '';
}

function openLoginModal() {
  loginError.value = '';
  loginSuccess.value = false;
  loginModalOpen.value = true;
}

async function refreshUserRole() {
  if (!accessToken.value) {
    userRole.value = 'other';
    return;
  }
  try {
    const me = await getCurrentEmployee();
    const pos = (me?.position || '').toLowerCase();
    currentEmployeeName.value = me?.full_name || '';
    if (pos === ROLES.SUPERVISOR) userRole.value = ROLES.SUPERVISOR;
    else if (pos === ROLES.ADMIN) userRole.value = ROLES.ADMIN;
    else if (pos === ROLES.MANAGER) userRole.value = ROLES.MANAGER;
    else if (pos === ROLES.MASTER) userRole.value = ROLES.MASTER;
    else userRole.value = 'other';
    window.localStorage.setItem('user_role', userRole.value);
  } catch {
    userRole.value = 'other';
    window.localStorage.setItem('user_role', userRole.value);
  }
}

function initAuth() {
  accessToken.value = window.localStorage.getItem('access_token') || '';
  lastLoginEmail.value = window.localStorage.getItem('last_login_email') || '';
}

export function useAuth() {
  return {
    email,
    password,
    isLoggingIn,
    loginError,
    loginSuccess,
    accessToken,
    lastLoginEmail,
    loginModalOpen,
    userRole,
    currentEmployeeName,
    isAuthenticated,
    handleLogin,
    handleLogout,
    openLoginModal,
    refreshUserRole,
    initAuth,
  };
}
