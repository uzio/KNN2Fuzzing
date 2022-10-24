import VueRouter from 'vue-router'
import Layout from './Layout'

export const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/workstation',
    name: '主界面',
    hidden: true
  },
  {
    path: '/login',
    component: () => import('@/views/login'),
    name: '登陆界面',
    hidden: true
  },
  {
    path: '/settings',
    name: '设置',
    icon: 'setting',
    hidden: true,
    component: Layout,
    children: [
      {
        path: '',
        component: () => import('@/views/settings')
      }
    ]
  },
  {
    path: '/workstation',
    name: '任务工作台',
    icon: 'console',
    component: Layout,
    children: [
      {
        path: '',
        component: () => import('@/views/workstation')
      },
      {
        path: 'job',
        component: () => import('@/views/fuzz/JobContainer'),
        children: [
          {
            path: 'case/:id',
            component: () => import('@/views/fuzz/CasePanel')
          },
          {
            path: 'fuzz/:id',
            component: () => import('@/views/fuzz/FuzzPanel')
          },
          {
            path: 'result/:id',
            component: () => import('@/views/fuzz/ResultPanel')
          }
        ]
      },
      {
        path: 'scan/:id',
        component: () => import('@/views/scan')
      }
    ]
  },
  {
    path: '/case',
    name: '用例库管理',
    icon: 'case',
    component: Layout,
    children: [
      {
        path: '',
        component: () => import('@/views/case/index')
      }
    ]
  },
  {
    path: '/vuls',
    name: '漏洞库管理',
    icon: 'vuls',
    component: Layout,
    children: [
      {
        path: '',
        component: () => import('@/views/vuls')
      }
    ]
  },
  {
    path: '/users',
    name: '用户管理',
    icon: 'users',
    component: Layout,
    children: [
      {
        path: '',
        component: () => import('@/views/users')
      }
    ]
  },
  {
    name: '404',
    path: '/404',
    hidden: true,
    component: () => import('@/views/404.vue')
  },
  {
    path: '*',
    redirect: '/',
    hidden: true
  }
]

export default new VueRouter({
  routes
})
