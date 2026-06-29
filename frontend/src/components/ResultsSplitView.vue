<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import ApartmentCard from './ApartmentCard.vue'
import MapView from './MapView.vue'
import type { ApartmentResult } from '../api'

const props = defineProps<{
  apartments: ApartmentResult[]
  loading?: boolean
  submitted?: boolean
}>()

const selectedApartment = ref<ApartmentResult | null>(null)

function handleSelect(apt: ApartmentResult) {
  selectedApartment.value = apt
}

// Pagination & Filter States
const currentPage = ref(1)
const pageSize = ref(10)
const dealsOnly = ref(false)

// Reset page index on payload or filter changes
watch(() => props.apartments, () => {
  currentPage.value = 1
})
watch(dealsOnly, () => {
  currentPage.value = 1
})

// Filter results client-side
const filteredApartments = computed(() => {
  let list = props.apartments
  if (dealsOnly.value) {
    list = list.filter((apartment) => apartment.is_high_value_deal === true)
  }
  return list
})

// Paginate current slice for card rendering
const paginatedApartments = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredApartments.value.slice(start, end)
})

// Total pages count
const totalPages = computed(() => {
  return Math.ceil(filteredApartments.value.length / pageSize.value) || 1
})

// Mapped coordinates list matching current filter
const withCoordinates = computed(() =>
  filteredApartments.value.filter((apartment) => apartment.latitude != null && apartment.longitude != null),
)

function nextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

function prevPage() {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}
</script>

<template>
  <div class="grid gap-5 lg:grid-cols-[minmax(0,0.88fr)_minmax(0,1.12fr)]">
    <div v-reveal="0" class="rounded-[1.65rem] border border-white/70 bg-white/70 p-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.65)] backdrop-blur-xl sm:p-5">
      <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.35em] text-slate-500">Your matches</p>
          <h2 class="mt-2 display-font text-2xl font-semibold tracking-tight text-slate-950">Recommendations</h2>
          <p class="text-sm text-slate-600">
            <span v-if="props.loading">Loading results...</span>
            <span v-else-if="props.submitted">{{ filteredApartments.length }} apartments returned</span>
            <span v-else>Run a search to see ranked results</span>
          </p>
        </div>

        <div class="flex items-center gap-3">
          <!-- Hot Deals Curation Filter Toggle -->
          <div v-if="props.submitted && props.apartments.length" class="flex items-center rounded-full border border-slate-200 bg-white/60 p-0.5 shadow-sm">
            <button 
              @click="dealsOnly = false" 
              type="button"
              :class="['rounded-full px-3 py-1 text-[0.65rem] font-bold uppercase tracking-wider transition-all duration-300', !dealsOnly ? 'bg-slate-950 text-white shadow-sm' : 'bg-transparent text-slate-600 hover:text-slate-900']"
            >
              All
            </button>
            <button 
              @click="dealsOnly = true" 
              type="button"
              :class="['rounded-full px-3 py-1 text-[0.65rem] font-bold uppercase tracking-wider transition-all duration-300', dealsOnly ? 'bg-amber-500 text-white shadow-sm' : 'bg-transparent text-amber-700 hover:text-amber-900']"
            >
              🔥 Deals Only
            </button>
          </div>

          <div class="rounded-full border border-slate-200 bg-white/80 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
            {{ withCoordinates.length }} mapped
          </div>
        </div>
      </div>

      <div class="h-[640px] space-y-3 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-slate-300 scrollbar-track-transparent">
        <div v-if="!filteredApartments.length" class="flex h-full items-center justify-center rounded-[1.5rem] border border-dashed border-slate-300 bg-[linear-gradient(180deg,rgba(255,255,255,0.82),rgba(248,250,252,0.82))] p-8 text-center text-slate-500">
          <div>
            <p class="display-font text-2xl font-semibold text-slate-800">No matches found</p>
            <p class="mt-2 text-sm">No apartments match your current filters. Try relaxing your filters or toggling off the 'Deals Only' filter.</p>
          </div>
        </div>

        <ApartmentCard v-for="(apt, index) in paginatedApartments" :key="apt.id" :apt="apt" :style="{ '--reveal-delay': `${index * 25}ms` }" @select="handleSelect" />
      </div>

      <!-- Pagination Footer Controls -->
      <div v-if="filteredApartments.length > pageSize" class="mt-4 flex items-center justify-between border-t border-slate-150 pt-4">
        <button 
          @click="prevPage" 
          type="button"
          :disabled="currentPage === 1" 
          class="inline-flex items-center justify-center rounded-xl border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          ← Prev
        </button>
        <span class="text-xs font-semibold uppercase tracking-wider text-slate-500">
          Page {{ currentPage }} of {{ totalPages }} ({{ filteredApartments.length }} units)
        </span>
        <button 
          @click="nextPage" 
          type="button"
          :disabled="currentPage === totalPages" 
          class="inline-flex items-center justify-center rounded-xl border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Next →
        </button>
      </div>
    </div>

    <div v-reveal="120" class="overflow-hidden rounded-[1.65rem] border border-white/70 bg-white/70 shadow-[0_25px_60px_-35px_rgba(15,23,42,0.45)] backdrop-blur-xl">
      <MapView :apartments="filteredApartments" :selected="selectedApartment" />
    </div>
  </div>
</template>

<style scoped></style>
