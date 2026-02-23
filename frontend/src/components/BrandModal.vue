<template>
  <div
    v-if="open"
    class="modal-backdrop"
    @click="$emit('close')"
  >
    <div class="modal" @click.stop>
      <div class="login-card">
        <div class="field">
          <div class="field-label">{{ editBrand ? 'Редактирование бренда' : 'Новый бренд' }}</div>
        </div>
        <div class="field">
          <label class="field-label">Название</label>
          <input
            v-model="name"
            class="field-input"
            type="text"
            placeholder="Samsung"
          >
        </div>
        <div class="field">
          <button
            class="btn btn-primary"
            type="button"
            :disabled="!nameTrimmed"
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
import { ref, watch, computed } from 'vue';

const props = defineProps({
  open: { type: Boolean, required: true },
  editBrand: { type: Object, default: null },
});

const emit = defineEmits(['close', 'submit']);

const name = ref('');

const nameTrimmed = computed(() => (name.value || '').trim());

watch(() => [props.open, props.editBrand], () => {
  if (props.open) {
    name.value = props.editBrand?.name ?? '';
  }
}, { immediate: true });

function submit() {
  if (!nameTrimmed.value) return;
  emit('submit', { name: nameTrimmed.value });
}
</script>
