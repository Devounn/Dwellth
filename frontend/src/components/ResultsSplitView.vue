<script setup lang="ts">
import { computed } from 'vue'
import ApartmentCard from './ApartmentCard.vue'
import MapView from './MapView.vue'
import type { ApartmentResult } from '../api'
const props = defineProps<{
  apartments: ApartmentResult[]
  loading?: boolean
  submitted?: boolean
}>()

import { ref } from 'vue'

const selectedApartment = ref<ApartmentResult | null>(null)

function handleSelect(apt: ApartmentResult) {
  selectedApartment.value = apt
}

const withCoordinates = computed(() =>
  props.apartments.filter((apartment) => apartment.latitude != null && apartment.longitude != null),
)
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
            <span v-else-if="props.submitted">{{ props.apartments.length }} apartments returned</span>
            <span v-else>Run a search to see ranked results</span>
          </p>
        </div>
        <div class="rounded-full border border-slate-200 bg-white/80 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
          {{ withCoordinates.length }} mapped
        </div>
      </div>

      <div class="h-[640px] space-y-3 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-slate-300 scrollbar-track-transparent">
        <div v-if="!props.apartments.length" class="flex h-full items-center justify-center rounded-[1.5rem] border border-dashed border-slate-300 bg-[linear-gradient(180deg,rgba(255,255,255,0.82),rgba(248,250,252,0.82))] p-8 text-center text-slate-500">
          <div>
            <p class="display-font text-2xl font-semibold text-slate-800">No recommendations yet</p>
            <p class="mt-2 text-sm">Use the form above to generate your first set of apartments.</p>
          </div>
        </div>

        <ApartmentCard v-for="(apt, index) in props.apartments" :key="apt.id" :apt="apt" :style="{ '--reveal-delay': `${index * 70}ms` }" @select="handleSelect" />
      </div>
    </div>

    <div v-reveal="120" class="overflow-hidden rounded-[1.65rem] border border-white/70 bg-white/70 shadow-[0_25px_60px_-35px_rgba(15,23,42,0.45)] backdrop-blur-xl">
      <MapView :apartments="props.apartments" :selected="selectedApartment" />
    </div>
  </div>
</template>

<style scoped></style>
