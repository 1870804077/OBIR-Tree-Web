import { Menus } from '@/types/menu';

export const menuData: Menus[] = [
  {
    id: '1',
    title: '数据总览',
    index: '/data-overview',
    icon: 'Odometer',
  },
  {
    id: '2',
    title: '数据库内容',
    index: '/database-view',
    icon: 'Calendar',
  },
  {
    id: '3',
    title: '项目检索过程',
    index: '/project-search',
    icon: 'PieChart',
    children: [
      {
        id: '31',
        pid: '3',
        index: '/project-search/data',
        title: '检索数据展示',
      },
      {
        id: '32',
        pid: '3',
        index: '/project-search/map',
        title: '检索地图展示',
      },
    ],
  },
];
