<template>
  <div>
    <div class="table-header">
      <div class="table-meta">
        Сотрудники
      </div>
      <button
        v-if="canCreateEmployees"
        class="btn btn-primary"
        type="button"
        @click="$emit('create-employee')"
      >
        Новый сотрудник
      </button>
    </div>
    <table v-if="employees.length">
      <thead>
        <tr>
          <th>ФИО</th>
          <th>Телефон</th>
          <th>Должность</th>
          <th>Зарплата</th>
          <th>% от прибыли</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="e in employees"
          :key="e.uuid"
          :style="canManageEmployees ? 'cursor: pointer' : ''"
          @click="canManageEmployees && $emit('edit-employee', e)"
        >
          <td>{{ e.full_name }}</td>
          <td>{{ e.phone || '—' }}</td>
          <td>{{ e.position }}</td>
          <td>{{ e.salary != null ? e.salary : '—' }}</td>
          <td>{{ e.profit_percent != null ? e.profit_percent + '%' : '—' }}</td>
        </tr>
      </tbody>
    </table>
    <div v-else class="empty-state">
      Сотрудников пока нет.
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { canManageEmployees as canManageEmployeesFn } from '../constants/roles';

const props = defineProps({
  employees: { type: Array, required: true },
  userRole: { type: String, required: true },
});

defineEmits(['create-employee', 'edit-employee']);

const canManageEmployees = computed(
  () => canManageEmployeesFn(props.userRole),
);
const canCreateEmployees = computed(
  () => canManageEmployeesFn(props.userRole),
);
</script>
