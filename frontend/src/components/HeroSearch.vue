<script setup lang="ts">
import { ref } from 'vue'
import type { RecommendRequest } from '../api'
const props = defineProps<{ loading?: boolean }>()
const emit = defineEmits<{
  (e: 'search', payload: RecommendRequest): void
}>()

const budget = ref<number | null>(2200)
const squareFeet = ref<number | null>(650)
const bedrooms = ref<number | null>(1)
const bathrooms = ref<number | null>(1)
const amenitiesCount = ref<number | null>(4)
const petsAllowed = ref(false)

function submit() {
  if (props.loading) return

  const payload: RecommendRequest = {
    budget: budget.value ?? undefined,
    square_feet: squareFeet.value ?? undefined,
    bedrooms: bedrooms.value ?? undefined,
    bathrooms: bathrooms.value ?? undefined,
    amenities_count: amenitiesCount.value ?? undefined,
    pets_allowed_bin: petsAllowed.value ? 1 : 0,
  }
  emit('search', payload)
}
</script>

<template>
  <form class="grid gap-4" @submit.prevent="submit">
    <div class="grid gap-4 sm:grid-cols-2">
      <label class="group rounded-[1.4rem] border border-slate-200 bg-white/80 px-4 py-3 shadow-[inset_0_1px_0_rgba(255,255,255,0.7)] transition focus-within:-translate-y-0.5 focus-within:border-sky-300 focus-within:shadow-[0_16px_40px_-24px_rgba(2,132,199,0.8)]">
        <span class="text-[0.65rem] font-semibold uppercase tracking-[0.35em] text-slate-500">Budget</span>
        <div class="mt-2 flex items-end gap-2">
          <span class="select-none text-lg font-semibold text-slate-400">$</span>
          <input v-model.number="budget" type="number" min="0" class="min-w-0 flex-1 border-0 bg-transparent p-0 text-lg font-semibold text-slate-950 outline-none placeholder:text-slate-400" placeholder="2200" />
        </div>
      </label>

      <label class="group rounded-[1.4rem] border border-slate-200 bg-white/80 px-4 py-3 shadow-[inset_0_1px_0_rgba(255,255,255,0.7)] transition focus-within:-translate-y-0.5 focus-within:border-amber-300 focus-within:shadow-[0_16px_40px_-24px_rgba(245,158,11,0.7)]">
        <span class="text-[0.65rem] font-semibold uppercase tracking-[0.35em] text-slate-500">Square feet</span>
        <input v-model.number="squareFeet" type="number" min="0" class="mt-2 w-full border-0 bg-transparent p-0 text-lg font-semibold text-slate-950 outline-none placeholder:text-slate-400" placeholder="650" />
      </label>

      <label class="group rounded-[1.4rem] border border-slate-200 bg-white/80 px-4 py-3 shadow-[inset_0_1px_0_rgba(255,255,255,0.7)] transition focus-within:-translate-y-0.5 focus-within:border-sky-300 focus-within:shadow-[0_16px_40px_-24px_rgba(14,165,233,0.8)]">
        <span class="text-[0.65rem] font-semibold uppercase tracking-[0.35em] text-slate-500">Bedrooms</span>
        <input v-model.number="bedrooms" type="number" min="0" class="mt-2 w-full border-0 bg-transparent p-0 text-lg font-semibold text-slate-950 outline-none placeholder:text-slate-400" placeholder="1" />
      </label>

      <label class="group rounded-[1.4rem] border border-slate-200 bg-white/80 px-4 py-3 shadow-[inset_0_1px_0_rgba(255,255,255,0.7)] transition focus-within:-translate-y-0.5 focus-within:border-emerald-300 focus-within:shadow-[0_16px_40px_-24px_rgba(16,185,129,0.65)]">
        <span class="text-[0.65rem] font-semibold uppercase tracking-[0.35em] text-slate-500">Bathrooms</span>
        <input v-model.number="bathrooms" type="number" min="0" step="0.5" class="mt-2 w-full border-0 bg-transparent p-0 text-lg font-semibold text-slate-950 outline-none placeholder:text-slate-400" placeholder="1" />
      </label>

      <label class="group rounded-[1.4rem] border border-slate-200 bg-white/80 px-4 py-3 shadow-[inset_0_1px_0_rgba(255,255,255,0.7)] transition focus-within:-translate-y-0.5 focus-within:border-rose-300 focus-within:shadow-[0_16px_40px_-24px_rgba(244,63,94,0.7)] sm:col-span-2">
        <span class="text-[0.65rem] font-semibold uppercase tracking-[0.35em] text-slate-500">Amenities count</span>
        <input v-model.number="amenitiesCount" type="number" min="0" class="mt-2 w-full border-0 bg-transparent p-0 text-lg font-semibold text-slate-950 outline-none placeholder:text-slate-400" placeholder="4" />
      </label>
    </div>

    <label class="group flex items-center justify-between rounded-[1.4rem] border border-slate-200 bg-white/80 px-4 py-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.7)] transition hover:border-slate-300">
      <span>
        <span class="block text-[0.65rem] font-semibold uppercase tracking-[0.35em] text-slate-500">Lifestyle</span>
        <span class="mt-1 block text-sm text-slate-600">Pets allowed</span>
      </span>
      <span class="relative inline-flex h-9 w-16 items-center rounded-full border border-slate-200 bg-slate-100 p-1 transition group-hover:bg-slate-200/80">
        <input v-model="petsAllowed" type="checkbox" class="peer sr-only" />
        <span class="h-7 w-7 rounded-full bg-white shadow-md transition-transform duration-300 peer-checked:translate-x-7 peer-checked:bg-gradient-to-r peer-checked:from-sky-400 peer-checked:to-emerald-300"></span>
      </span>
    </label>

    <button
      type="submit"
      :disabled="props.loading"
      class="group inline-flex w-full items-center justify-center rounded-[1.4rem] bg-slate-950 px-5 py-4 text-base font-semibold text-white shadow-[0_20px_50px_-24px_rgba(15,23,42,0.85)] transition hover:-translate-y-0.5 hover:bg-slate-900 disabled:cursor-not-allowed disabled:opacity-60"
    >
      <span v-if="props.loading">Searching...</span>
      <span v-else>Find homes</span>
      <span class="ml-2 inline-flex h-2 w-2 rounded-full bg-sky-400 transition group-hover:scale-125"></span>
    </button>
  </form>
</template>

<style scoped></style>
