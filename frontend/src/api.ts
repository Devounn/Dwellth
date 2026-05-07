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
  city?: string
  price: number
  beds?: number | null
  baths?: number | null
  sq_ft?: number | null
  lifestyle_tag?: string
  is_high_value_deal?: boolean
  latitude?: number | null
  longitude?: number | null
  similarity?: number
}

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

// Simple in-memory cache to avoid duplicate identical requests during tuning.
const cache = new Map<string, { ts: number; data: ApartmentResult[] }>()
const CACHE_TTL = 1000 * 60 // 60s

export async function recommend(payload: RecommendRequest): Promise<ApartmentResult[]> {
  const key = JSON.stringify(payload || {})
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

  const data = (await res.json()) as ApartmentResult[]
  cache.set(key, { ts: now, data })
  return data
}

export function clearRecommendCache() {
  cache.clear()
}

export default { recommend, clearRecommendCache }
