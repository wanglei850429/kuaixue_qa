import Vue from 'vue'
import VueRouter from 'vue-router'

// 引入组件
import QA from './page/QA'
import stopword from './page/stopword'
import userword from './page/userword'
import addQA from './page/addQA'

// 要告诉 vue 使用 vueRouter
Vue.use(VueRouter)

// 2. 定义路由
// 每个路由应该映射一个组件。
const routes = [
  {
    path: '/QA',
    component: QA
  },
  {
    path: '/stopword',
    component: stopword
  },
  {
    path: '/userword',
    component: userword
  },
  {
    path: '/addQA',
    component: addQA
  },
  {
    path: '/',
    redirect: '/QA'
  }
]


const router = new VueRouter({
  routes, 
  linkActiveClass: 'active'
})

export default router
