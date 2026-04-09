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
  <!-- 根容器需要设置为相对定位，作为绝对定位 footer 的参考点 -->
  <div class="login_root">
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

    <!-- 底部备案号区域：使用绝对定位覆盖在 container 上 -->
    <footer class="site-footer">
      <div class="footer-content">
        <!-- 公安备案 -->
        <a href="你的公安链接" target="_blank" class="footer-link">
          <img src="@/assets/images/gongan.png"
            style="width: 16px; height: 16px; display: inline-block; vertical-align: middle; margin-right: 4px; border: 0;"
            alt="" />
          浙公网安备33010902004606号
        </a>

        <span class="divider">|</span>

        <!-- 工信部备案 -->
        <a href="https://beian.miit.gov.cn/" target="_blank" class="footer-link">
          浙ICP备2026020450号-1
        </a>
      </div>
    </footer>
  </div>
</template>

<style scoped lang="scss">
.login_root {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.login_container {
  width: 100%;
  height: 100vh;
  background: url('@/assets/images/background.jpg') no-repeat;
  background-size: cover;
  position: relative;
  z-index: 1;
}

/* 表单样式保持不变... */
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

/* ================= 核心修改区域 ================= */

.site-footer {
  position: absolute;
  bottom: 20px;
  /* 稍微往上提一点，不要太贴边，更美观 */
  left: 0;
  width: 100%;
  z-index: 999;

  /* 去掉所有背景色和边框 */
  background-color: transparent;
  border: none;
  box-shadow: none;

  .footer-content {
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 12px;

    /* 关键：文字阴影，保证在浅色背景图上也能看清 */
    color: rgba(255, 255, 255, 0.9);
    /* 默认白色文字 */
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
    /* 黑色半透明阴影 */

    .divider {
      margin: 0 10px;
      opacity: 0.6;
      /* 分隔符淡一点 */
    }

    .footer-link {
      /* 继承父级的白色文字 */
      color: inherit;
      text-decoration: none;
      transition: all 0.3s;

      &:hover {
        color: #fff;
        /* 悬停变亮白 */
        text-shadow: 0 0 8px rgba(255, 255, 255, 0.8);
        /* 悬停发光效果 */
      }
    }
  }
}
</style>