//进行axios  二次 封装
import axios from 'axios'
import { ElMessage } from 'element-plus'
// 引入用户相关的仓库
import { useUserStore } from '@/store/modules/user'
import router from '@/router'

// 第一步  利用axios 对象的create方法，创建一个axios实例
const request = axios.create({
    //基础路径，发请求的时候，基础路径当中会出现api
    baseURL: import.meta.env.VITE_APP_BASE_API,
    //请求超时时间5秒
    timeout: 5000,
})

// 第二部 request实例添加请求拦截器
request.interceptors.request.use((config) => {
    //获取用户相关的小仓库:获取仓库内部token,登陆成功后携带给服务器
    let UserState = useUserStore()
    if (UserState.token) {
        //config配置对象，对象里面有个属性很重要，headers请求头
        //给请求头添加token验证的字段
        config.headers.Authorization = `Bearer ${UserState.token}`
    }


    return config
},
    (error) => {
        //请求失败 进这里
        return Promise.reject(error)
    }
)
// 第三步 request实例添加响应拦截器
request.interceptors.response.use(
    (response) => {
        //响应成功 进这里
        return response.data
    },
    (error) => {
        //响应失败 进这里
        const userStore = useUserStore()

        // 判断是否有响应数据（后端返回了错误信息）
        if (error.response && error.response.data) {
            const responseData = error.response.data


            // 特殊处理 401 未授权
            if (error.response.status === 401) {
                // 清空仓库中的 token
                userStore.$patch({ token: '' })
                localStorage.removeItem('token')

                // 跳转回登录页
                if (router.currentRoute.value.path !== '/login') {
                    router.replace('/login')
                }
            }

            // 🔴 关键修改：返回后端的错误数据，而不是完整的 error 对象
            return Promise.reject(responseData)
        }

        // 如果没有响应数据（网络错误等）
        let message = ''
        let status = error.response?.status
        switch (status) {
            case 400:
                message = '请求错误(400)'
                break
            case 403:
                message = '拒绝访问(403)'
                break
            case 404:
                message = '请求出错(404)'
                break
            case 408:
                message = '请求超时(408)'
                break
            case 500:
                message = '服务器错误(500)'
                break
            case 501:
                message = '服务未实现(501)'
                break
            case 502:
                message = '网络错误(502)'
                break
            case 503:
                message = '服务不可用(503)'
                break
            case 504:
                message = '网络超时(504)'
                break
            case 505:
                message = 'HTTP版本不受支持(505)'
                break
            default:
                message = '连接服务器失败'
        }

        ElMessage({
            message: message,
            type: 'error',
            duration: 5 * 1000,
        })

        // 返回错误信息对象
        return Promise.reject({
            code: status || 500,
            message: message,
            data: null,
            ok: false
        })
    }
)
// console.log(axios)
// console.log(request)

// 对外暴露request实例对象
export default request
