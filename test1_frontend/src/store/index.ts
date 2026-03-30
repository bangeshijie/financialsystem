// 仓库大仓库
import { createPinia } from "pinia";
//  导入pinia持久化插件
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

const pinia = createPinia();
// 使用插件
pinia.use(piniaPluginPersistedstate)

export default pinia;