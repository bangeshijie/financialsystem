//通过vue-router插件实现模板路由配置
import { createRouter, createWebHashHistory } from 'vue-router'
import { constantRoutes } from './routes'


//创建路由对象
const router = createRouter({
    //配置路由规则
    history: createWebHashHistory(),
    routes: constantRoutes,
    //配置滚动行为
    scrollBehavior() {
        // 始终滚动到顶部
        return {
            left: 0,
            top: 0
        }
    },

})
//对外暴露路由对象
export default router

