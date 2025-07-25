import { createRouter, createWebHistory } from 'vue-router';
import MapPage from '../views/MapPage.vue';
import DataDisplay from '../views/DataDisplay.vue';


const routes = [
  {
    path: '/',
    redirect: '/map'
  },
  {
    path: '/map',
    name: 'Map',
    component: MapPage,
    meta: { title: '地图展示' }
  },
  {
    path: '/data',
    name: 'Data',
    component: DataDisplay,
    meta: { title: '查询过程展示' }
  },

];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;