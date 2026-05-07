<script setup lang="ts">
import { defineEmits } from 'vue'
import type { ApartmentResult } from '../api'
const props = defineProps<{ apt: ApartmentResult }>()
const emit = defineEmits<{ (e: 'select', apt: ApartmentResult): void }>()
</script>

<template>
  <article v-reveal @click="emit('select', props.apt)" class="group cursor-pointer overflow-hidden rounded-[1.5rem] border border-slate-200 bg-white/85 p-4 shadow-[0_20px_50px_-32px_rgba(15,23,42,0.45)] transition duration-500 hover:-translate-y-1 hover:border-slate-300 hover:shadow-[0_28px_70px_-30px_rgba(15,23,42,0.5)]">
    <div class="flex items-start justify-between gap-4">
      <div>
        <div class="flex flex-wrap gap-2">
          <span class="rounded-full bg-slate-950 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-white">
            {{ apt.lifestyle_tag || 'Recommended' }}
          </span>
          <span v-if="apt.is_high_value_deal" class="rounded-full border border-amber-300 bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-900 shadow-[0_0_25px_rgba(245,158,11,0.22)]">
            🔥 High Value Deal
          </span>
        </div>

        <h3 class="mt-3 display-font text-2xl font-semibold tracking-tight text-slate-950">
          {{ apt.title }}
        </h3>
        <p class="mt-1 text-sm text-slate-500">{{ apt.city || 'City unavailable' }}</p>
        <p v-if="apt.description" class="mt-3 text-sm text-slate-600">{{ apt.description }}</p>
      </div>

      <div class="text-right">
        <div class="text-3xl font-semibold text-slate-950">${{ apt.price.toLocaleString() }}</div>
        <div class="mt-1 text-xs uppercase tracking-[0.22em] text-slate-400">per month</div>
      </div>
    </div>

    <dl class="mt-4 grid grid-cols-3 gap-3 border-t border-slate-200 pt-4 text-sm text-slate-600">
      <div class="rounded-2xl bg-slate-50 px-3 py-3">
        <dt class="text-xs uppercase tracking-[0.2em] text-slate-400">Beds</dt>
        <dd class="mt-1 font-medium text-slate-900">{{ apt.beds ?? '—' }}</dd>
      </div>
      <div class="rounded-2xl bg-slate-50 px-3 py-3">
        <dt class="text-xs uppercase tracking-[0.2em] text-slate-400">Baths</dt>
        <dd class="mt-1 font-medium text-slate-900">{{ apt.baths ?? '—' }}</dd>
      </div>
      <div class="rounded-2xl bg-slate-50 px-3 py-3">
        <dt class="text-xs uppercase tracking-[0.2em] text-slate-400">Sq Ft</dt>
        <dd class="mt-1 font-medium text-slate-900">{{ apt.sq_ft ? apt.sq_ft.toLocaleString() : '—' }}</dd>
      </div>
    </dl>

    <div v-if="apt.similarity !== undefined" class="mt-4 h-2 overflow-hidden rounded-full bg-slate-100">
      <div class="h-full rounded-full bg-gradient-to-r from-sky-400 to-indigo-500" :style="{ width: `${Math.max(8, Math.min(100, (apt.similarity || 0) * 100))}%` }"></div>
    </div>
  </article>
</template>

<style scoped></style>
