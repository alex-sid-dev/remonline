<template>
  <div class="order-detail-page">
    <div v-if="orderDetails.loading" class="empty-state">
      Загрузка деталей заказа…
    </div>

    <div v-else class="order-detail-columns">
      <!-- Column 1: client, device, editable fields -->
      <aside class="order-detail-col order-detail-col--left">
        <div class="order-info-card">
          <div class="order-info-row">
            <span class="order-info-label">ФИО клиента</span>
            <span class="order-info-value">{{ orderDetails.data.client.full_name }}</span>
          </div>
          <div class="order-info-row">
            <span class="order-info-label">Телефон</span>
            <span class="order-info-value">{{ orderDetails.data.client.phone || '—' }}</span>
          </div>
          <div class="order-info-row">
            <span class="order-info-label">Адрес</span>
            <span class="order-info-value">{{ orderDetails.data.client.address || '—' }}</span>
          </div>
          <div class="order-info-row">
            <span class="order-info-label">Бренд</span>
            <span class="order-info-value">{{ orderDetails.data.device.brand || '—' }}</span>
          </div>
          <div class="order-info-row">
            <span class="order-info-label">Модель</span>
            <span class="order-info-value">{{ orderDetails.data.device.model || '—' }}</span>
          </div>
          <div class="order-info-row">
            <span class="order-info-label">Серийный номер</span>
            <span class="order-info-value">{{ orderDetails.data.device.serial_number || '—' }}</span>
          </div>
          <div class="order-info-row">
            <span class="order-info-label">Менеджер</span>
            <span class="order-info-value">
              {{ orderDetails.data.creator?.full_name || '—' }}
            </span>
          </div>
          <div class="order-info-row">
            <span class="order-info-label">Инженер</span>
            <span class="order-info-value">
              {{ orderDetails.data.assigned_employee?.full_name || '—' }}
            </span>
          </div>
        </div>
        <div class="login-card mt-16">
          <div
            v-if="userRole === 'supervisor' || userRole === 'admin'"
            class="field"
          >
            <label class="field-label" for="details-manager">Менеджер</label>
            <select
              id="details-manager"
              v-model="detailsManagerUuid"
              class="field-input"
            >
              <option :value="null">Не назначен</option>
              <option
                v-for="e in employees.filter((e) => ['manager', 'admin', 'supervisor'].includes(e.position))"
                :key="e.uuid"
                :value="e.uuid"
              >
                {{ e.full_name }}
              </option>
            </select>
          </div>
          <div
            v-if="userRole === 'supervisor' || userRole === 'admin'"
            class="field"
          >
            <label class="field-label" for="details-engineer">Инженер</label>
            <select
              id="details-engineer"
              v-model="detailsEngineerUuid"
              class="field-input"
            >
              <option :value="null">Не назначен</option>
              <option
                v-for="e in engineerOptions"
                :key="e.uuid"
                :value="e.uuid"
              >
                {{ e.full_name }}
              </option>
            </select>
          </div>
          <div class="field">
            <label class="field-label" for="details-status">Статус</label>
            <select
              id="details-status"
              v-model="orderDetails.data.status"
              class="field-input"
            >
              <option
                v-for="s in availableStatuses"
                :key="s.value"
                :value="s.value"
              >
                {{ s.label }}
              </option>
            </select>
          </div>
          <div class="field">
            <label class="field-label" for="details-price">Цена (авто)</label>
            <input
              id="details-price"
              :value="orderCalculatedPrice"
              class="field-input"
              type="number"
              step="0.01"
              disabled
            >
          </div>
          <div class="field">
            <label class="field-label" for="details-problem">Неисправность</label>
            <input
              id="details-problem"
              v-model="orderDetails.data.problem_description"
              class="field-input"
              type="text"
            >
          </div>
          <button
            class="btn btn-primary"
            type="button"
            @click="saveOrderDetails"
          >
            Сохранить изменения
          </button>
        </div>
      </aside>

      <!-- Column 2: works and parts -->
      <div class="order-detail-col order-detail-col--center">
        <div class="order-detail-block">
          <div class="order-detail-block-head">
            <span class="order-detail-block-title">Работы</span>
            <button
              class="btn btn-primary"
              type="button"
              @click="$emit('add-work')"
            >
              + Добавить работу
            </button>
          </div>
          <div v-if="orderDetails.data.works.length" class="order-detail-table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Название</th>
                  <th>Исполнитель</th>
                  <th>Кол-во</th>
                  <th>Цена (за всё)</th>
                  <th>Описание</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                <template
                  v-for="w in orderDetails.data.works"
                  :key="w.uuid"
                >
                  <tr
                    class="cursor-pointer"
                    @click="startEditWork(w)"
                  >
                    <td>{{ w.title }}</td>
                    <td>{{ w.employee?.full_name || '—' }}</td>
                    <td>{{ w.qty || 1 }}</td>
                    <td>{{ (w.price || 0) * (w.qty || 1) || '—' }}</td>
                    <td>{{ w.description || '—' }}</td>
                    <td class="text-right">
                      <button
                        class="btn btn-ghost"
                        type="button"
                        @click.stop="decrementWork(w)"
                      >
                        −
                      </button>
                    </td>
                  </tr>
                  <tr v-if="editingWork?.uuid === w.uuid">
                    <td colspan="6" class="inline-form-cell">
                      <div class="login-card inline-form-wrapper">
                        <div class="field">
                          <label class="field-label">Название</label>
                          <input
                            v-model="editingWork.title"
                            class="field-input"
                            type="text"
                          >
                        </div>
                        <div class="field">
                          <label class="field-label">Исполнитель</label>
                          <select
                            v-model="editingWork.employee_uuid"
                            class="field-input"
                          >
                            <option :value="null">Не назначен</option>
                            <option
                              v-for="e in workEngineerOptions"
                              :key="e.uuid"
                              :value="e.uuid"
                            >
                              {{ e.full_name }}
                            </option>
                          </select>
                        </div>
                        <div class="field">
                          <label class="field-label">Кол-во</label>
                          <input
                            v-model.number="editingWork.qty"
                            class="field-input"
                            type="number"
                            min="1"
                            @keydown="blockNonNumeric"
                          >
                        </div>
                        <div class="field">
                          <label class="field-label">Цена</label>
                          <input
                            v-model.number="editingWork.price"
                            class="field-input"
                            type="number"
                            step="0.01"
                            @keydown="blockNonNumeric"
                          >
                        </div>
                        <div class="field">
                          <label class="field-label">Описание</label>
                          <input
                            v-model="editingWork.description"
                            class="field-input"
                            type="text"
                          >
                        </div>
                        <div class="field-row gap-8">
                          <button
                            class="btn btn-primary"
                            type="button"
                            @click="saveEditWork"
                          >
                            Сохранить
                          </button>
                          <button
                            class="btn btn-ghost"
                            type="button"
                            @click="editingWork = null"
                          >
                            Отмена
                          </button>
                        </div>
                      </div>
                    </td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>
          <div v-else class="empty-state">
            Работ пока нет.
          </div>
        </div>
        <div class="order-detail-block">
          <div class="order-detail-block-head">
            <span class="order-detail-block-title">Запчасти</span>
            <button
              class="btn btn-primary"
              type="button"
              @click="$emit('add-part')"
            >
              + Добавить запчасть
            </button>
          </div>
          <div v-if="orderDetails.data.parts.length" class="order-detail-table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Название</th>
                  <th>SKU</th>
                  <th>Кол-во</th>
                  <th>Цена (за всё)</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="p in orderDetails.data.parts"
                  :key="p.id"
                >
                  <td>{{ p.part_info?.name || '—' }}</td>
                  <td>{{ p.part_info?.sku || '—' }}</td>
                  <td>{{ p.qty }}</td>
                  <td>{{ (p.price ?? p.part_info?.price ?? 0) * (p.qty || 0) || '—' }}</td>
                  <td class="text-right">
                    <button
                      class="btn btn-ghost"
                      type="button"
                      @click.stop="decrementOrderPart(p)"
                    >
                      −
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
      </div>

      <!-- Column 3: comments chat -->
      <aside class="order-detail-col order-detail-col--right">
        <div class="order-comments-chat">
          <div class="order-comments-title">Комментарии</div>
          <div class="order-comments-list" ref="commentsListRef">
            <div
              v-for="c in (orderDetails.data.comments || [])"
              :key="c.id"
              class="order-comment-bubble"
            >
              <div class="order-comment-text">{{ c.text }}</div>
              <div class="order-comment-meta">
                {{ formatCommentDate(c.created_at) }}
                <span v-if="c.creator?.full_name"> · {{ c.creator.full_name }}</span>
              </div>
            </div>
            <div v-if="!(orderDetails.data.comments || []).length" class="empty-state">
              Нет комментариев.
            </div>
          </div>
          <div class="order-comments-input-row">
            <input
              v-model="newCommentText"
              class="field-input order-comments-input"
              type="text"
              placeholder="Написать комментарий…"
              @keydown.enter.prevent="sendOrderComment"
            >
            <button
              class="btn btn-primary"
              type="button"
              @click="sendOrderComment"
            >
              Отправить
            </button>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue';
import { ORDER_STATUS_OPTIONS, formatCommentDate } from '../utils/orderHelpers';
import { blockNonNumeric } from '../utils/inputHelpers';
import { extractErrorMessage } from '../utils/errorHelpers';
import {
  updateOrder,
  getOrderDetails,
  createOrderComment,
  updateWork,
  deleteWork,
  updateOrderPart,
  deleteOrderPart,
  getParts,
  getOrderActHtml,
  getOrderReceiptHtml,
} from '../services/api';

const props = defineProps({
  orderDetails: { type: Object, required: true },
  employees: { type: Array, required: true },
  parts: { type: Array, required: true },
  userRole: { type: String, required: true },
});

const emit = defineEmits(['add-work', 'add-part', 'error', 'update:parts', 'update:order']);

const detailsManagerUuid = ref(null);
const detailsEngineerUuid = ref(null);
const newCommentText = ref('');
const commentsListRef = ref(null);
const editingWork = ref(null);

watch(
  () => props.orderDetails.data,
  (d) => {
    if (d) {
      detailsManagerUuid.value = d.creator?.uuid ?? null;
      detailsEngineerUuid.value = d.assigned_employee?.uuid ?? null;
    }
  },
  { immediate: true },
);

const engineerOptions = computed(() => {
  const masters = props.employees.filter((e) => e.position === 'master');
  if (detailsEngineerUuid.value && !masters.some((e) => e.uuid === detailsEngineerUuid.value)) {
    const assigned = props.employees.find((e) => e.uuid === detailsEngineerUuid.value);
    if (assigned) return [assigned, ...masters];
  }
  return masters;
});

const workEngineerOptions = computed(() => {
  const masters = props.employees.filter((e) => e.position === 'master');
  const currentUuid = editingWork.value?.employee_uuid;
  if (currentUuid && !masters.some((e) => e.uuid === currentUuid)) {
    const current = props.employees.find((e) => e.uuid === currentUuid);
    if (current) return [current, ...masters];
  }
  return masters;
});

const availableStatuses = computed(() => {
  if (props.userRole === 'supervisor') return ORDER_STATUS_OPTIONS;
  return ORDER_STATUS_OPTIONS.filter((s) => s.value !== 'closed');
});

const orderCalculatedPrice = computed(() => {
  const d = props.orderDetails.data;
  if (!d) return 0;
  let total = 0;
  for (const w of d.works || []) {
    total += (w.price || 0) * (w.qty || 1);
  }
  for (const p of d.parts || []) {
    const unit = p.price ?? p.part_info?.price ?? 0;
    total += unit * (p.qty || 0);
  }
  return total;
});

async function saveOrderDetails() {
  if (!props.orderDetails.data) return;
  try {
    const payload = {
      status: props.orderDetails.data.status,
      price: orderCalculatedPrice.value,
      problem_description: props.orderDetails.data.problem_description,
    };
    if (detailsEngineerUuid.value !== (props.orderDetails.data.assigned_employee?.uuid ?? null)) {
      payload.assigned_employee_uuid = detailsEngineerUuid.value;
    }
    if (detailsManagerUuid.value !== (props.orderDetails.data.creator?.uuid ?? null)) {
      payload.creator_uuid = detailsManagerUuid.value;
    }
    await updateOrder(props.orderDetails.data.uuid, payload);
    const updated = await getOrderDetails(props.orderDetails.data.uuid);
    emit('update:order', updated);
  } catch (e) {
    emit('error', extractErrorMessage(e, 'Не удалось сохранить заказ.'));
  }
}

async function sendOrderComment() {
  if (!props.orderDetails.data || !newCommentText.value.trim()) return;
  try {
    await createOrderComment({
      order_uuid: props.orderDetails.data.uuid,
      text: newCommentText.value.trim(),
    });
    const updated = await getOrderDetails(props.orderDetails.data.uuid);
    emit('update:order', updated);
    newCommentText.value = '';
    await nextTick();
    if (commentsListRef.value) {
      commentsListRef.value.scrollTop = commentsListRef.value.scrollHeight;
    }
  } catch (e) {
    emit('error', extractErrorMessage(e, 'Не удалось отправить комментарий.'));
  }
}

function startEditWork(work) {
  editingWork.value = {
    uuid: work.uuid,
    title: work.title,
    employee_uuid: work.employee?.uuid || null,
    qty: work.qty || 1,
    price: work.price || 0,
    description: work.description || '',
  };
}

async function saveEditWork() {
  if (!editingWork.value || !props.orderDetails.data) return;
  try {
    const payload = {
      title: editingWork.value.title,
      qty: editingWork.value.qty,
      price: editingWork.value.price,
      description: editingWork.value.description || undefined,
    };
    if (editingWork.value.employee_uuid) {
      payload.employee_uuid = editingWork.value.employee_uuid;
    }
    await updateWork(editingWork.value.uuid, payload);
    const updated = await getOrderDetails(props.orderDetails.data.uuid);
    emit('update:order', updated);
    editingWork.value = null;
  } catch (e) {
    emit('error', extractErrorMessage(e, 'Не удалось обновить работу.'));
  }
}

const actLoading = ref(false);

function openPrintWindow(blob) {
  const url = URL.createObjectURL(new Blob([blob], { type: 'text/html' }));
  const win = window.open(url, '_blank');
  if (win) {
    win.addEventListener('afterprint', () => URL.revokeObjectURL(url));
    win.onload = () => win.print();
  }
  setTimeout(() => URL.revokeObjectURL(url), 120000);
}

async function printAct() {
  if (!props.orderDetails.data || actLoading.value) return;
  actLoading.value = true;
  try {
    const blob = await getOrderActHtml(props.orderDetails.data.uuid);
    openPrintWindow(blob);
  } catch (e) {
    emit('error', extractErrorMessage(e, 'Не удалось сгенерировать акт.'));
  } finally {
    actLoading.value = false;
  }
}

async function printReceipt() {
  if (!props.orderDetails.data || actLoading.value) return;
  actLoading.value = true;
  try {
    const blob = await getOrderReceiptHtml(props.orderDetails.data.uuid);
    openPrintWindow(blob);
  } catch (e) {
    emit('error', extractErrorMessage(e, 'Не удалось сгенерировать квитанцию.'));
  } finally {
    actLoading.value = false;
  }
}

async function decrementWork(work) {
  if (!props.orderDetails.data) return;
  try {
    if ((work.qty || 1) > 1) {
      await updateWork(work.uuid, { qty: (work.qty || 1) - 1 });
    } else {
      await deleteWork(work.uuid);
    }
    const updated = await getOrderDetails(props.orderDetails.data.uuid);
    emit('update:order', updated);
  } catch (e) {
    emit('error', extractErrorMessage(e, 'Не удалось обновить работу.'));
  }
}

async function decrementOrderPart(orderPart) {
  if (!props.orderDetails.data) return;
  try {
    if ((orderPart.qty || 0) > 1) {
      await updateOrderPart(orderPart.uuid, { qty: orderPart.qty - 1 });
    } else {
      await deleteOrderPart(orderPart.uuid);
    }
    const [updatedOrder, partsRes] = await Promise.all([
      getOrderDetails(props.orderDetails.data.uuid),
      getParts(),
    ]);
    emit('update:order', updatedOrder);
    emit('update:parts', partsRes.items);
  } catch (e) {
    emit('error', extractErrorMessage(e, 'Не удалось обновить запчасть в заказе.'));
  }
}

defineExpose({ printAct, printReceipt });
</script>
