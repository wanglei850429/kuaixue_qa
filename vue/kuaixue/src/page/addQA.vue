<template>
  <div id="addQA">
    <table width="90%" class="mytable">
        <tr>
          <td class='h1'>问题</td>
          <td><input type="text" name="question" v-model="question" placeholder="请输入问题" class="input"/></td>
        </tr>
        <tr>
          <td class='h1'>回答</td>
          <td><input type="text" name="answer" v-model="answer" placeholder="请输入回答" class="input"/></td>
        </tr>
    </table>
    <div class='question-form'>
        <button type="button" class="button" @click="_add"><span>追加</span></button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'addQA',
  data () {
    return {
      question:"",
      answer:""
    };
  },
  methods : {
    _add() {
      if (!this.question || !this.answer) {
        alert("请输入问题和回答");
        return;
      }
      let data = {
        question:this.question,
        answer:this.answer
      };
      this.axios.post('http://127.0.0.1:5000/QA/add/'+this.question+'/'+this.answer)
            .then((response)=>{
              this.question = "";
              this.answer = "";
              }).catch((response)=>{console.log(response)})
    }
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
.mytable {
  border-collapse: collapse;
  margin: 0 auto;
}
.mytable td, table th {
  border: 1px solid #cad9ea;
  color: #666;
  height: 30px;
}
.lefttd {
    text-align: left;
}
.mytable thead th{
  background-color: #CCE8EB;
}
.mytable tr:nth-child(odd){
  background: #fff;
}
.mytable tr:nth-child(even){
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
.input {
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
width: 480px;
margin-bottom: 5px;
position: relative;
 }
</style>