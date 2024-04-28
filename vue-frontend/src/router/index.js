import { createRouter, createWebHistory } from 'vue-router'
import LatestPosition from '../components/LatestPosition.vue'
import Positions from '../components/Positions.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/positions/latest',
      name: 'latestposition',
      component: LatestPosition
    },
    {
      path: '/positions',
      name: 'positions',
      component: Positions
    },
  ]
})

export default router