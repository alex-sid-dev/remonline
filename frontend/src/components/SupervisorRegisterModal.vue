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
            type="email"
            autocomplete="email"
            placeholder="owner@company.ru"
            required
          >
        </div>

        <div class="field">
          <label class="field-label" for="sup-password">Пароль</label>
          <input
            id="sup-password"
            v-model="form.password"
            class="field-input"
            type="password"
            autocomplete="new-password"
            placeholder="Придумайте сложный пароль"
            required
          >
        </div>

        <div class="field">
          <label class="field-label" for="sup-fullname">ФИО супервизора</label>
          <input
            id="sup-fullname"
            v-model="form.full_name"
            class="field-input"
            type="text"
            placeholder="Иванов Иван Иванович"
            required
          >
        </div>

        <div class="field">
          <label class="field-label" for="sup-phone">Телефон</label>
          <input
            id="sup-phone"
            v-model="form.phone"
            class="field-input"
            type="text"
            placeholder="+78008008000"
            required
          >
          <div class="hint">
            Формат: +7 и 10 цифр, например +78008008000
          </div>
        </div>

        <div class="field">
          <label class="field-label" for="sup-org-name">Название компании</label>
          <input
            id="sup-org-name"
            v-model="form.organization_name"
            class="field-input"
            type="text"
            placeholder="ООО «Ремонт-сервис»"
            required
          >
        </div>

        <div class="field">
          <label class="field-label" for="sup-inn">ИНН</label>
          <input
            id="sup-inn"
            v-model="form.inn"
            class="field-input"
            type="text"
            placeholder="1234567890"
            required
          >
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
              type="text"
            >
          </div>
          <div class="col">
            <label class="field-label" for="sup-bik">БИК (необязательно)</label>
            <input
              id="sup-bik"
              v-model="form.bik"
              class="field-input"
              type="text"
            >
          </div>
        </div>

        <div class="field row">
          <div class="col">
            <label class="field-label" for="sup-bank-account">Р/с (необязательно)</label>
            <input
              id="sup-bank-account"
              v-model="form.bank_account"
              class="field-input"
              type="text"
            >
          </div>
          <div class="col">
            <label class="field-label" for="sup-corr-account">К/с (необязательно)</label>
            <input
              id="sup-corr-account"
              v-model="form.corr_account"
              class="field-input"
              type="text"
            >
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
            :disabled="isSubmitting"
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
import { reactive, ref } from 'vue';
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

const { initAuth, refreshUserRole } = useAuth();

async function onSubmit() {
  error.value = '';
  success.value = false;
  isSubmitting.value = true;

  try {
    const payload = {
      email: form.email,
      password: form.password,
      full_name: form.full_name,
      phone: form.phone,
      organization_name: form.organization_name,
      inn: form.inn,
      address: form.address || null,
      kpp: form.kpp || null,
      bank_account: form.bank_account || null,
      corr_account: form.corr_account || null,
      bik: form.bik || null,
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

