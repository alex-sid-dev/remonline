<template>
  <div
    v-if="open"
    class="modal-backdrop"
    @click="$emit('close')"
  >
    <div class="modal" @click.stop>
      <div class="login-card">
        <div class="field">
          <div class="field-label">Новый клиент</div>
        </div>
        <div class="field">
          <label class="field-label" for="modal-client-name">Имя *</label>
          <input
            id="modal-client-name"
            v-model="form.full_name"
            class="field-input"
            type="text"
            placeholder="ФИО клиента"
          >
        </div>
        <div class="field">
          <label class="field-label" for="modal-client-phone">Телефон *</label>
          <input
            id="modal-client-phone"
            v-model="form.phone"
            class="field-input"
            :class="{ 'field-input--error': form.phone && !isValidPhone(form.phone) }"
            type="text"
            placeholder="+78008008000"
          >
          <div v-if="form.phone && !isValidPhone(form.phone)" class="error">
            Формат: +7 и 10 цифр, например +78008008000
          </div>
          <div v-else class="hint">
            Формат: +7 и 10 цифр, например +78008008000
          </div>
        </div>
        <div class="field">
          <label class="field-label" for="modal-client-email">Email</label>
          <input id="modal-client-email" v-model="form.email" class="field-input" type="email">
        </div>
        <div class="field">
          <label class="field-label" for="modal-client-telegram">Telegram</label>
          <input id="modal-client-telegram" v-model="form.telegram_nick" class="field-input" type="text">
        </div>
        <div class="field">
          <label class="field-label" for="modal-client-address">Адрес</label>
          <input id="modal-client-address" v-model="form.address" class="field-input" type="text">
        </div>
        <div class="field">
          <label class="field-label" for="modal-client-comment">Комментарий</label>
          <input id="modal-client-comment" v-model="form.comment" class="field-input" type="text">
        </div>
        <div class="field">
          <button
            class="btn btn-primary"
            type="button"
            :disabled="!formValid"
            @click="submit"
          >
            Сохранить
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, watch } from 'vue';
import { isValidPhone } from '../utils/inputHelpers';

const props = defineProps({
  open: { type: Boolean, required: true },
});

const emit = defineEmits(['close', 'submit']);

const form = reactive({
  full_name: '', phone: '', email: '', telegram_nick: '', comment: '', address: '',
});

watch(() => props.open, (val) => {
  if (val) {
    Object.assign(form, { full_name: '', phone: '', email: '', telegram_nick: '', comment: '', address: '' });
  }
});

const formValid = computed(() => form.full_name.trim().length > 0 && isValidPhone(form.phone));

function submit() {
  emit('submit', { ...form });
}
</script>
