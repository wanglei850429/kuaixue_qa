import Vue from 'vue'
import App from './App.vue'
import axios from 'axios'
import VueAxios from 'vue-axios'
import VueRouter from 'vue-router'
import router from './router'
import script from './js/script'
Vue.use(VueAxios,axios)
let vm = new Vue({
  router,
  el: '#app',
  render: h => h(App)
})
Vue.use({vm})