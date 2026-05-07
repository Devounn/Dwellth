<script setup lang="ts">
const emit = defineEmits<{
  (e: 'done'): void
}>()

import { onMounted } from 'vue'

onMounted(() => {
  // auto-close after animation completes
  const timeout = setTimeout(() => emit('done'), 2000)
  return () => clearTimeout(timeout)
})
</script>

<template>
  <div class="intro-overlay">
    <div class="spinner-wrap">
      <div class="spinner-core">
        <svg viewBox="0 0 100 100" class="spinner-logo" aria-hidden="true">
          <defs>
            <linearGradient id="g" x1="0" x2="1">
              <stop offset="0%" stop-color="#84cfff" />
              <stop offset="100%" stop-color="#a9f0d1" />
            </linearGradient>
          </defs>
          <circle cx="50" cy="50" r="36" stroke="url(#g)" stroke-width="8" fill="none" stroke-linecap="round" stroke-dasharray="100 200" />
          <circle cx="50" cy="50" r="16" fill="#fff" opacity="0.08" />
        </svg>
      </div>
      <div class="spinner-caption">Dwellth</div>
    </div>
  </div>
</template>

<style scoped>
.intro-overlay {
  position: fixed;
  inset: 0;
  display: grid;
  place-items: center;
  background: linear-gradient(180deg, rgba(8,10,20,0.6), rgba(8,10,20,0.45));
  z-index: 60;
  pointer-events: none;
  animation: intro-fade 1.2s ease forwards;
}
.spinner-wrap {
  pointer-events: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.spinner-core {
  width: 96px;
  height: 96px;
  display: grid;
  place-items: center;
  border-radius: 999px;
  background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.04), transparent 20%);
  box-shadow: 0 18px 50px -20px rgba(2,6,23,0.6);
}
.spinner-logo {
  width: 72px;
  height: 72px;
  transform-origin: 50% 50%;
  animation: spin 1.1s cubic-bezier(.2,.9,.2,1) infinite;
}
.spinner-caption {
  color: #e6f6ff;
  font-weight: 700;
  letter-spacing: 0.06em;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes intro-fade {
  0% { opacity: 1; }
  80% { opacity: 1; }
  100% { opacity: 0; visibility: hidden; transform: scale(1.02); }
}
</style>
