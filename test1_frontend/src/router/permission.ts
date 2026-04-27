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
// 定义白名单路由（不需要用户信息的路由）
const whiteList = ['/login', '/404']

// 全局前置守卫
router.beforeEach(async (to, _from, next) => {
    NProgress.start()

    // 【新增】修复异常的 URL 格式
    if (window.location.href.includes('/login#/')) {
        console.warn('检测到异常 URL，正在修复...')
        const correctPath = window.location.href.replace('/login#/', '#/')
        window.location.href = correctPath
        return
    }

    const userStore = useUserStore(pinia)
    const hasToken = !!userStore.token
    const hasUserInfo = !!userStore.username

    console.log('路由守卫:', { path: to.path, hasToken, hasUserInfo })

    // 情况 1: 有 Token (已登录)
    if (hasToken) {
        // 如果已登录，访问登录页 -> 重定向到首页
        if (to.path === '/login') {
            NProgress.done()
            next('/')
            return
        }

        // 如果已登录，但没有用户信息
        if (!hasUserInfo) {
            try {
                await userStore.userInfo()
                next({ ...to, replace: true })
                return
            } catch (error) {
                console.error('获取用户信息失败:', error)
                await userStore.userLogout()
                next(`/login?redirect=${to.path}`)
                return
            }
        }

        // 正常情况：放行
        next()
        return
    }

    // 情况 2: 没有 Token (未登录)
    if (whiteList.includes(to.path)) {
        next()
    } else {
        next(`/login?redirect=${to.path}`)
    }
})

// 全局后置守卫
router.afterEach((to, _from) => {
    NProgress.done()

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


