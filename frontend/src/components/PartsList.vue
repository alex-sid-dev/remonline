<template>
  <div>
    <div class="table-header">
      <div class="table-meta">
        Запчасти: общий список номенклатуры.
        <div class="field-row mt-16">
          <input
            v-model="partsSearch"
            class="field-input"
            type="text"
            placeholder="Поиск по названию или SKU"
            @input="onSearchInput"
          >
        </div>
      </div>
      <button
        v-if="canManageParts(props.userRole)"
        class="btn btn-primary"
        type="button"
        @click="$emit('create-part')"
      >
        Новая запчасть
      </button>
    </div>
    <div v-if="parts.length">
      <table>
        <thead>
          <tr>
            <th>Название</th>
            <th>SKU</th>
            <th>Цена</th>
            <th>Остаток</th>
            <th v-if="canManageParts(props.userRole)">
              Действия
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="p in filteredParts"
            :key="p.uuid"
          >
            <td>{{ p.name }}</td>
            <td>{{ p.sku || '—' }}</td>
            <td>{{ p.price ?? '—' }}</td>
            <td>{{ p.stock_qty ?? '—' }}</td>
            <td
              v-if="canManageParts(props.userRole)"
            >
              <button
                class="btn btn-ghost"
                type="button"
                @click="$emit('edit-part', p)"
              >
                Редактировать
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else class="empty-state">
      Запчастей пока нет.
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { canManageParts } from '../constants/roles';
import { debounce } from '../utils/debounce';

const props = defineProps({
  parts: { type: Array, required: true },
  userRole: { type: String, required: true },
});

defineEmits(['create-part', 'edit-part']);

const partsSearch = ref('');
const debouncedSearch = ref('');

const applySearch = debounce((val) => {
  debouncedSearch.value = val;
}, 300);

function onSearchInput() {
  applySearch(partsSearch.value);
}

const filteredParts = computed(() => {
  const q = debouncedSearch.value.trim().toLowerCase();
  if (!q) return props.parts;
  return props.parts.filter((p) => {
    const name = (p.name || '').toLowerCase();
    const sku = (p.sku || '').toLowerCase();
    return name.includes(q) || sku.includes(q);
  });
});
</script>
