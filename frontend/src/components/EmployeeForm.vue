<template>
  <div class="employee-form-page">
    <div class="employee-form-card login-card">
      <div class="field">
        <div class="field-label form-title">
          {{ editMode ? 'Редактирование сотрудника' : 'Новый сотрудник' }}
        </div>
      </div>

      <!-- Create mode: email + password -->
      <template v-if="!editMode">
        <div class="field">
          <label class="field-label" for="emp-email">Email</label>
          <input
            id="emp-email"
            v-model="form.email"
            class="field-input"
            :class="{ 'field-input--error': empEmailError }"
            type="email"
            autocomplete="off"
          >
          <div v-if="empEmailError" class="error">
            {{ empEmailError }}
          </div>
        </div>
        <div class="field">
          <label class="field-label" for="emp-password">Пароль</label>
          <input
            id="emp-password"
            v-model="form.password"
            class="field-input"
            :class="{ 'field-input--error': empPasswordError }"
            type="password"
            autocomplete="new-password"
          >
          <div v-if="empPasswordError" class="error">
            {{ empPasswordError }}
          </div>
        </div>
      </template>

      <!-- Fields -->
      <div class="field">
        <label class="field-label" for="emp-fullname">ФИО</label>
        <input
          id="emp-fullname"
          v-model="form.full_name"
          class="field-input"
          :disabled="!canEditFields"
          type="text"
        >
      </div>
      <div class="field">
        <label class="field-label" for="emp-phone">Телефон</label>
        <input
          id="emp-phone"
          v-model="form.phone"
          class="field-input"
          :disabled="!canEditFields"
          type="text"
          placeholder="+78008008000"
        >
        <div v-if="canEditFields" class="hint">
          Формат: +7 и 10 цифр, например +78008008000
        </div>
      </div>
      <div class="field">
        <label class="field-label" for="emp-position">Роль</label>
        <select
          id="emp-position"
          v-model="form.position"
          class="field-input"
          :disabled="!canEditFields"
        >
          <option value="master">master</option>
          <option value="manager">manager</option>
          <option value="admin">admin</option>
          <option v-if="userRole === ROLES.SUPERVISOR" value="supervisor">supervisor</option>
        </select>
      </div>

      <!-- Salary / profit_percent: only supervisor -->
      <template v-if="userRole === ROLES.SUPERVISOR">
        <div class="field">
          <label class="field-label" for="emp-salary">Зарплата в месяц</label>
          <input
            id="emp-salary"
            v-model.number="form.salary"
            class="field-input"
            type="number"
            min="0"
            step="1"
            placeholder="0"
            @keydown="blockNonNumeric"
          >
        </div>
        <div class="field">
          <label class="field-label" for="emp-profit-percent">% от прибыли</label>
          <input
            id="emp-profit-percent"
            v-model.number="form.profit_percent"
            class="field-input"
            type="number"
            min="0"
            max="100"
            step="0.1"
            placeholder="0"
            @keydown="blockNonNumeric"
          >
        </div>
      </template>
      <template v-else-if="editMode">
        <div class="field">
          <label class="field-label">Зарплата в месяц</label>
          <input
            class="field-input"
            :value="employee?.salary ?? '—'"
            disabled
          >
        </div>
        <div class="field">
          <label class="field-label">% от прибыли</label>
          <input
            class="field-input"
            :value="employee?.profit_percent != null ? employee.profit_percent + '%' : '—'"
            disabled
          >
        </div>
      </template>

      <!-- Save button -->
      <div v-if="canEditFields" class="employee-form-actions">
        <button
          class="btn btn-primary"
          type="button"
          :disabled="!formValid"
          @click="submit"
        >
          Сохранить
        </button>
      </div>

      <!-- Password change: supervisor + admin (with restrictions) -->
      <div
        v-if="editMode && canChangePassword"
        class="mt-16 border-top-subtle"
      >
        <div class="field">
          <label class="field-label" for="emp-new-password">Новый пароль</label>
          <input
            id="emp-new-password"
            v-model="newPassword"
            class="field-input"
            type="password"
            autocomplete="new-password"
            placeholder="Введите новый пароль"
          >
        </div>
        <div class="employee-form-actions">
          <button
            class="btn btn-primary"
            type="button"
            :disabled="!newPassword || newPassword.length < 6"
            @click="changePassword"
          >
            Сменить пароль
          </button>
        </div>
        <div v-if="passwordMessage" class="hint text-center">
          {{ passwordMessage }}
        </div>
      </div>

      <!-- Delete: any employee except supervisor -->
      <div
        v-if="editMode && canEditFields && employee?.position !== ROLES.SUPERVISOR"
        class="employee-form-actions mt-16 border-top-subtle"
      >
        <button
          class="btn btn-primary btn-danger"
          type="button"
          @click="remove"
        >
          Удалить сотрудника
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue';
import { blockNonNumeric } from '../utils/inputHelpers';
import { extractErrorMessage } from '../utils/errorHelpers';
import { ROLES } from '../constants/roles';
import {
  registerUser,
  createEmployee,
  updateEmployee,
  deleteEmployee,
  getEmployees,
  changeEmployeePassword,
} from '../services/api';

const props = defineProps({
  employee: { type: Object, default: null },
  userRole: { type: String, required: true },
  validationRules: { type: Object, default: null },
});

const emit = defineEmits(['saved', 'deleted', 'error']);

const editMode = computed(() => !!props.employee);

const canEditFields = computed(() => {
  if (!editMode.value) return true;
  if (props.userRole === ROLES.SUPERVISOR) return true;
  if (props.userRole === ROLES.ADMIN) {
    return [ROLES.MASTER, ROLES.MANAGER].includes(props.employee?.position);
  }
  return false;
});

const canChangePassword = computed(() => {
  if (!props.employee) return false;
  if (props.userRole === ROLES.SUPERVISOR) return true;
  if (props.userRole === ROLES.ADMIN) {
    return [ROLES.MASTER, ROLES.MANAGER].includes(props.employee.position);
  }
  return false;
});

const form = reactive({
  email: '',
  password: '',
  full_name: props.employee?.full_name ?? '',
  phone: props.employee?.phone ?? '',
  position: props.employee?.position ?? 'master',
  salary: props.employee?.salary ?? null,
  profit_percent: props.employee?.profit_percent ?? null,
});

const newPassword = ref('');
const passwordMessage = ref('');

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const empEmailError = computed(() => {
  if (editMode.value) return '';
  const v = (form.email ?? '').trim();
  if (!v) return props.validationRules?.email?.message ?? 'Введите email';
  if (!EMAIL_RE.test(v)) return props.validationRules?.email?.message ?? 'Некорректный формат email';
  return '';
});

const empPasswordError = computed(() => {
  if (editMode.value) return '';
  const v = form.password ?? '';
  if (!v) return props.validationRules?.password?.messages?.required ?? 'Введите пароль';
  const p = props.validationRules?.password;
  const msg = p?.messages;
  if (!p) return v.length < 6 ? 'Пароль не менее 6 символов' : '';
  if (v.length < p.min_length || v.length > p.max_length) return msg?.length ?? `Пароль от ${p.min_length} до ${p.max_length} символов`;
  if (!/\d/.test(v)) return msg?.digit ?? 'Пароль должен содержать хотя бы одну цифру';
  if (!/[A-Z]/.test(v)) return msg?.uppercase ?? 'Пароль должен содержать хотя бы одну заглавную букву';
  const special = p.special_characters ?? "!@#$%^&*(),.?\":{}|<>_-+[]=\\/";
  if (![...special].some((c) => v.includes(c))) return msg?.special ?? 'Пароль должен содержать хотя бы один спецсимвол';
  return '';
});

const formValid = computed(() => {
  if (editMode.value) {
    return (form.full_name ?? '').trim().length > 0;
  }
  return !empEmailError.value && !empPasswordError.value && (form.full_name ?? '').trim().length > 0;
});

async function submit() {
  try {
    if (editMode.value && props.employee) {
      const payload = {
        full_name: form.full_name,
        phone: form.phone,
        position: form.position,
      };
      if (props.userRole === ROLES.SUPERVISOR) {
        if (form.salary != null) payload.salary = form.salary;
        if (form.profit_percent != null) payload.profit_percent = form.profit_percent;
      }
      await updateEmployee(props.employee.uuid, payload);
    } else {
      const registration = await registerUser(form.email, form.password);
      const payload = {
        user_uuid: registration.uuid,
        full_name: form.full_name,
        phone: form.phone,
        position: form.position,
      };
      if (props.userRole === ROLES.SUPERVISOR) {
        if (form.salary != null) payload.salary = form.salary;
        if (form.profit_percent != null) payload.profit_percent = form.profit_percent;
      }
      await createEmployee(payload);
    }
    const result = await getEmployees();
    emit('saved', result.items);
  } catch (e) {
    emit('error', extractErrorMessage(e, 'Ошибка сохранения сотрудника.'));
  }
}

async function changePassword() {
  if (!props.employee || !newPassword.value) return;
  passwordMessage.value = '';
  try {
    await changeEmployeePassword(props.employee.uuid, newPassword.value);
    newPassword.value = '';
    passwordMessage.value = 'Пароль успешно изменён';
    setTimeout(() => { passwordMessage.value = ''; }, 3000);
  } catch (e) {
    emit('error', extractErrorMessage(e, 'Ошибка смены пароля.'));
  }
}

async function remove() {
  if (!props.employee) return;
  if (!window.confirm(`Удалить ${form.full_name || 'сотрудника'}? Это действие невозможно отменить.`)) return;
  try {
    await deleteEmployee(props.employee.uuid);
    const result = await getEmployees();
    emit('deleted', result.items);
  } catch (e) {
    emit('error', extractErrorMessage(e, 'Ошибка удаления сотрудника.'));
  }
}
</script>
