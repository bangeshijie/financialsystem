// 创建用户相关小仓库
import { defineStore } from "pinia";
import { ref } from "vue";

// 引入接口
import { reqLogin, reqUserInfo, reqLogout, reqChangePassword } from "@/api/user";
// 引入数据类型
import type { loginFormData, loginResponseData, userInfoResponseData, updatePasswordData, updatePasswordResponseData } from '@/api/user/type';

// 引入本地存储封装函数
import { setToken, getToken, removeToken } from "@/utils/token";
// 引入路由(常量路由)
import { constantRoutes, asyncRoutes, anyRoutes } from "@/router/routes";

// 注意：如果 types/type.ts 中定义了 UserState 接口，可以保留引用用于类型检查，
// 但在 Setup Store 中，我们通常直接通过 ref 的类型推断来管理状态类型。⭐组合式api写法不显式使用
// import type { UserState } from "./types/type";


// 引入深拷贝方法
// @ts-ignore
import cloneDeep from 'lodash/cloneDeep'

import router from '@/router'

// 用于过滤当前用户需要展示的异步路由
function filterAsyncRoutes(asyncRoutes: any, routes: any) {

    return asyncRoutes.filter((item: any) => {
        if (routes.includes(item.name)) {
            if (item.children && item.children.length > 0) {
                item.children = filterAsyncRoutes(item.children, routes)
            }
            return true
        }
        return false
    })
}

/**
 * 深拷贝路由配置（完整保留所有属性，包括函数和嵌套结构）验证可用!!!!这里还是引用cloneDeep   
 */
// function cloneDeep(routes: any[]): any[] {
//     if (!routes || !Array.isArray(routes)) return [];

//     return routes.map(route => {
//         // 创建新对象，拷贝所有属性
//         const clonedRoute: any = {};

//         // 拷贝所有自有属性
//         for (const key in route) {
//             if (Object.prototype.hasOwnProperty.call(route, key)) {
//                 const value = route[key];

//                 // 处理数组（主要是 children）
//                 if (Array.isArray(value)) {
//                     clonedRoute[key] = cloneRoutes(value);
//                 }
//                 // 处理对象（但不处理函数和特殊对象）
//                 else if (value && typeof value === 'object' && !(value instanceof Function)) {
//                     // 简单对象，浅拷贝即可（如 meta）
//                     clonedRoute[key] = { ...value };
//                 }
//                 // 其他类型（string, number, boolean, function 等）直接赋值
//                 else {
//                     clonedRoute[key] = value;
//                 }
//             }
//         }

//         return clonedRoute;
//     });
// }

export const useUserStore = defineStore("user", () => {
    // =======================
    // 1. State (状态)
    // 使用 ref 定义响应式数据
    // =======================

    // 存储 token，初始化时尝试从本地获取
    const token = ref<string>(getToken() || '');

    // 仓库生成路由菜单数组，初始化为常量路由
    const menuRoutes = ref(constantRoutes);

    const username = ref<string>('');
    const bio = ref<string>('');
    const avatar = ref<string>('');
    const email = ref<string>('');
    const gender = ref<string>('');

    // 存储用户按钮权限
    const buttons = ref<string[]>([]);
    const routes = ref<string[]>([]);
    const roles = ref<string[]>([]);

    // =======================
    // 2. Actions (行为/方法)
    // 使用 const + 箭头函数定义
    // =======================









    /**
     * 用户登录
     * @param data 登录表单数据
     * @returns Promise<string> 成功返回 'ok'，失败 reject 错误
     */
    const useLogin = async (data: loginFormData): Promise<string> => {
        try {
            // 发送登录请求
            const result: loginResponseData = await reqLogin(data);

            // 登录成功 (code == 200)
            if (result.code == 200) {
                const newToken = result.data.token;

                // 更新 state (注意 .value)
                token.value = newToken;


                // 持久化存储 token 
                setToken(newToken);

                return 'ok';
            } else {
                // 业务逻辑错误，返回 rejected promise
                return Promise.reject(new Error(result.data as string));
            }
        } catch (error) {
            // 网络异常或其他未捕获错误
            return Promise.reject(error);
        }
    };

    /**
     * 获取用户信息
     * @returns Promise<string> 成功返回 'ok'，失败 reject 错误
     */
    const userInfo = async (): Promise<string> => {
        try {
            // 发送获取用户信息请求
            const result: userInfoResponseData = await reqUserInfo();

            if (result.code === 200) {

                // 1.更新 更新基础用户信息 
                username.value = result.data.username;
                bio.value = result.data.bio;

                avatar.value = result.data.avatar;
                gender.value = result.data.gender;
                email.value = result.data.email;
                buttons.value = result.data.buttons || [];
                routes.value = result.data.routes || [];
                roles.value = result.data.roles || [];
                // 2. 使用深拷贝防止污染原始 asyncRoutes 数组
                const userAsyncRoutes = filterAsyncRoutes(cloneDeep(asyncRoutes), result.data.routes);
                // 3. 生成完整的菜单路由 (用于侧边栏渲染)
                menuRoutes.value = [...constantRoutes, ...userAsyncRoutes, ...anyRoutes];
                // 4. 【核心修改】动态挂载路由
                // 只挂载当前用户有权访问的路由 (userAsyncRoutes) 和 任意路由 (anyRoutes)
                // 不要挂载所有的 asyncRoutes，否则没权限的人也能通过 URL 访问
                const routesToAdd = [...userAsyncRoutes, ...anyRoutes];

                routesToAdd.forEach(route => {
                    // 检查是否已存在该名称的路由，避免重复添加 (虽然刷新后 store 重置通常不会重复，但做个防御更好)
                    if (!router.hasRoute(route.name)) {
                        router.addRoute(route);
                    }
                });

                console.log('动态路由挂载完成，当前路由表:', router.getRoutes().map(r => r.name));

                return 'ok';
            } else {
                return Promise.reject(result.message || '获取用户信息失败');
            }
        } catch (error) {
            console.error('userInfo action error:', error);
            return Promise.reject(error);
        }
    };

    /**
     * 退出登录
     * @returns Promise<string> 成功返回 'ok'，失败 reject 错误
     */
    const userLogout = async (): Promise<void> => {
        try {
            // 1. 尝试调用后端退出 (即使失败也要继续执行前端清理)
            await reqLogout().catch(() => { });
        } finally {
            // 2. 清理 Token
            removeToken();

            // 3. 重置 Store 所有状态
            token.value = '';
            username.value = '';
            avatar.value = '';
            bio.value = '';
            email.value = '';
            gender.value = '';
            buttons.value = [];
            routes.value = [];
            roles.value = [];
            menuRoutes.value = constantRoutes;

            // 4. 【核心】强制刷新页面或重定向到登录页
            // 使用 location.href 会完全重新加载页面，彻底清除组件缓存
            // 这样下一个用户登录时，是一个全新的应用实例
            window.location.href = '/login';

            // 注意：执行了 location.href 后，后面的代码不会执行，Promise 也不会 resolve
            // 所以这里不需要 return 'ok'，因为页面已经跳走了
        }
    };

    // 修改密码
    const changePassword = async (data: updatePasswordData): Promise<string> => {
        try {
            const result: updatePasswordResponseData = await reqChangePassword(data);

            if (result.code === 200) {

                await userLogout();

                return 'ok';
            } else {
                return Promise.reject(new Error(result.message));
            }
        } catch (error) {
            return Promise.reject(error);
        }
    };

    // =======================
    // 3. Getters (计算属性) - 可选
    // 如果有需要，可以使用 computed
    // =======================
    // import { computed } from 'vue';
    // const isLoggedIn = computed(() => !!token.value);

    // =======================
    // 4. Return (暴露给外部)
    // Setup Store 必须手动返回需要暴露的属性和方法
    // =======================
    return {
        // State
        token,
        menuRoutes,
        username,
        avatar,
        gender,

        bio,
        email,
        roles,
        buttons,
        routes,

        // Actions
        useLogin,
        userInfo,
        userLogout,
        changePassword,

        // Getters (如果有)
        // isLoggedIn
    };
});   