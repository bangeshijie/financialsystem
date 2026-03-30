// 小仓库 :layout组件相关配置的仓库
import { defineStore } from 'pinia'
const useLayoutSettingStore = defineStore('SettingStore', {
    state: () => {
        // 用户菜单控制折叠还是打开切换的变量
        return {
            fold: false,
            refsh: false,//用于控制刷新按钮实现
        }
    }
})


export default useLayoutSettingStore