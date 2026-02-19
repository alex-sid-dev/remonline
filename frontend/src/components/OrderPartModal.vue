<template>
  <div
    v-if="open"
    class="modal-backdrop"
    @click="$emit('close')"
  >
    <div class="modal" @click.stop>
      <div class="login-card">
        <div class="field-label">Добавить запчасть</div>
        <div class="field">
          <label class="field-label">Запчасть</label>
          <div class="field-row">
            <input
              v-model="searchQuery"
              class="field-input"
              type="text"
              placeholder="Поиск по названию или SKU (от 3 символов)"
              @input="handleSearchInput"
              @focus="handleSearchInput"
            >
          </div>
          <div v-if="suggestionsOpen && searchQuery.length >= 3" class="autocomplete-list">
            <button
              v-for="p in filteredParts"
              :key="p.uuid"
              type="button"
              class="autocomplete-item"
              @click="selectPart(p)"
            >
              <div class="autocomplete-item-main">{{ p.name }}</div>
              <div class="autocomplete-item-sub">{{ p.sku || 'без SKU' }}</div>
            </button>
            <div v-if="!filteredParts.length" class="autocomplete-empty">Ничего не найдено</div>
          </div>
        </div>
        <div class="field">
          <label class="field-label">Кол-во</label>
          <input
            v-model.number="form.qty"
            class="field-input"
            type="number"
            min="1"
            @keydown="blockNonNumeric"
          >
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
          <button class="btn btn-primary" type="button" @click="submit">Добавить запчасть</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue';
import { blockNonNumeric } from '../utils/inputHelpers';

const props = defineProps({
  open: { type: Boolean, required: true },
  parts: { type: Array, required: true },
});

const emit = defineEmits(['close', 'submit']);

const form = reactive({ part_uuid: '', qty: 1, price: null });
const searchQuery = ref('');
const suggestionsOpen = ref(false);

watch(() => props.open, (val) => {
  if (val) {
    Object.assign(form, { part_uuid: '', qty: 1, price: null });
    searchQuery.value = '';
    suggestionsOpen.value = false;
  }
});

const filteredParts = computed(() => {
  const q = searchQuery.value.trim().toLowerCase();
  if (q.length < 3) return props.parts;
  return props.parts.filter((p) => {
    const name = (p.name || '').toLowerCase();
    const sku = (p.sku || '').toLowerCase();
    return name.includes(q) || sku.includes(q);
  });
});

function handleSearchInput() {
  suggestionsOpen.value = searchQuery.value.trim().length >= 3;
  form.part_uuid = '';
}

function selectPart(part) {
  form.part_uuid = part.uuid;
  searchQuery.value = `${part.name} (${part.sku || 'без SKU'})`;
  suggestionsOpen.value = false;
}

function submit() {
  emit('submit', { ...form });
}
</script>
