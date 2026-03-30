<script setup lang="ts">
import { User, Lock } from '@element-plus/icons-vue';
import { reactive, ref } from 'vue';
//引入用户相关仓库
import { useUserStore } from '@/store/modules/user';

import { useRouter, useRoute } from 'vue-router'
import { ElNotification } from 'element-plus';
// 引入获取当前时间的函数
import { getTimeState } from '@/utils/time';

// 引入自定义表单校验规则函数
import { validateUsername, validatePassword } from '@/utils/validation';



// 获取el-form组件
const loginFormdata = ref();

//获取路由器
const $router = useRouter()
//获取路由对象
const $route = useRoute()


// 定义登录按钮加载转圈loading 响应变量
const loading = ref(false);


const userStore = useUserStore();
// 收集账号和数据
const loginForm = reactive({ username: '', password: '' });
// 登录按钮回调
const handleLogin = async () => {

  //表单校验
  await loginFormdata.value.validate();

  //显示登录加载效果
  loading.value = true;
  try {
    await userStore.useLogin(loginForm);
    //编程导航跳转到首页
    // 判断登录的时候,路由路径是否有query参数  有的话跳转到对应的页面 没有就跳转到首页
    let redirect = $route.query.redirect as string;
    $router.push({ path: redirect || '/' });
    ElNotification({
      title: `hi~${getTimeState()}`,
      message: '欢迎回来',
      type: 'success',
    });
    // 登录成功加载效果也消失
    loading.value = false;

  } catch (error) {
    // 登录失败加载loading效果消失
    loading.value = false;
    console.log(error);
    ElNotification({
      title: '错误',
      message: (error as Error).message,
      type: 'error',
    });

  }
}




//定义表单校验规则     blur 代表输入框失去焦点时触发验证  还有一个选项change 代表值改变时触发验证
const rules = {
  username: [
    // { required: true, message: '请输入用户名', trigger: 'blur' },
    // { min: 4, max: 12, message: '长度在4到12个字符', trigger: 'blur' }
    { trigger: 'blur', validator: validateUsername }
  ],
  password: [
    // { required: true, message: '请输入密码', trigger: 'blur' },
    // { min: 6, max: 16, message: '长度在6到16个字符', trigger: 'blur' }
    { trigger: 'blur', validator: validatePassword }
  ]
};



</script>

<template>
  <div class="login_container">
    <el-row>
      <el-col :span="12" :xs="0"></el-col>
      <el-col :span="12" :xs="24">
        <el-form class="login_form" :model="loginForm" :rules="rules" ref="loginFormdata">
          <h1>hello</h1>
          <h2>欢迎来到XX财务管理平台</h2>
          <el-form-item prop="username">
            <el-input :prefix-icon="User" placeholder="请输入用户名" v-model="loginForm.username"></el-input>
          </el-form-item>
          <el-form-item prop="password">
            <el-input type="password" :prefix-icon="Lock" placeholder="请输入密码" show-password
              v-model="loginForm.password"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button :loading="loading" class="login_btn" type="primary" size="default"
              @click="handleLogin">登录</el-button>
          </el-form-item>

        </el-form>


      </el-col>
    </el-row>

  </div>

</template>

<style scoped lang="scss">
.login_container {
  width: 100%;
  height: 100vh;
  background: url('@/assets/images/background.jpg') no-repeat;
  background-size: cover;
}

.login_form {
  position: relative;
  width: 80%;
  top: 30vh;
  background: url("@/assets/images/login_form.png") no-repeat;
  background-size: cover;
  padding: 40px;

  h1 {
    color: white;
    font-size: 40px;
  }

  h2 {
    color: white;
    font-size: 20px;
    margin-bottom: 30px;
  }
}

.login_btn {
  width: 100%;
}
</style>
