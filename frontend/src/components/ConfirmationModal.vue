<template>
  <transition name="modal-fade">
    <div v-if="isOpen" class="modal-overlay" @click.self="cancel">
      <div class="modal-content">
        <div class="modal-header">
          <h3 class="modal-title">{{ title }}</h3>
          <button class="close-btn" @click="cancel">×</button>
        </div>
        <div class="modal-body">
          <p class="modal-message">{{ message }}</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="cancel">取消</button>
          <button class="btn btn-danger" @click="confirm">确定</button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'ConfirmationModal',
  props: {
    isOpen: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: '确认操作'
    },
    message: {
      type: String,
      default: '确定要执行此操作吗？'
    }
  },
  emits: ['confirm', 'cancel'],
  methods: {
    confirm() {
      this.$emit('confirm')
    },
    cancel() {
      this.$emit('cancel')
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: var(--bg-card, #1e1e1e);
  border: 1px solid var(--border-color, #333);
  border-radius: var(--radius-lg, 12px);
  width: 90%;
  max-width: 400px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

.modal-header {
  padding: var(--space-md, 1rem) var(--space-lg, 1.5rem);
  border-bottom: 1px solid var(--border-color, #333);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary, #fff);
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-muted, #999);
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.close-btn:hover {
  color: var(--text-primary, #fff);
}

.modal-body {
  padding: var(--space-lg, 1.5rem);
}

.modal-message {
  margin: 0;
  color: var(--text-secondary, #ccc);
  line-height: 1.5;
}

.modal-footer {
  padding: var(--space-md, 1rem) var(--space-lg, 1.5rem);
  background: var(--bg-input, #2a2a2a);
  display: flex;
  justify-content: flex-end;
  gap: var(--space-sm, 0.5rem);
}

/* Inherit button styles from parent or define basic ones for fallback */
.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-secondary {
  background: var(--bg-hover, #444);
  color: var(--text-primary, #fff);
}

.btn-secondary:hover {
  background: var(--bg-active, #555);
}

.btn-danger {
  background: var(--danger, #ef4444);
  color: white;
}

.btn-danger:hover {
  background: var(--danger-hover, #dc2626);
}

/* Animations */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active .modal-content,
.modal-fade-leave-active .modal-content {
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.modal-fade-enter-from .modal-content,
.modal-fade-leave-to .modal-content {
  transform: scale(0.95) translateY(10px);
}
</style>
