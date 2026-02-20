<template>
  <div
    v-if="open"
    class="modal-backdrop"
    @click="$emit('close')"
  >
    <div class="modal modal--wide" @click.stop>
      <div class="login-card">
        <div class="field">
          <div class="field-label">
            {{ hasOrganization ? 'Реквизиты организации' : 'Ввести данные организации' }}
          </div>
        </div>
        <div class="field">
          <label class="field-label">Название</label>
          <input
            v-model="form.name"
            class="field-input"
            type="text"
            placeholder="ООО «Пример»"
          >
        </div>
        <div class="field">
          <label class="field-label">ИНН</label>
          <input
            v-model="form.inn"
            class="field-input"
            type="text"
            placeholder="7707123456"
          >
        </div>
        <div class="field">
          <label class="field-label">Адрес</label>
          <input
            v-model="form.address"
            class="field-input"
            type="text"
            placeholder="г. Москва, ул. Примерная, д. 1"
          >
        </div>
        <div class="field">
          <label class="field-label">КПП</label>
          <input
            v-model="form.kpp"
            class="field-input"
            type="text"
            placeholder="770701001"
          >
        </div>
        <div class="field">
          <label class="field-label">Р/с (расчётный счёт)</label>
          <input
            v-model="form.bank_account"
            class="field-input"
            type="text"
            placeholder="40702810000000000000"
          >
        </div>
        <div class="field">
          <label class="field-label">К/с (корр. счёт)</label>
          <input
            v-model="form.corr_account"
            class="field-input"
            type="text"
            placeholder="30101810000000000000"
          >
        </div>
        <div class="field">
          <label class="field-label">БИК</label>
          <input
            v-model="form.bik"
            class="field-input"
            type="text"
            placeholder="044525225"
          >
        </div>
        <div v-if="message" class="hint" :class="{ error: messageError }">
          {{ message }}
        </div>
        <div class="org-modal-actions">
          <button
            class="btn btn-primary"
            type="button"
            :disabled="saving"
            @click="submit"
          >
            {{ saving ? 'Сохранение…' : 'Сохранить' }}
          </button>
          <button
            v-if="hasOrganization"
            class="btn btn-secondary"
            type="button"
            :disabled="saving"
            @click="remove"
          >
            Удалить реквизиты
          </button>
          <button
            class="btn btn-secondary"
            type="button"
            :disabled="saving"
            @click="$emit('close')"
          >
            Закрыть
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, watch } from 'vue';
import { getOrganization, createOrganization, updateOrganization, deleteOrganization } from '../services/api';
import { extractErrorMessage } from '../utils/errorHelpers';

const props = defineProps({
  open: { type: Boolean, required: true },
});

const emit = defineEmits(['close', 'saved']);

const form = reactive({
  name: '',
  inn: '',
  address: '',
  kpp: '',
  bank_account: '',
  corr_account: '',
  bik: '',
});

const hasOrganization = ref(false);
const saving = ref(false);
const message = ref('');
const messageError = ref(false);

async function load() {
  hasOrganization.value = false;
  Object.assign(form, {
    name: '',
    inn: '',
    address: '',
    kpp: '',
    bank_account: '',
    corr_account: '',
    bik: '',
  });
  try {
    const data = await getOrganization();
    hasOrganization.value = true;
    Object.assign(form, {
      name: data.name ?? '',
      inn: data.inn ?? '',
      address: data.address ?? '',
      kpp: data.kpp ?? '',
      bank_account: data.bank_account ?? '',
      corr_account: data.corr_account ?? '',
      bik: data.bik ?? '',
    });
  } catch (e) {
    if (e?.response?.status === 404) {
      hasOrganization.value = false;
    } else {
      message.value = extractErrorMessage(e, 'Не удалось загрузить реквизиты.');
      messageError.value = true;
    }
  }
}

watch(() => props.open, (val) => {
  if (val) {
    message.value = '';
    messageError.value = false;
    load();
  }
});

async function submit() {
  message.value = '';
  messageError.value = false;
  saving.value = true;
  try {
    const payload = {
      name: form.name?.trim() ?? '',
      inn: form.inn?.trim() ?? '',
      address: form.address?.trim() || null,
      kpp: form.kpp?.trim() || null,
      bank_account: form.bank_account?.trim() || null,
      corr_account: form.corr_account?.trim() || null,
      bik: form.bik?.trim() || null,
    };
    if (hasOrganization.value) {
      await updateOrganization(payload);
      message.value = 'Реквизиты сохранены';
    } else {
      await createOrganization(payload);
      hasOrganization.value = true;
      message.value = 'Реквизиты созданы';
    }
    messageError.value = false;
    emit('saved');
  } catch (e) {
    message.value = extractErrorMessage(e, 'Ошибка сохранения реквизитов.');
    messageError.value = true;
  } finally {
    saving.value = false;
  }
}

async function remove() {
  if (!window.confirm('Удалить реквизиты организации? Они перестанут отображаться в квитанциях и актах.')) return;
  message.value = '';
  messageError.value = false;
  saving.value = true;
  try {
    await deleteOrganization();
    hasOrganization.value = false;
    Object.assign(form, { name: '', inn: '', address: '', kpp: '', bank_account: '', corr_account: '', bik: '' });
    message.value = 'Реквизиты удалены';
    emit('saved');
  } catch (e) {
    message.value = extractErrorMessage(e, 'Ошибка удаления.');
    messageError.value = true;
  } finally {
    saving.value = false;
  }
}
</script>

<style scoped>
.org-modal-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}
.hint.error {
  color: var(--color-danger, #c00);
}
.modal--wide {
  max-width: 420px;
}
</style>
