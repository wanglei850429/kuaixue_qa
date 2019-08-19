<template>
  <div id="stopword">
    <div class='question-form'>
        <input type="text" name="word" v-model="word" placeholder="请输入停用词" class="stopword_input"/>
        <button type="button" class="button" @click="_insert"><span>追加</span></button>
        <button type="button" class="button" @click="_delete"><span>删除</span></button>
    </div>
    <table width="90%" class="table">
        <thead>
            <tr>
                <th>#</th>
                <th>停用词</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="(item,index) in dataList">
                <td>{{index+1}}</td>
                <td>{{item.word}}</td>
            </tr>
        </tbody>
    </table>
  </div>
</template>
<script>
export default {
  name: 'stopword',
  data () {
    return {
      word:"",
      dataList:[]
    };
  },
  mounted : function(){
    this.axios.get('http://127.0.0.1:5000/QA/stop_word/0')
        .then((response)=>{
            this.dataList = response.data
            }).catch((response)=>{console.log(response)})
  },
  methods : {
    _insert() {
      if (!this.word) {
        alert("请输入停用词");
        return;
      }
      for (let i=0;i<this.dataList.length;i++) {
          if (this.dataList[i]['word']==this.word) {
              alert("该停用词已存在");
              return;
          }
      }
      let data = {
        word:this.word
      };
      this.axios.post('http://127.0.0.1:5000/QA/stop_word/'+this.word)
            .then((response)=>{
              this.dataList = response.data
              }).catch((response)=>{console.log(response)})
      this.word = ""
    },
    _delete() {
      if (!this.word) {
        alert("请输入停用词");
        return;
      }
      let exists = false
      for (let i=0;i<this.dataList.length;i++) {
          if (this.dataList[i]['word']==this.word) {
              exists = true
              break;
          }
      }
      if (!exists) {
          alert("该停用词不存在");
          return
      }
      let data = {
        word:this.word
      };
      this.axios.delete('http://127.0.0.1:5000/QA/stop_word/'+this.word)
            .then((response)=>{
              this.dataList = response.data
              }).catch((response)=>{console.log(response)})
      this.word = ""
    },
  }

}

</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

h1, h2 {
  font-weight: normal;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: inline-block;
  margin: 0 10px;
}

a {
  color: #42b983;
}
.table {
  border-collapse: collapse;
  margin: 0 auto;
  text-align: center;
}
.table td, table th {
  border: 1px solid #cad9ea;
  color: #666;
  height: 30px;
}
.table thead th{
  background-color: #CCE8EB;
  width: 100px;
}
.table thead,tbody tr {
	display:table;
	width:500px;
	table-layout:fixed;
}

.table tbody{
    display:block;
    height:250px;
	width:500px;
    overflow-y:scroll;
    height:400px;
}
.table tr:nth-child(odd){
  background: #fff;
}
.table tr:nth-child(even){
  background: #F5FAFA;
}
 .button {
position: relative;
display: inline-block;
margin: 5px;
padding: 7px 15px;
font-size: 13px;
font-weight: bold;
color: #333;
text-shadow: 0 1px 0 rgba(255,255,255,0.9);
white-space: nowrap;
background-color: #eaeaea;
background-image: -moz-linear-gradient(#fafafa, #eaeaea);
background-image: -webkit-linear-gradient(#fafafa, #eaeaea);
background-image: linear-gradient(#fafafa, #eaeaea);
background-repeat: repeat-x;
border-radius: 3px;
border: 1px solid #ddd;
border-bottom-color: #c5c5c5;
box-shadow: 0 1px 3px rgba(0,0,0,.05);
vertical-align: middle;
cursor: pointer;
-moz-box-sizing: border-box;
box-sizing: border-box;
-webkit-touch-callout: none;
-webkit-user-select: none;
-khtml-user-select: none;
-moz-user-select: none;
-ms-user-select: none;
user-select: none;
-webkit-appearance: none;
 }
 .button:hover,
 .button:active {
background-position: 0 -15px;
border-color: #ccc #ccc #b5b5b5;
 }
 .button:active {
background-color: #dadada;
border-color: #b5b5b5;
background-image: none;
box-shadow: inset 0 3px 5px rgba(0,0,0,.15);
 }
 .button:focus,
 input[type=text]:focus{
outline: none;
border-color: #51a7e8;
box-shadow: inset 0 1px 2px rgba(0,0,0,.075), 0 0 5px rgba(81,167,232,.5);
 }
.stopword_input{
font-size: 13px;
min-height: 32px;
margin: 0;
padding: 7px 8px;
outline: none;
color: #333;
background-color: #fff;
background-repeat: no-repeat;
background-position: right center;
border: 1px solid #ccc;
border-radius: 3px;
box-shadow: inset 0 1px 2px rgba(0,0,0,0.075);
-moz-box-sizing: border-box;
box-sizing: border-box;
transition: all 0.15s ease-in;
-webkit-transition: all 0.15s ease-in 0;
vertical-align: middle;
width: 100px;
margin-bottom: 5px;
position: relative;
 }
</style>