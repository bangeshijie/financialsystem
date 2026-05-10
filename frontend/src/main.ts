import { createApp } from 'vue'

// 引入模板的全局样式
import '@/styles/index.scss'

import App from './App.vue'

import ElementPlus from 'element-plus';

import 'element-plus/dist/index.css'
//@ts-ignore忽略当前文件ts类型的检测否则有红色提示(打包会失败)
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
// 引入 element-plus 暗黑模式
import 'element-plus/theme-chalk/dark/css-vars.css'

import globalComponent from '@/components/index.ts'
// 引入路由对象
import router from '@/router/index.ts'


// 引入模板的全局样式
import '@/styles/index.scss'

//引入pinia仓库

import pinia from '@/store/index.ts'


// 引入路由鉴权文件
import './router/permission'
// 注册自定义指令
import { permission, permissionHide } from './directives/permission'


const app = createApp(App)
app.use(ElementPlus, {
    locale: zhCn
})



//注册pinia仓库
app.use(pinia)

// 注册全局组件
app.use(globalComponent)

// 注册全局指令
app.directive('permission', permission)
app.directive('permission-hide', permissionHide)

//注册路由  
app.use(router)





app.mount('#app')
