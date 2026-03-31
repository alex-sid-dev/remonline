<template>
  <div
    v-if="modelValue"
    class="modal-backdrop"
    @click="$emit('update:modelValue', false)"
  >
    <div
      class="modal"
      @click.stop
    >
      <form
        class="login-card"
        @submit.prevent="onSubmit"
      >
        <div class="field">
          <div class="field-label form-title">
            Регистрация супервизора
          </div>
        </div>

        <div class="field">
          <label class="field-label" for="sup-email">Email</label>
          <input
            id="sup-email"
            v-model="form.email"
            class="field-input"
            :class="{ 'field-input--error': touched.email && fieldErrors.email }"
            type="email"
            autocomplete="email"
            placeholder="owner@company.ru"
            required
            @blur="markTouched('email')"
          >
          <div class="hint">
            Используйте реальный email в формате name@domain.tld.
          </div>
          <div v-if="touched.email && fieldErrors.email" class="error">
            {{ fieldErrors.email }}
          </div>
        </div>

        <div class="field">
          <label class="field-label" for="sup-password">Пароль</label>
          <input
            id="sup-password"
            v-model="form.password"
            class="field-input"
            :class="{ 'field-input--error': touched.password && fieldErrors.password }"
            type="password"
            autocomplete="new-password"
            placeholder="Придумайте сложный пароль"
            required
            @blur="markTouched('password')"
          >
          <div class="hint">
            От 6 до 10 символов, минимум 1 заглавная буква, 1 цифра и 1 спецсимвол.
          </div>
          <div v-if="touched.password && fieldErrors.password" class="error">
            {{ fieldErrors.password }}
          </div>
        </div>

        <div class="field">
          <label class="field-label" for="sup-fullname">ФИО супервизора</label>
          <input
            id="sup-fullname"
            v-model="form.full_name"
            class="field-input"
            :class="{ 'field-input--error': touched.full_name && fieldErrors.full_name }"
            type="text"
            placeholder="Иванов Иван Иванович"
            required
            @blur="markTouched('full_name')"
          >
          <div class="hint">
            Обязательное поле.
          </div>
          <div v-if="touched.full_name && fieldErrors.full_name" class="error">
            {{ fieldErrors.full_name }}
          </div>
        </div>

        <div class="field">
          <label class="field-label" for="sup-phone">Телефон</label>
          <input
            id="sup-phone"
            v-model="form.phone"
            class="field-input"
            :class="{ 'field-input--error': touched.phone && fieldErrors.phone }"
            type="text"
            placeholder="+78008008000"
            required
            @blur="markTouched('phone')"
          >
          <div class="hint">
            Формат: +7 и 10 цифр, например +78008008000
          </div>
          <div v-if="touched.phone && fieldErrors.phone" class="error">
            {{ fieldErrors.phone }}
          </div>
        </div>

        <div class="field">
          <label class="field-label" for="sup-org-name">Название компании</label>
          <input
            id="sup-org-name"
            v-model="form.organization_name"
            class="field-input"
            :class="{ 'field-input--error': touched.organization_name && fieldErrors.organization_name }"
            type="text"
            placeholder="ООО «Ремонт-сервис»"
            required
            @blur="markTouched('organization_name')"
          >
          <div class="hint">
            Обязательное поле.
          </div>
          <div v-if="touched.organization_name && fieldErrors.organization_name" class="error">
            {{ fieldErrors.organization_name }}
          </div>
        </div>

        <div class="field">
          <label class="field-label" for="sup-inn">ИНН</label>
          <input
            id="sup-inn"
            v-model="form.inn"
            class="field-input"
            :class="{ 'field-input--error': touched.inn && fieldErrors.inn }"
            type="text"
            placeholder="1234567890"
            required
            @blur="markTouched('inn')"
          >
          <div class="hint">
            10 или 12 цифр без пробелов и разделителей.
          </div>
          <div v-if="touched.inn && fieldErrors.inn" class="error">
            {{ fieldErrors.inn }}
          </div>
        </div>

        <div class="field">
          <label class="field-label" for="sup-address">Адрес (необязательно)</label>
          <input
            id="sup-address"
            v-model="form.address"
            class="field-input"
            type="text"
            placeholder="Город, улица, дом"
          >
        </div>

        <div class="field row">
          <div class="col">
            <label class="field-label" for="sup-kpp">КПП (необязательно)</label>
            <input
              id="sup-kpp"
              v-model="form.kpp"
              class="field-input"
              :class="{ 'field-input--error': touched.kpp && fieldErrors.kpp }"
              type="text"
              placeholder="123456789"
              @blur="markTouched('kpp')"
            >
            <div class="hint">
              Если заполняете, укажите 9 цифр.
            </div>
            <div v-if="touched.kpp && fieldErrors.kpp" class="error">
              {{ fieldErrors.kpp }}
            </div>
          </div>
          <div class="col">
            <label class="field-label" for="sup-bik">БИК (необязательно)</label>
            <input
              id="sup-bik"
              v-model="form.bik"
              class="field-input"
              :class="{ 'field-input--error': touched.bik && fieldErrors.bik }"
              type="text"
              placeholder="044525225"
              @blur="markTouched('bik')"
            >
            <div class="hint">
              Если заполняете, укажите 9 цифр.
            </div>
            <div v-if="touched.bik && fieldErrors.bik" class="error">
              {{ fieldErrors.bik }}
            </div>
          </div>
        </div>

        <div class="field row">
          <div class="col">
            <label class="field-label" for="sup-bank-account">Р/с (необязательно)</label>
            <input
              id="sup-bank-account"
              v-model="form.bank_account"
              class="field-input"
              :class="{ 'field-input--error': touched.bank_account && fieldErrors.bank_account }"
              type="text"
              placeholder="40702810900000000001"
              @blur="markTouched('bank_account')"
            >
            <div class="hint">
              Если заполняете, укажите 20 цифр.
            </div>
            <div v-if="touched.bank_account && fieldErrors.bank_account" class="error">
              {{ fieldErrors.bank_account }}
            </div>
          </div>
          <div class="col">
            <label class="field-label" for="sup-corr-account">К/с (необязательно)</label>
            <input
              id="sup-corr-account"
              v-model="form.corr_account"
              class="field-input"
              :class="{ 'field-input--error': touched.corr_account && fieldErrors.corr_account }"
              type="text"
              placeholder="30101810400000000225"
              @blur="markTouched('corr_account')"
            >
            <div class="hint">
              Если заполняете, укажите 20 цифр.
            </div>
            <div v-if="touched.corr_account && fieldErrors.corr_account" class="error">
              {{ fieldErrors.corr_account }}
            </div>
          </div>
        </div>

        <div class="hint">
          Эти данные используются для создания вашей компании и печатных форм.
        </div>

        <div v-if="error" class="error">
          {{ error }}
        </div>
        <div v-if="success" class="success">
          Регистрация выполнена, вход выполнен.
        </div>

        <div class="field">
          <button
            class="btn btn-primary"
            type="submit"
            :disabled="isSubmitting || !isFormValid"
          >
            <span v-if="isSubmitting" class="loader">
              <span class="loader-dot" />
              <span class="loader-dot" />
              <span class="loader-dot" />
            </span>
            <span v-else>Зарегистрироваться</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue';
import { useAuth } from '../composables/useAuth';
import { registerSupervisor } from '../services/api';

const props = defineProps({
  modelValue: { type: Boolean, default: false },
});

const emit = defineEmits(['update:modelValue', 'register-success']);

const form = reactive({
  email: '',
  password: '',
  full_name: '',
  phone: '',
  organization_name: '',
  inn: '',
  address: '',
  kpp: '',
  bank_account: '',
  corr_account: '',
  bik: '',
});

const isSubmitting = ref(false);
const error = ref('');
const success = ref(false);
const touched = reactive({
  email: false,
  password: false,
  full_name: false,
  phone: false,
  organization_name: false,
  inn: false,
  kpp: false,
  bik: false,
  bank_account: false,
  corr_account: false,
});

const { initAuth, refreshUserRole } = useAuth();

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PHONE_REGEX = /^\+7\d{10}$/;
const INN_REGEX = /^\d{10}(\d{2})?$/;
const PASSWORD_SPECIAL_CHAR_REGEX = /[!@#$%^&*(),.?":{}|<>_\-+\[\]=\\/]/;

const validators = {
  email(value) {
    const trimmed = value.trim();
    if (!trimmed) return 'Введите email';
    if (!EMAIL_REGEX.test(trimmed)) return 'Некорректный формат email';
    return '';
  },
  password(value) {
    if (!value) return 'Введите пароль';
    if (value.length < 6 || value.length > 10) return 'Пароль от 6 до 10 символов';
    if (!/[A-Z]/.test(value)) return 'Добавьте хотя бы одну заглавную букву';
    if (!/\d/.test(value)) return 'Добавьте хотя бы одну цифру';
    if (!PASSWORD_SPECIAL_CHAR_REGEX.test(value)) return 'Добавьте хотя бы один спецсимвол';
    return '';
  },
  full_name(value) {
    if (!value.trim()) return 'Введите ФИО';
    return '';
  },
  phone(value) {
    const trimmed = value.trim();
    if (!trimmed) return 'Введите телефон';
    if (!PHONE_REGEX.test(trimmed)) return 'Формат телефона: +7 и 10 цифр';
    return '';
  },
  organization_name(value) {
    if (!value.trim()) return 'Введите название компании';
    return '';
  },
  inn(value) {
    const trimmed = value.trim();
    if (!trimmed) return 'Введите ИНН';
    if (!INN_REGEX.test(trimmed)) return 'ИНН должен содержать 10 или 12 цифр';
    return '';
  },
  kpp(value) {
    const trimmed = value.trim();
    if (!trimmed) return '';
    if (!/^\d{9}$/.test(trimmed)) return 'КПП должен содержать 9 цифр';
    return '';
  },
  bik(value) {
    const trimmed = value.trim();
    if (!trimmed) return '';
    if (!/^\d{9}$/.test(trimmed)) return 'БИК должен содержать 9 цифр';
    return '';
  },
  bank_account(value) {
    const trimmed = value.trim();
    if (!trimmed) return '';
    if (!/^\d{20}$/.test(trimmed)) return 'Р/с должен содержать 20 цифр';
    return '';
  },
  corr_account(value) {
    const trimmed = value.trim();
    if (!trimmed) return '';
    if (!/^\d{20}$/.test(trimmed)) return 'К/с должен содержать 20 цифр';
    return '';
  },
};

const fieldErrors = computed(() => ({
  email: validators.email(form.email),
  password: validators.password(form.password),
  full_name: validators.full_name(form.full_name),
  phone: validators.phone(form.phone),
  organization_name: validators.organization_name(form.organization_name),
  inn: validators.inn(form.inn),
  kpp: validators.kpp(form.kpp),
  bik: validators.bik(form.bik),
  bank_account: validators.bank_account(form.bank_account),
  corr_account: validators.corr_account(form.corr_account),
}));

const isFormValid = computed(
  () => Object.values(fieldErrors.value).every((value) => !value),
);

function markTouched(field) {
  touched[field] = true;
}

async function onSubmit() {
  touched.email = true;
  touched.password = true;
  touched.full_name = true;
  touched.phone = true;
  touched.organization_name = true;
  touched.inn = true;
  touched.kpp = true;
  touched.bik = true;
  touched.bank_account = true;
  touched.corr_account = true;

  if (!isFormValid.value) {
    error.value = 'Проверьте корректность заполнения формы.';
    return;
  }

  error.value = '';
  success.value = false;
  isSubmitting.value = true;

  try {
    const payload = {
      email: form.email.trim(),
      password: form.password,
      full_name: form.full_name.trim(),
      phone: form.phone.trim(),
      organization_name: form.organization_name.trim(),
      inn: form.inn.trim(),
      address: form.address.trim() || null,
      kpp: form.kpp.trim() || null,
      bank_account: form.bank_account.trim() || null,
      corr_account: form.corr_account.trim() || null,
      bik: form.bik.trim() || null,
    };

    await registerSupervisor(payload);

    // Подтягиваем токены из localStorage и определяем роль.
    initAuth();
    await refreshUserRole();

    success.value = true;
    emit('register-success');
    emit('update:modelValue', false);
  } catch (e) {
    const message = e?.response?.data?.detail || e?.message || 'Ошибка регистрации супервизора.';
    error.value = typeof message === 'string' ? message : 'Ошибка регистрации супервизора.';
  } finally {
    isSubmitting.value = false;
  }
}
</script>

