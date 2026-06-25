import { createRouter, createWebHistory } from 'vue-router'
import { storage } from '../utils/storage'
import BasicLayout from '../layouts/BasicLayout.vue'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import FieldsView from '../views/FieldsView.vue'
import FieldDetailView from '../views/FieldDetailView.vue'
import AgentWorkspaceView from '../views/AgentWorkspaceView.vue'
import HistoryView from '../views/HistoryView.vue'
import TaskDetailView from '../views/TaskDetailView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginView },
    {
      path: '/',
      component: BasicLayout,
      redirect: '/dashboard',
      children: [
        { path: 'dashboard', component: DashboardView },
        { path: 'fields', component: FieldsView },
        { path: 'fields/:id', component: FieldDetailView },
        { path: 'agent', component: AgentWorkspaceView },
        { path: 'history', component: HistoryView },
        { path: 'history/:taskId', component: TaskDetailView }
      ]
    }
  ]
})

router.beforeEach((to) => {
  const hasToken = Boolean(storage.getToken())
  if (to.path === '/login' && hasToken) return '/dashboard'
  if (to.path !== '/login' && !hasToken) return '/login'
  return true
})

export default router
