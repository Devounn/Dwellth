import { createApp } from 'vue'
import App from './App.vue'
import 'leaflet/dist/leaflet.css'
import './styles.css'

const app = createApp(App)

app.directive('reveal', {
	mounted(el, binding) {
		if (!(el instanceof HTMLElement)) return

		el.classList.add('reveal')
		if (typeof binding.value === 'number') {
			el.style.setProperty('--reveal-delay', `${binding.value}ms`)
		}

		const observer = new IntersectionObserver(
			([entry]) => {
				if (!entry) return

				if (entry.isIntersecting) {
					el.classList.add('is-visible')
					observer.disconnect()
				}
			},
			{ threshold: 0.15, rootMargin: '0px 0px -10% 0px' },
		)

		observer.observe(el)
		;(el as HTMLElement & { __revealObserver?: IntersectionObserver }).__revealObserver = observer
	},
	unmounted(el) {
		;(el as HTMLElement & { __revealObserver?: IntersectionObserver }).__revealObserver?.disconnect()
	},
})

app.mount('#app')
