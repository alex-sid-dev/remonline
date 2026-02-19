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
        @submit.prevent="onLogin"
      >
        <div class="field">
          <label class="field-label" for="modal-email">Email</label>
          <input
            id="modal-email"
            v-model="email"
            class="field-input"
            type="email"
            autocomplete="username"
            placeholder="admin@admin.ru"
            required
          >
        </div>

        <div class="field">
          <label class="field-label" for="modal-password">Пароль</label>
          <input
            id="modal-password"
            v-model="password"
            class="field-input"
            type="password"
            autocomplete="current-password"
            placeholder="••••••••"
            required
          >
        </div>

        <div class="hint">
          Данные используются только для получения токенов доступа.
        </div>

        <div v-if="loginError" class="error">
          {{ loginError }}
        </div>
        <div v-if="loginSuccess" class="success">
          Вход выполнен.
        </div>

        <div class="field">
          <button
            class="btn btn-primary"
            type="submit"
            :disabled="isLoggingIn"
          >
            <span v-if="isLoggingIn" class="loader">
              <span class="loader-dot" />
              <span class="loader-dot" />
              <span class="loader-dot" />
            </span>
            <span v-else>Войти</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { useAuth } from '../composables/useAuth';

defineProps({
  modelValue: { type: Boolean, default: false },
});

const emit = defineEmits(['update:modelValue', 'login-success']);

const { email, password, isLoggingIn, loginError, loginSuccess, handleLogin } = useAuth();

async function onLogin() {
  const ok = await handleLogin();
  if (ok) {
    emit('update:modelValue', false);
    emit('login-success');
  }
}
</script>
