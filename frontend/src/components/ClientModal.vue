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

        <!-- Телефон (обязательно) -->
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

          <div
            v-if="matchingClients.length"
            class="autocomplete-list mt-8"
          >
            <div class="autocomplete-empty">
              Найдены клиенты с таким телефоном:
            </div>
            <button
              v-for="c in matchingClients"
              :key="c.uuid"
              type="button"
              class="autocomplete-item"
              @click="pickExistingClient(c)"
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

        <!-- ФИО (обязательно) -->
        <div class="field">
          <label class="field-label" for="modal-client-name">ФИО *</label>
          <input
            id="modal-client-name"
            v-model="form.full_name"
            class="field-input"
            type="text"
            placeholder="ФИО клиента"
          >
        </div>

        <!-- Адрес (необязательно) -->
        <div class="field">
          <label class="field-label" for="modal-client-address">Адрес</label>
          <input id="modal-client-address" v-model="form.address" class="field-input" type="text">
        </div>

        <!-- Email (необязательно) -->
        <div class="field">
          <label class="field-label" for="modal-client-email">Email</label>
          <input id="modal-client-email" v-model="form.email" class="field-input" type="email">
        </div>

        <!-- Telegram (необязательно) -->
        <div class="field">
          <label class="field-label" for="modal-client-telegram">Telegram</label>
          <input id="modal-client-telegram" v-model="form.telegram_nick" class="field-input" type="text">
        </div>

        <!-- Комментарий (как и раньше, опционально) -->
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
  existingClients: { type: Array, default: () => [] },
});

const emit = defineEmits(['close', 'submit']);

const form = reactive({
  uuid: null,
  full_name: '',
  phone: '',
  email: '',
  telegram_nick: '',
  comment: '',
  address: '',
});

watch(() => props.open, (val) => {
  if (val) {
    Object.assign(form, {
      uuid: null,
      full_name: '',
      phone: '',
      email: '',
      telegram_nick: '',
      comment: '',
      address: '',
    });
  }
});

const formValid = computed(() => form.full_name.trim().length > 0 && isValidPhone(form.phone));

const matchingClients = computed(() => {
  const raw = (form.phone || '').replace(/\D/g, '');
  if (raw.length < 5) return [];
  return props.existingClients.filter((c) => {
    const phone = (c.phone || '').replace(/\D/g, '');
    return phone.includes(raw);
  });
});

function pickExistingClient(client) {
  Object.assign(form, {
    uuid: client.uuid || null,
    full_name: client.full_name || '',
    phone: client.phone || '',
    email: client.email || '',
    telegram_nick: client.telegram_nick || '',
    comment: client.comment || '',
    address: client.address || '',
  });
}

function submit() {
  emit('submit', { ...form });
}
</script>
