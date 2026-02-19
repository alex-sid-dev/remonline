<template>
  <div
    v-if="open"
    class="modal-backdrop"
    @click="$emit('close')"
  >
    <div class="modal" @click.stop>
      <div class="login-card">
        <div class="field">
          <div class="field-label">{{ editMode ? 'Редактирование запчасти' : 'Новая запчасть' }}</div>
        </div>
        <div class="field">
          <label class="field-label">Название</label>
          <input v-model="form.name" class="field-input" type="text">
        </div>
        <div class="field">
          <label class="field-label">SKU</label>
          <input v-model="form.sku" class="field-input" type="text">
        </div>
        <div class="field">
          <label class="field-label">Цена</label>
          <input
            v-model.number="form.price"
            class="field-input"
            type="number"
            step="0.01"
            @keydown="blockNonNumeric"
          >
        </div>
        <div class="field">
          <label class="field-label">Остаток</label>
          <input
            v-model.number="form.stock_qty"
            class="field-input"
            type="number"
            min="0"
            @keydown="blockNonNumeric"
          >
        </div>
        <div class="field">
          <button class="btn btn-primary" type="button" @click="submit">Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue';
import { blockNonNumeric } from '../utils/inputHelpers';

const props = defineProps({
  open: { type: Boolean, required: true },
  editMode: { type: Boolean, default: false },
  initialData: { type: Object, default: null },
});

const emit = defineEmits(['close', 'submit']);

const form = reactive({ name: '', sku: '', price: null, stock_qty: null });

watch(() => props.open, (val) => {
  if (val && props.initialData) {
    Object.assign(form, {
      name: props.initialData.name || '',
      sku: props.initialData.sku || '',
      price: props.initialData.price ?? null,
      stock_qty: props.initialData.stock_qty ?? null,
    });
  } else if (val) {
    Object.assign(form, { name: '', sku: '', price: null, stock_qty: null });
  }
});

function submit() {
  emit('submit', { ...form });
}
</script>
