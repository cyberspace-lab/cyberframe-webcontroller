import { createRouter, createWebHistory } from 'vue-router'
import ActiveSessions from '@/components/ActiveSessions.vue'
import ActiveSessionDetail from '@/components/ActiveSessionDetail.vue'
import InactiveSessions from '@/components/InactiveSessions.vue'
import InactiveSessionDetail from '@/components/InactiveSessionDetail.vue'
import ConfigEdit from '@/components/ConfigEdit.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/activesessions',
      name: 'activesessions',
      component: ActiveSessions
    },
    {
      path: '/activesessiondetail/:deviceId/:sessionName',
      name: 'activesessiondetail',
      component: ActiveSessionDetail,
      props: true
    },
    {
      path: '/inactivesessions',
      name: 'inactivesessions',
      component: InactiveSessions
    },
    {
      path: '/inactivesessiondetail/:deviceId/:sessionName',
      name: 'inactivesessiondetail',
      component: InactiveSessionDetail,
      props: true
    },
    {
      path: '/configedit',
      name: 'configedit',
      component: ConfigEdit
    }
  ]
})

export default router