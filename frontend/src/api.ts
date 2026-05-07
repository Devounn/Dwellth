export type RecommendRequest = {
  budget?: number
  square_feet?: number
  bedrooms?: number
  bathrooms?: number
  amenities_count?: number
  pets_allowed_bin?: number
}

export type ApartmentResult = {
  id: string
  title: string
  description?: string
  city?: string
  address?: string
  state?: string
  name?: string
  apartment_name?: string
  price: number
  estimated_price?: number | null
  predicted_fair_price?: number | null
  beds?: number | null
  baths?: number | null
  sq_ft?: number | null
  lifestyle_tag?: string
  is_high_value_deal?: boolean
  latitude?: number | null
  longitude?: number | null
  similarity?: number
  [key: string]: unknown
}

function toApartmentResult(raw: Record<string, unknown>, fallbackId: number): ApartmentResult {
  const title =
    (typeof raw.title === 'string' && raw.title) ||
    (typeof raw.name === 'string' && raw.name) ||
    (typeof raw.apartment_name === 'string' && raw.apartment_name) ||
    (typeof raw.property_name === 'string' && raw.property_name) ||
    (typeof raw.listing_title === 'string' && raw.listing_title) ||
    (typeof raw.address === 'string' && raw.address) ||
    `Apartment ${fallbackId + 1}`

  const description =
    (typeof raw.description === 'string' && raw.description) ||
    (typeof raw.summary === 'string' && raw.summary) ||
    (typeof raw.details === 'string' && raw.details) ||
    (typeof raw.description_text === 'string' && raw.description_text) ||
    undefined

  return {
    ...raw,
    id: typeof raw.id === 'string' ? raw.id : String(raw.id ?? fallbackId),
    title,
    description,
    city: typeof raw.city === 'string' ? raw.city : typeof raw.cityname === 'string' ? raw.cityname : undefined,
    price: typeof raw.price === 'number' ? raw.price : Number(raw.price ?? 0),
    estimated_price:
      typeof raw.estimated_price === 'number'
        ? raw.estimated_price
        : typeof raw.predicted_fair_price === 'number'
          ? raw.predicted_fair_price
          : typeof raw.fair_price === 'number'
            ? raw.fair_price
            : typeof raw.estimated_price === 'number'
              ? raw.estimated_price
              : null,
    predicted_fair_price:
      typeof raw.predicted_fair_price === 'number'
        ? raw.predicted_fair_price
        : typeof raw.fair_price === 'number'
          ? raw.fair_price
          : typeof raw.estimated_price === 'number'
            ? raw.estimated_price
            : null,
    beds: typeof raw.beds === 'number' ? raw.beds : typeof raw.bedrooms === 'number' ? raw.bedrooms : null,
    baths: typeof raw.baths === 'number' ? raw.baths : typeof raw.bathrooms === 'number' ? raw.bathrooms : null,
    sq_ft: typeof raw.sq_ft === 'number' ? raw.sq_ft : typeof raw.square_feet === 'number' ? raw.square_feet : null,
    latitude: typeof raw.latitude === 'number' ? raw.latitude : typeof raw.lat === 'number' ? raw.lat : null,
    longitude: typeof raw.longitude === 'number' ? raw.longitude : typeof raw.lon === 'number' ? raw.lon : null,
    similarity: typeof raw.similarity === 'number' ? raw.similarity : undefined,
  }
}

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

// Simple in-memory cache to avoid duplicate identical requests during tuning.
const cache = new Map<string, { ts: number; data: ApartmentResult[] }>()
const CACHE_TTL = 1000 * 60 // 60s
const CACHE_VERSION = 2

export async function recommend(payload: RecommendRequest): Promise<ApartmentResult[]> {
  const key = `${CACHE_VERSION}:${JSON.stringify(payload || {})}`
  const now = Date.now()

  const entry = cache.get(key)
  if (entry && now - entry.ts < CACHE_TTL) {
    return entry.data
  }

  const res = await fetch(`${API_BASE}/recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!res.ok) {
    throw new Error(`API error: ${res.status}`)
  }

  const data = (await res.json()) as Record<string, unknown>[]
  const normalized = data.map((item, index) => toApartmentResult(item, index))
  cache.set(key, { ts: now, data: normalized })
  return normalized
}

export function clearRecommendCache() {
  cache.clear()
}

export default { recommend, clearRecommendCache }
