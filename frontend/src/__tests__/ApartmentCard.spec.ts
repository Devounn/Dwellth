import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import ApartmentCard from '../components/ApartmentCard.vue'

function mountCard(similarity: number | undefined) {
  return mount(ApartmentCard, {
    props: {
      apt: {
        id: 'apt-1',
        title: 'Test Apartment',
        price: 2400,
        similarity,
      },
    },
    global: {
      directives: {
        reveal: () => undefined,
      },
    },
  })
}

describe('ApartmentCard similarity bar', () => {
  it('hides the bar when similarity is zero', () => {
    const wrapper = mountCard(0)

    expect(wrapper.text()).toContain('0%')
    expect(wrapper.find('.h-full.rounded-full').exists()).toBe(false)
  })

  it('renders a blue bar for positive similarity', () => {
    const wrapper = mountCard(0.42)
    const bar = wrapper.find('.h-full.rounded-full')

    expect(bar.exists()).toBe(true)
    expect(bar.attributes('class')).toContain('from-sky-400')
    expect(bar.attributes('style')).toContain('width: 42%')
  })

  it('renders a red bar for negative similarity', () => {
    const wrapper = mountCard(-0.18)
    const bar = wrapper.find('.h-full.rounded-full')

    expect(bar.exists()).toBe(true)
    expect(bar.attributes('class')).toContain('from-rose-400')
    expect(bar.attributes('style')).toContain('width: 18%')
  })
})