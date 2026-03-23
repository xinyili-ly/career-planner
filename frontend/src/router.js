import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'
import JobRequirementsView from './views/JobRequirementsView.vue'
import JobDetailView from './views/JobDetailView.vue'
import StudentAbilitiesView from './views/StudentAbilitiesView.vue'
import CareerReportView from './views/CareerReportView.vue'
import AbilityTrainingPlanView from './views/AbilityTrainingPlanView.vue'
import AbilityTrainingPlanGeneratedView from './views/AbilityTrainingPlanGeneratedView.vue'
import CareerReportTemplateView from './views/CareerReportTemplateView.vue'
import ProfileView from './views/ProfileView.vue'
import ReportDetailView from './views/ReportDetailView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView
  },
  {
    path: '/jobs',
    name: 'JobRequirements',
    component: JobRequirementsView
  },
  {
    path: '/student-abilities',
    name: 'StudentAbilities',
    component: StudentAbilitiesView
  },
  {
    path: '/ability-training-plan',
    name: 'AbilityTrainingPlan',
    component: AbilityTrainingPlanView
  },
  {
    path: '/ability-training-plan/generated',
    name: 'AbilityTrainingPlanGenerated',
    component: AbilityTrainingPlanGeneratedView
  },
  {
    path: '/career-report',
    name: 'CareerReport',
    component: CareerReportView
  },
  {
    path: '/career-report-template',
    name: 'CareerReportTemplate',
    component: CareerReportTemplateView
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfileView
  },
  {
    path: '/report/:id',
    name: 'ReportDetail',
    component: ReportDetailView
  },
  {
    path: '/jobs/:id',
    name: 'JobDetail',
    component: JobDetailView,
    props: true
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

