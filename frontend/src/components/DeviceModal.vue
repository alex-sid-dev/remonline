<template>
  <div
    v-if="open"
    class="modal-backdrop"
    @click="$emit('close')"
  >
    <div class="modal" @click.stop>
      <div class="login-card">
        <div class="field">
          <div class="field-label">Новое устройство</div>
        </div>
        <div class="field">
          <label class="field-label" for="modal-device-type">Тип устройства</label>
          <select id="modal-device-type" v-model="form.type_uuid" class="field-input">
            <option disabled value="">Выберите тип</option>
            <option v-for="dt in deviceTypes" :key="dt.uuid" :value="dt.uuid">
              {{ dt.name }}
            </option>
          </select>
        </div>
        <div class="field">
          <label class="field-label" for="modal-device-brand">Бренд</label>
          <input id="modal-device-brand" v-model="form.brand" class="field-input" type="text">
        </div>
        <div class="field">
          <label class="field-label" for="modal-device-model">Модель</label>
          <input id="modal-device-model" v-model="form.model" class="field-input" type="text">
        </div>
        <div class="field">
          <label class="field-label" for="modal-device-serial">Серийный номер</label>
          <input id="modal-device-serial" v-model="form.serial_number" class="field-input" type="text">
        </div>
        <div class="field">
          <label class="field-label" for="modal-device-description">Внешнее состояние</label>
          <input id="modal-device-description" v-model="form.description" class="field-input" type="text">
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

const props = defineProps({
  open: { type: Boolean, required: true },
  deviceTypes: { type: Array, required: true },
  initialData: { type: Object, default: null },
});

const emit = defineEmits(['close', 'submit']);

const form = reactive({ type_uuid: '', brand: '', model: '', serial_number: '', description: '' });

watch(() => props.open, (val) => {
  if (val && props.initialData) {
    Object.assign(form, {
      type_uuid: props.initialData.type_uuid || '',
      brand: props.initialData.brand || '',
      model: props.initialData.model || '',
      serial_number: props.initialData.serial_number || '',
      description: props.initialData.description || '',
    });
  } else if (val) {
    Object.assign(form, { type_uuid: '', brand: '', model: '', serial_number: '', description: '' });
  }
});

const formValid = computed(() => !!form.type_uuid && !!form.brand?.trim() && !!form.model?.trim());

function submit() {
  emit('submit', { ...form });
}
</script>
