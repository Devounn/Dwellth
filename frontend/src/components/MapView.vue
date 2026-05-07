<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import L from 'leaflet'
import type { ApartmentResult } from '../api'
const props = defineProps<{ apartments: ApartmentResult[]; selected?: ApartmentResult | null }>()

const mapContainer = ref<HTMLDivElement | null>(null)
let map: L.Map | null = null
const markerLayer = L.layerGroup()
const markersMap = new Map<string, L.Marker>()

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

  const bounds: L.LatLngExpression[] = []

  for (const apartment of apartments) {
    if (apartment.latitude == null || apartment.longitude == null) continue
    const marker = L.marker([apartment.latitude, apartment.longitude])
      .bindPopup(
      `
        <div style="min-width: 180px">
          <div style="font-weight: 700; margin-bottom: 4px">${apartment.title}</div>
          <div style="font-size: 12px; color: #475569; margin-bottom: 6px">${apartment.city ?? ''}</div>
          <div style="font-size: 12px; color: #475569; margin-bottom: 6px">${apartment.description ?? ''}</div>
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
      // If marker isn't present yet, just pan and add a temporary marker
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
  <div class="flex h-[720px] flex-col bg-[radial-gradient(circle_at_top_right,rgba(132,207,255,0.18),transparent_20%),linear-gradient(160deg,#06111f_0%,#111827_55%,#17213a_100%)]">
    <div class="flex items-center justify-between border-b border-white/10 px-5 py-4 text-white/90">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.35em] text-sky-300">Map view</p>
        <h3 class="mt-1 display-font text-2xl font-semibold text-white">Recommended apartments</h3>
      </div>
    </div>

    <div class="relative min-h-0 flex-1">
      <div ref="mapContainer" class="h-full w-full"></div>

      <div class="pointer-events-none absolute left-4 top-4 max-w-xs rounded-[1.25rem] border border-white/10 bg-slate-950/50 p-4 text-white shadow-2xl backdrop-blur-md">
        <p class="text-[0.65rem] font-semibold uppercase tracking-[0.35em] text-sky-300">Overview</p>
        <p class="mt-2 text-sm leading-6 text-white/80">
          Each pin reflects a recommended apartment.
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
