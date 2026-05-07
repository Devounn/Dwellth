<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import L from 'leaflet'
import type { ApartmentResult } from '../api'
const props = defineProps<{ apartments: ApartmentResult[]; selected?: ApartmentResult | null }>()

const mapContainer = ref<HTMLDivElement | null>(null)
let map: L.Map | null = null
const markerLayer = L.layerGroup()
const markersMap = new Map<string, L.Marker>()

function truncate(text: string, max = 260) {
  if (!text) return ''
  return text.length > max ? `${text.slice(0, max).trimEnd()}...` : text
}

const mappedCount = computed(() => props.apartments.filter((apartment) => apartment.latitude != null && apartment.longitude != null).length)

const selectedLabel = computed(() => {
  const apartment = props.selected
  if (!apartment) return 'Select a card to lock the map'
  return apartment.title || apartment.name || apartment.apartment_name || apartment.address || 'Selected apartment'
})

const selectedAddress = computed(() => {
  const apartment = props.selected
  if (!apartment) return ''
  return apartment.address || apartment.city || ''
})

const selectedDescription = computed(() => truncate(props.selected?.description ?? '', 168))

const selectedActualPrice = computed(() => props.selected?.price ?? null)

const selectedEstimatedPrice = computed(() => props.selected?.estimated_price ?? props.selected?.predicted_fair_price ?? null)

const priceGap = computed(() => {
  if (selectedActualPrice.value == null || selectedEstimatedPrice.value == null) return null
  return selectedEstimatedPrice.value - selectedActualPrice.value
})

const defaultIcon = L.icon({
  iconUrl: new URL('leaflet/dist/images/marker-icon.png', import.meta.url).href,
  iconRetinaUrl: new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href,
  shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

L.Marker.prototype.options.icon = defaultIcon

function renderMarkers(apartments: ApartmentResult[]) {
  if (!map) return

  markerLayer.clearLayers()
  markersMap.clear()

  const bounds: L.LatLngExpression[] = []

  for (const apartment of apartments) {
    if (apartment.latitude == null || apartment.longitude == null) continue
    const popupDescription = truncate(apartment.description ?? '', 260)
    const marker = L.marker([apartment.latitude, apartment.longitude])
      .bindPopup(
      `
        <div style="min-width: 180px">
          <div style="font-weight: 800; margin-bottom: 4px">${apartment.title}</div>
          <div style="font-size: 12px; color: #475569; margin-bottom: 6px">${apartment.city ?? ''}</div>
          <div style="font-size: 12px; color: #475569; margin-bottom: 6px; line-height: 1.45">${popupDescription}</div>
          <div style="font-weight: 600">$${apartment.price.toLocaleString()}</div>
        </div>
      `,
    )
    markerLayer.addLayer(marker)
    markersMap.set(apartment.id, marker)
    bounds.push([apartment.latitude, apartment.longitude])
  }

  markerLayer.addTo(map)

  if (bounds.length > 0) {
    map.fitBounds(bounds as L.LatLngBoundsExpression, { padding: [24, 24], maxZoom: 13 })
  }
}

onMounted(() => {
  if (!mapContainer.value) return

  map = L.map(mapContainer.value, {
    zoomControl: true,
    scrollWheelZoom: false,
  }).setView([40.7128, -74.006], 11)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(map)

  renderMarkers(props.apartments)

  nextTick(() => {
    map?.invalidateSize()
  })
})

watch(
  () => props.apartments,
  (list) => {
    renderMarkers(list)
  },
  { deep: true },
)

// When user selects a card, center map on the apartment and open popup
watch(
  () => props.selected,
  (sel) => {
    if (!sel || !map) return
    if (sel.latitude == null || sel.longitude == null) return

    const marker = markersMap.get(sel.id)
    if (marker) {
      map.setView([sel.latitude, sel.longitude], 15, { animate: true })
      marker.openPopup()
    } else {
      // If marker isn't present yet, just pan to the selected coordinates.
      map.setView([sel.latitude, sel.longitude], 15, { animate: true })
    }
  },
  { deep: true },
)

onBeforeUnmount(() => {
  map?.remove()
  map = null
})
</script>

<template>
  <div class="flex min-h-[760px] flex-col overflow-hidden rounded-[1.65rem] bg-[radial-gradient(circle_at_top_right,rgba(132,207,255,0.16),transparent_24%),radial-gradient(circle_at_bottom_left,rgba(242,184,75,0.08),transparent_24%),linear-gradient(160deg,#06111f_0%,#0f1728_48%,#17213a_100%)]">
    <div class="flex shrink-0 items-center justify-between border-b border-white/10 px-5 py-4 text-white/90">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.35em] text-sky-300">Map view</p>
        <h3 class="mt-1 display-font text-2xl font-semibold text-white">Recommended apartments</h3>
      </div>

      <div class="hidden items-center gap-2 sm:flex">
        <span class="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[0.65rem] font-semibold uppercase tracking-[0.3em] text-white/75">
          {{ mappedCount }} mapped
        </span>
        <span class="rounded-full border border-sky-300/30 bg-sky-300/10 px-3 py-1 text-[0.65rem] font-semibold uppercase tracking-[0.3em] text-sky-200">
          Click a card
        </span>
      </div>
    </div>

    <div class="relative min-h-[520px] flex-1 overflow-hidden isolate">
      <div ref="mapContainer" class="absolute inset-0 z-0 h-full w-full"></div>

      <div class="pointer-events-none absolute inset-0 z-10 bg-[linear-gradient(180deg,rgba(6,17,31,0.04)_0%,rgba(6,17,31,0)_18%,rgba(6,17,31,0)_72%,rgba(6,17,31,0.15)_100%)]"></div>

      <div class="pointer-events-auto absolute inset-x-0 bottom-0 z-20 max-h-[42%] overflow-y-auto border-t border-white/10 bg-[#08101c]/98 px-5 py-4 text-white/95 shadow-[0_-18px_40px_-24px_rgba(0,0,0,0.8)] backdrop-blur-lg">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div class="max-w-2xl">
            <p class="text-[0.65rem] font-semibold uppercase tracking-[0.35em] text-sky-300">Overview</p>
            <p class="mt-2 text-sm leading-6 text-white/80">
              Each pin reflects a recommended apartment. Tap a card to focus the matching pin.
            </p>
          </div>
        </div>

        <div class="mt-4 grid gap-3 sm:grid-cols-[minmax(0,1.2fr)_auto] sm:items-end">
          <div>
            <p class="text-[0.65rem] font-semibold uppercase tracking-[0.35em] text-white/45">Focus</p>
            <p class="mt-1 display-font text-xl font-semibold text-white">{{ selectedLabel }}</p>
            <p v-if="selectedAddress" class="mt-1 text-sm text-white/65">{{ selectedAddress }}</p>
            <p v-if="selectedDescription" class="mt-2 text-sm leading-6 text-white/75">{{ selectedDescription }}</p>
          </div>

          <div class="rounded-[1.15rem] border border-white/10 bg-white/6 px-4 py-3 shadow-[0_12px_30px_-20px_rgba(0,0,0,0.65)]">
            <p class="text-[0.62rem] font-semibold uppercase tracking-[0.3em] text-white/45">Actual vs estimated</p>
            <div class="mt-2 grid grid-cols-2 gap-3 text-left">
              <div>
                <p class="text-[0.62rem] font-semibold uppercase tracking-[0.28em] text-white/45">Actual</p>
                <p class="mt-1 text-lg font-semibold text-white">
                  {{ selectedActualPrice != null ? `$${Math.round(selectedActualPrice).toLocaleString()}` : '—' }}
                </p>
              </div>
              <div>
                <p class="text-[0.62rem] font-semibold uppercase tracking-[0.28em] text-white/45">Estimated</p>
                <p class="mt-1 text-lg font-semibold text-sky-200">
                  {{ selectedEstimatedPrice != null ? `$${Math.round(selectedEstimatedPrice).toLocaleString()}` : '—' }}
                </p>
              </div>
            </div>
            <p v-if="priceGap !== null" class="mt-2 text-xs text-white/60">
              {{ priceGap >= 0 ? 'Estimated above actual by' : 'Estimated below actual by' }}
              <span class="font-semibold text-white">${{ Math.abs(Math.round(priceGap)).toLocaleString() }}</span>
            </p>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
