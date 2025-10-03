import { createRouter, createWebHashHistory, RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    // name: 'Home', // 移除
    component: () => import('@/views/home.vue'),
    children: [
      {
        path: 'data-overview',
        name: 'DataOverview',
        component: () => import('@/views/DataOverview.vue'),
        meta: { title: '数据总览' },
      },
      {
        path: 'database-view',
        name: 'DatabaseView',
        component: () => import('@/views/DatabaseView.vue'),
        meta: { title: '数据库内容' },
      },
      {
        path: 'project-search',
        // name: 'ProjectSearch', // 移除
        component: () => import('@/views/ProjectSearch.vue'),
        meta: { title: '项目检索过程' },
        children: [
          {
            path: 'data',
            name: 'ProcessFlowDisplay',
            component: () => import('@/views/ProcessFlowDisplay.vue'),
            meta: { title: '检索流程展示' },
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
        path: 'theme',
        name: 'Theme',
        component: () => import('@/views/pages/theme.vue'),
        meta: { title: '主题设置' },
      },
      {
        path: 'obir-tree-realtime',
        name: 'OBIRTreeRealtime',
        component: () => import('@/views/OBIRTreeRealtimePage.vue'),
        meta: { title: 'OBIR-Tree实时路径' },
      },
      {
        path: 'obir-tree-display',
        name: 'OBIRTreeDisplay',
        component: () => import('@/views/OBIRTreeRealtimePage.vue'),
        meta: { title: 'PathORAM搜索前后改变展示' },
      },

      {
        path: '',
        redirect: 'data-overview',
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
