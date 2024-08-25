import { createRouter, createWebHistory } from 'vue-router'
import LatestPosition from '../components/LatestPosition.vue'
import Positions from '../components/Positions.vue'
import OngoingSessions from '../components/OngoingSessions.vue'
import ControlPanel from '../components/ControlPanel.vue'
import PastSessions from '@/components/PastSessions.vue';
import PastSessionDetail from '@/components/PastSessionDetail.vue';

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
    {
      path: '/sessions',
      name: 'ongoingsessions',
      component: OngoingSessions
    },
    {
      path: '/controlpanel/:deviceId',
      name: 'controlpanel',
      component: ControlPanel,
      props: true
    },
    {
      path: '/past-sessions',
      name: 'pastsessions',
      component: PastSessions
    },
    {
      path: '/pastsessiondetail/:deviceId',
      name: 'pastsessiondetail',
      component: PastSessionDetail,
      props: true
    }
  ]
})

export default router