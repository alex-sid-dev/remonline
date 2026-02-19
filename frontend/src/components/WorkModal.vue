<template>
  <div
    v-if="open"
    class="modal-backdrop"
    @click="$emit('close')"
  >
    <div class="modal" @click.stop>
      <div class="login-card">
        <div class="field-label">Добавить работу</div>
        <div class="field">
          <label class="field-label" for="mw-title">Название</label>
          <input id="mw-title" v-model="form.title" class="field-input" type="text">
        </div>
        <div class="field">
          <label class="field-label" for="mw-price">Цена</label>
          <input
            id="mw-price"
            v-model.number="form.price"
            class="field-input"
            type="number"
            step="0.01"
            @keydown="blockNonNumeric"
          >
        </div>
        <div class="field">
          <label class="field-label" for="mw-desc">Описание</label>
          <input id="mw-desc" v-model="form.description" class="field-input" type="text">
        </div>
        <div class="field">
          <button class="btn btn-primary" type="button" @click="submit">Добавить работу</button>
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
});

const emit = defineEmits(['close', 'submit']);

const form = reactive({ title: '', price: null, description: '' });

watch(() => props.open, (val) => {
  if (val) Object.assign(form, { title: '', price: null, description: '' });
});

function submit() {
  emit('submit', { ...form });
}
</script>
