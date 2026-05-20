<script setup lang="ts">
import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
import HeroSearch from './components/HeroSearch.vue'
import ResultsSplitView from './components/ResultsSplitView.vue'
import IntroSpinner from './components/IntroSpinner.vue'
import type { RecommendRequest, ApartmentResult } from './api'
import { recommend } from './api'

const results = ref<ApartmentResult[]>([])
const loading = ref(false)
const error = ref('')
const submitted = ref(false)
const showIntro = ref(true)

const isCompact = ref(false)

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function handleScroll() {
  isCompact.value = window.scrollY > 160
}

onMounted(() => window.addEventListener('scroll', handleScroll, { passive: true }))
onBeforeUnmount(() => window.removeEventListener('scroll', handleScroll))

const totalResults = computed(() => results.value.length)

async function onSearch(payload: RecommendRequest) {
  loading.value = true
  error.value = ''
  submitted.value = true

  try {
    results.value = await recommend(payload)
  } catch (err) {
    results.value = []
    error.value = err instanceof Error ? err.message : 'Unable to load recommendations.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen overflow-x-hidden text-slate-900">
    <IntroSpinner v-if="showIntro" @done="showIntro = false" />
    <div class="pointer-events-none fixed inset-0 -z-10">
      <div class="absolute left-[-10%] top-[-12%] h-80 w-80 rounded-full bg-sky-300/35 blur-3xl motion-safe:animate-[pulse_10s_ease-in-out_infinite]"></div>
      <div class="absolute right-[-6%] top-[8%] h-96 w-96 rounded-full bg-amber-300/25 blur-3xl motion-safe:animate-[pulse_12s_ease-in-out_infinite]"></div>
      <div class="absolute bottom-[-10%] left-[18%] h-80 w-80 rounded-full bg-emerald-200/35 blur-3xl motion-safe:animate-[pulse_14s_ease-in-out_infinite]"></div>
    </div>

    <header class="px-4 pt-5 sm:px-6 lg:px-8">
      <div :class="[ 'soft-panel mx-auto flex max-w-7xl items-center justify-between rounded-full py-4', isCompact ? 'compact-header pl-4 pr-4' : 'pl-8 pr-6 sm:pl-10 lg:pl-12' ]">
        <div class="flex items-center gap-3">
          <p class="text-[0.85rem] uppercase tracking-[0.5em] text-slate-500">Dwellth</p>
          <p v-if="!isCompact" class="mt-1 display-font text-2xl font-semibold tracking-tight text-slate-950 sm:text-3xl">Curated apartment recommendations</p>
        </div>

        <div class="flex items-center gap-3">
          <button v-if="isCompact" @click="scrollToTop" class="compact-btn" aria-label="Open Dwellth">
            <span class="compact-initial">D</span>
          </button>
        </div>
      </div>
    </header>

    <main class="mx-auto flex w-full max-w-7xl flex-col gap-7 px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
      <section class="grid gap-6 lg:grid-cols-[1.08fr_0.92fr]">
        <div v-reveal="0" class="soft-panel relative overflow-hidden rounded-[2.25rem] p-6 sm:p-8 lg:p-10">
          <div class="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(132,207,255,0.22),transparent_30%),radial-gradient(circle_at_bottom_left,rgba(242,184,75,0.18),transparent_28%)]"></div>
          <div class="absolute left-0 top-0 h-full w-px bg-gradient-to-b from-sky-300/70 via-amber-200/60 to-transparent"></div>
          <div class="relative flex h-full min-h-[420px] items-center">
            <div class="max-w-2xl">
              <h2 class="max-w-xl display-font text-5xl font-semibold leading-[0.94] tracking-tight text-slate-950 sm:text-6xl lg:text-7xl">
                Apartments that feel curated, not scraped.
              </h2>

              <p class="mt-5 max-w-2xl text-base leading-8 text-slate-700 sm:text-lg">
                Search by budget, size, and lifestyle signals. The recommender blends clustering, similarity, and value scoring, then returns the sharpest options first.
              </p>
            </div>
          </div>
        </div>

        <div v-reveal="120" class="soft-panel relative overflow-hidden rounded-[2.25rem] p-5 sm:p-6 lg:p-8">
          <div class="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-sky-400 via-amber-300 to-emerald-300"></div>
          <div class="flex flex-col gap-5">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.35em] text-slate-500">Search panel</p>
              <h3 class="mt-2 display-font text-3xl font-semibold tracking-tight text-slate-950">Tune the filters, let the model do the rest.</h3>
              <p class="mt-3 max-w-xl text-sm leading-7 text-slate-600 sm:text-base">
                  Think about it, It's going to be your home after all.
              </p>
            </div>

            <HeroSearch :loading="loading" @search="onSearch" />

            <p v-if="error" class="rounded-[1.25rem] border border-rose-300 bg-rose-50 px-4 py-3 text-sm text-rose-700">
              {{ error }}
            </p>
          </div>
        </div>
      </section>

      <section v-reveal="80" class="soft-panel rounded-[2.25rem] p-3 sm:p-4 lg:p-5">
        <ResultsSplitView :apartments="results" :loading="loading" :submitted="submitted" />
      </section>
    </main>
  </div>
</template>

<style scoped></style>
