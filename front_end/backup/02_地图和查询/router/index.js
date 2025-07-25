import { createRouter, createWebHistory } from 'vue-router';
import MapPage from '../views/MapPage.vue';
import DataDisplay from '../views/DataDisplay.vue';
import SummaryPage from '../views/SummaryPage.vue';

const routes = [
  {
    path: '/',
    redirect: '/map'
  },
  {
    path: '/map',
    name: 'Map',
    component: MapPage,
    meta: { title: '地图查看' }
  },
  {
    path: '/data',
    name: 'Data',
    component: DataDisplay,
    meta: { title: '数据展示' }
  },
  {
    path: '/summary',
    name: 'Summary',
    component: SummaryPage,
    meta: { title: '总结页面' }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;