import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import TicketsView from '../views/TicketsView.vue'
import CreateTicketView from '../views/CreateTicketView.vue'
import TicketDetailView from '../views/TicketDetailView.vue'
import AdminPanelView from '../views/AdminPanelView.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: LoginView },
  { path: '/tickets', component: TicketsView },
  { path: '/tickets/create', component: CreateTicketView },
  { path: '/tickets/:id', component: TicketDetailView, props: true },
  { path: '/admin', component: AdminPanelView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const access = localStorage.getItem("access")

  if (to.path !== "/login" && !access) {
    next("/login")
  } else {
    next()
  }
})

export default router