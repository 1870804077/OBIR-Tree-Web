import { createRouter, createWebHistory } from 'vue-router';
import MapPage from '../views/MapPage.vue';
import DataDisplay from '../views/DataDisplay.vue';

const routes = [
  { path: '/', redirect: '/map' },
  { path: '/map', name: 'Map', component: MapPage },
  { path: '/data', name: 'Data', component: DataDisplay }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  console.log(`路由导航开始: 从${from.path}到${to.path}`);
  next();
});

router.afterEach((to, from) => {
  console.log(`路由导航完成: 从${from.path}到${to.path}`);
});

export default router;
