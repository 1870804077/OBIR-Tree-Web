import { createRouter, createWebHashHistory, RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    children: [
      {
        path: '/data-overview',
        name: 'DataOverview',
        component: () => import('@/views/DataOverview.vue'),
        meta: { title: '数据总览' },
      },
      {
        path: '/database-view',
        name: 'DatabaseView',
        component: () => import('@/views/DatabaseView.vue'),
        meta: { title: '数据库内容' },
      },
      {
        path: '/project-search',
        name: 'ProjectSearch',
        component: () => import('@/views/ProjectSearch.vue'),
        meta: { title: '项目检索过程' },
        children: [
          {
            path: 'data',
            name: 'ProcessDataDisplay',
            component: () => import('@/views/ProcessDataDisplay.vue'),
            meta: { title: '检索数据展示' },
          },
          {
            path: 'map',
            name: 'ProcessMapPage',
            component: () => import('@/views/ProcessMapPage.vue'),
            meta: { title: '检索地图展示' },
          },
          {
            path: '',
            redirect: 'data',
          },
        ],
      },
      {
        path: '/theme',
        name: 'Theme',
        component: () => import('@/views/pages/theme.vue'),
        meta: { title: '主题设置' },
      },
      {
        path: '',
        redirect: '/data-overview',
      },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/data-overview' },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

export default router;
