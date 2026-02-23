<template>
  <div>
    <div class="table-header">
      <div class="table-meta">
        Бренды устройств
      </div>
      <button
        v-if="canManage"
        class="btn btn-primary"
        type="button"
        @click="$emit('create-brand')"
      >
        Новый бренд
      </button>
    </div>
    <div v-if="brands.length" class="order-detail-table-wrap">
      <table>
        <thead>
          <tr>
            <th>Название</th>
            <th v-if="canManage">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="b in brands"
            :key="b.uuid"
          >
            <td>{{ b.name }}</td>
            <td v-if="canManage">
              <button
                class="btn btn-ghost"
                type="button"
                @click="$emit('edit-brand', b)"
              >
                Редактировать
              </button>
              <button
                class="btn btn-ghost"
                type="button"
                @click="$emit('delete-brand', b)"
              >
                Удалить
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else class="empty-state">
      Брендов пока нет. Добавьте бренды для выбора при создании устройств.
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { canManageEmployees } from '../constants/roles';

const props = defineProps({
  brands: { type: Array, required: true },
  userRole: { type: String, required: true },
});

defineEmits(['create-brand', 'edit-brand', 'delete-brand']);

const canManage = computed(() => canManageEmployees(props.userRole));
</script>
