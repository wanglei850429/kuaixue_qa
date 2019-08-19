<template>
  <div id='app' class='appcls'>
    <div class='wrapper'>
      <v-header :QA="QA"></v-header>
      <nav class="nav">
        <li class="nav-item">
          <!-- router-link 定义点击后导航到哪个路径下 -->
          <router-link @click.native="clickTabQuery" v-bind:class="{'clicked':tab1}" to="/QA">提问</router-link>
        </li>
        <li class="nav-item">
          <router-link @click.native="clickTabAdd" v-bind:class="{'clicked':tab4}"  to="/addQA">追加问答对</router-link>
        </li>
        <li class="nav-item">
          <router-link @click.native="clickTabSW" v-bind:class="{'clicked':tab2}"  to="/stopword">追加/删除停用词</router-link>
        </li>
        <li class="nav-item">
          <router-link @click.native="clickTabUW" v-bind:class="{'clicked':tab3}"  to="/userword">追加/删除专用词</router-link>
        </li>
        <span class="nav-indicator"></span>
      </nav>
      <!-- 对应的组件内容渲染到router-view中 -->
      <router-view></router-view>
    </div>
    <app-footer></app-footer>
  </div>
</template>
<script>
import Footer from './page/footer'
export default {
  name: 'App',
  data () {
    return {
      tab1:false,
      tab2:false,
      tab3:false,
      tab4:false
    };
  },
  components: {
      'app-footer':Footer
  },methods:{
    clickTabQuery() {
      this.tab1 = true;
      this.tab2 = false;
      this.tab3 = false;
      this.tab4 = false;
    },
    clickTabSW() {
      this.tab1 = false;
      this.tab2 = true;
      this.tab3 = false;
      this.tab4 = false;
    },
    clickTabUW() {
      this.tab1 = false;
      this.tab2 = false;
      this.tab3 = true;
      this.tab4 = false;
    },
    clickTabAdd() {
      this.tab1 = false;
      this.tab2 = false;
      this.tab3 = false;
      this.tab4 = true;
    }
  }
}

</script>
<style>
@import './css/style.css';
/*  */
a.router-link-active,nav li a:hover {
    display: block;
    background: rgb(118, 201, 50);
    color: #fff;
    border-radius: 0 40px;
    text-shadow: none
  }
.wrapper{
   height: 100%;
}
.appcls{
  height: 100%;
}
.clicked{
  display: block;
  background: rgb(118, 201, 50);
  color: #fff;
  border-radius: 0 40px;
  text-shadow: none
}
</style>