//路由鉴权(某一路由什么条件下可以访问)
import router from '@/router'
import setting from '../setting'

import NProgress from 'nprogress'
import 'nprogress/nprogress.css'
// 获取用户相关的小仓库内部token数据,去判断用户是否登陆成功
import pinia from '../store'
import { useUserStore } from '../store/modules/user'

// 配置NProgress
NProgress.configure({ showSpinner: false })



// 全局守卫:项目当中任意路由切换都会触发的勾子   

// 全局前置守卫
router.beforeEach(async (to, _from) => {
    // 开始进度条
    NProgress.start()

    const userStore = useUserStore(pinia)
    const hasToken = userStore.token
    const hasUserInfo = !!userStore.username // 判断是否有用户信息

    // 情况 1: 有 Token
    if (hasToken) {
        if (to.path === '/login') {
            // 已登录却要去登录页 -> 重定向到首页
            // 等价于 next('/')
            return '/'
        }

        // 情况 1.1: 有 Token 但没用户信息 (刷新页面场景)
        if (!hasUserInfo) {
            try {
                // 获取用户信息 + 动态挂载路由
                await userStore.userInfo()

                // 【关键】：路由挂载完成后，必须重新触发一次导航

                // 注意：这里必须 return 一个目标地址对象，让路由器重新开始解析
                return { ...to, replace: true }

            } catch (error) {
                // 获取失败 (Token 过期等) -> 清除状态并跳回登录页
                await userStore.userLogout()
                // 等价于 next(`/login?redirect=${to.path}`)
                return `/login?redirect=${to.path}`
            }
        }

        // 情况 1.2: 有 Token 且有用户信息 -> 直接放行
        // 等价于 next()
        return true
    }

    // 情况 2: 没有 Token
    if (to.path === '/login') {
        // 没登录且在登录页 -> 放行
        return true
    } else {
        // 没登录且去其他页 -> 拦截去登录页
        // 等价于 next(`/login?redirect=${to.path}`)
        return `/login?redirect=${to.path}`
    }
})

// 全局后置守卫
router.afterEach((to, _from) => {
    // 结束进度条
    NProgress.done()

    // 更新页面标题
    if (to.meta && to.meta.title) {
        document.title = `${setting.title}- ${to.meta.title}`
    } else {
        document.title = setting.title
    }

})


// 第一个问题:任意路由切换实现进度条业务 ---nprogress
// 第二个问题:路由鉴权访问权限的设置
// 全部路由组件: 登录/404/任意路由/首页/数据大屏/权限管理3个/商品管理3个
// 用户未登录,只能访问login
// 用户登录成功:不可以访问login 指向首页


