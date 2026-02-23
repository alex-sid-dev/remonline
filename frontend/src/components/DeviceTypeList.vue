<template>
  <div>
    <div class="table-header">
      <div class="table-meta">
        Типы устройств
      </div>
      <button
        v-if="canManage"
        class="btn btn-primary"
        type="button"
        @click="$emit('create-device-type')"
      >
        Новый тип
      </button>
    </div>
    <div v-if="deviceTypes.length" class="order-detail-table-wrap">
      <table>
        <thead>
          <tr>
            <th>Название</th>
            <th>Описание</th>
            <th v-if="canManage">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="dt in deviceTypes"
            :key="dt.uuid"
          >
            <td>{{ dt.name }}</td>
            <td>{{ dt.description || '—' }}</td>
            <td v-if="canManage">
              <button
                class="btn btn-ghost"
                type="button"
                @click="$emit('edit-device-type', dt)"
              >
                Редактировать
              </button>
              <button
                class="btn btn-ghost"
                type="button"
                @click="$emit('delete-device-type', dt)"
              >
                Удалить
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else class="empty-state">
      Типов устройств пока нет. Добавьте типы для выбора при создании заказов (телефон, ноутбук и т.д.).
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { canManageEmployees } from '../constants/roles';

const props = defineProps({
  deviceTypes: { type: Array, required: true },
  userRole: { type: String, required: true },
});

defineEmits(['create-device-type', 'edit-device-type', 'delete-device-type']);

const canManage = computed(() => canManageEmployees(props.userRole));
</script>
