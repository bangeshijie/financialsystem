<template>

    <el-button type="primary" size="small" icon="Refresh" circle @click="updateRefsh"
        style="background-color: transparent; border-color: transparent;"></el-button>
    <el-button type="primary" size="small" icon="FullScreen" circle @click="fullScreen"
        style="background-color: transparent; border-color: transparent;"></el-button>

    <!--  弹出框-->
    <el-popover placement="bottom" title="主题切换" :width="200" trigger="hover">
        <el-form>
            <el-form-item label="主题颜色" key="theme-color-item">
                <el-color-picker @change="setColor" v-model="color" size="default" show-alpha
                    :predefine="predefineColors" :teleported="false" />
            </el-form-item>
            <el-form-item label="暗黑模式" key="dark-mode-item">
                <el-switch @change="changeDark" v-model="dark" size="default" active-icon="Moon" inactive-icon="Sunny"
                    inline-prompt />
            </el-form-item>
        </el-form>

        <template #reference>

            <el-button type="primary" size="small" icon="Setting" circle
                style="background-color: transparent; border-color: transparent;"></el-button>
        </template>
    </el-popover>

    <img :src="userStore.avatar" alt="" style="width: 24px;height: 24px;margin: 0px 12px; border-radius: 50%;">
    <!-- 登陆头像下拉菜单 -->
    <el-dropdown>
        <span class="el-dropdown-link">
            {{ userStore.username }}
            <el-icon class="el-icon--right">
                <arrow-down />
            </el-icon>
        </span>
        <template #dropdown>
            <el-dropdown-menu>
                <el-dropdown-item @click="changepwd">修改密码</el-dropdown-item>
                <el-dropdown-item @click="logout">退出登录</el-dropdown-item>

            </el-dropdown-menu>
        </template>
    </el-dropdown>


    <!-- ================= 修改密码弹窗 (合并在此处) ================= -->
    <el-dialog v-model="dialogVisible" title="修改密码" width="400px" :close-on-click-modal="false" @close="resetPwdForm"
        :teleported="true" append-to-body :z-index="20260302" top="15vh">
        <el-form ref="pwdFormRef" :model="pwdFormData" :rules="pwdRules" label-width="80px" size="default">
            <el-form-item label="旧密码" prop="oldPassword">
                <el-input v-model="pwdFormData.oldPassword" type="password" placeholder="请输入当前密码" show-password
                    autocomplete="off" />
            </el-form-item>

            <el-form-item label="新密码" prop="newPassword">
                <el-input v-model="pwdFormData.newPassword" type="password" placeholder="请输入新密码" show-password
                    autocomplete="off" />
            </el-form-item>

            <el-form-item label="确认密码" prop="confirmPassword">
                <el-input v-model="pwdFormData.confirmPassword" type="password" placeholder="请再次输入新密码" show-password
                    autocomplete="off" />
            </el-form-item>
        </el-form>

        <template #footer>
            <span class="dialog-footer">
                <el-button @click="dialogVisible = false">取消</el-button>
                <el-button type="primary" :loading="pwdLoading" @click="handlePwdSubmit">
                    确定
                </el-button>
            </span>
        </template>
    </el-dialog>
    <!-- ================= 修改密码弹窗结束 ================= -->

</template>



<script setup lang="ts">
// 定义组件名
defineOptions({
    name: 'Setting'
})
import { useRouter, useRoute } from 'vue-router';

import { ref, onMounted, reactive } from 'vue'

import useLayoutSettingStore from '@/store/modules/setting';
import { validatePassword } from '@/utils/validation';
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'


let layoutSettingStore = useLayoutSettingStore();

// 获取用户相关的小仓库
import { useUserStore } from '@/store/modules/user';
let userStore = useUserStore()

//获取路由器对象
const $router = useRouter();
// 获取路由对象
const $route = useRoute();
// 刷新按钮点击回调
const updateRefsh = () => {
    layoutSettingStore.refsh = !layoutSettingStore.refsh;
}

// 全屏按钮 点击回调
const fullScreen = () => {
    // dom的一个属性,用来判断当前是否是全屏模式  全屏true 非全屏 false
    let full = document.fullscreenElement;
    if (!full) {
        //文档根节点方法 requestFullscreen  实现全屏模式
        document.documentElement.requestFullscreen()
    } else {
        // 退出全屏模式 
        document.exitFullscreen();
    }
}

// 修改密码
// --- 修改密码相关逻辑 (新增) ---

// 1. 控制弹窗显示
const dialogVisible = ref(false)
const pwdLoading = ref(false)
const pwdFormRef = ref<FormInstance>()

// 2. 表单数据
const pwdFormData = reactive({
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
})

// 3. 自定义验证器：确认密码一致性
const validateConfirmPassword = (_rule: any, value: string, callback: any) => {
    if (value === '') {
        callback(new Error('请再次输入密码'))
    } else if (value !== pwdFormData.newPassword) {
        callback(new Error('两次输入的密码不一致'))
    } else {
        callback()
    }
}

// 4. 表单验证规则
const pwdRules = reactive<FormRules>({
    oldPassword: [
        { required: true, message: '请输入旧密码', trigger: 'blur' },
        // 复用已有的 validatePassword 逻辑进行基础校验 (长度、字符类型等)
        { validator: validatePassword, trigger: 'blur' }
    ],
    newPassword: [
        { required: true, message: '请输入新密码', trigger: 'blur' },
        // 复用已有的 validatePassword 逻辑
        { validator: validatePassword, trigger: 'blur' }
    ],
    confirmPassword: [
        { required: true, validator: validateConfirmPassword, trigger: 'blur' }
    ]
})

// 5. 打开弹窗
const changepwd = () => {

    dialogVisible.value = true

}

// 6. 重置表单
const resetPwdForm = () => {
    if (pwdFormRef.value) {
        pwdFormRef.value.resetFields()
    }
    pwdFormData.oldPassword = ''
    pwdFormData.newPassword = ''
    pwdFormData.confirmPassword = ''
}

// 7. 提交处理 (修复版：使用 Promise 模式)
const handlePwdSubmit = async () => {
    if (!pwdFormRef.value) return

    try {
        // 1. 表单验证 (推荐写法：直接 await，失败会 throw 错误)
        await pwdFormRef.value.validate()

        // 2. 验证通过，开始加载
        pwdLoading.value = true

        // 3. 构造提交数据 (如果接口不需要 confirmPassword，这里需要剔除)

        const { confirmPassword, ...submitData } = pwdFormData;



        // 4. 调用 Store Action (核心逻辑在这里)
        // Store 内部会自动处理：请求接口 -> 成功则自动登出 -> 返回 'ok'
        await userStore.changePassword(submitData as any);

        // 5. 成功后的反馈 (如果 Store 里已经做了跳转，这里可能不会执行到，视 Store 实现而定)
        // 建议：Store 只负责数据和状态，View 负责跳转和提示，或者统一在 Store 处理。
        // 根据你的 Store 代码，changePassword 内部调用了 userLogout 但没有跳转路由。
        // 所以这里需要处理跳转。

        ElMessage.success('密码修改成功，已退出登录，请重新登录')
        dialogVisible.value = false

        // 确保跳转到登录页
        $router.push({
            path: '/login',
            query: { redirect: $route.fullPath }
        })

    } catch (error: any) {
        // 捕获验证错误或接口请求错误
        if (error.message) {
            // 如果是接口返回的业务错误 (Store reject 出来的)
            ElMessage.error(error.message)
        } else {
            // 如果是验证失败或其他未知错误
            // 验证失败通常 element 会自己处理红色边框提示，这里可以不打全局 msg，或者打一个通用的
            console.log('提交失败或验证未通过', error)
        }
    } finally {
        pwdLoading.value = false
    }
}

// 退出登录
const logout = async () => {
    try {
        // 先清除 store 状态和本地存储，但不进行页面跳转
        await userStore.userLogout();

        // 注意：userStore.userLogout() 中不应该有 window.location.href 跳转
        // 如果已经有，需要先修改 userStore.userLogout()

        // 使用 replace 而不是 push，避免产生历史记录
        await $router.replace({
            path: '/login',
            query: { redirect: $route.fullPath }
        });

        ElMessage.success('已退出登录');
    } catch (error) {
        console.error('退出失败:', error);
        ElMessage.error('退出失败');
    }
}

// switch暗黑模式 方法
const changeDark = () => {
    // 获取html根节点
    const html = document.documentElement
    if (dark.value) {
        html.className = 'dark'
        // 设置 CSS 变量
        html.setAttribute('data-theme', 'dark')
        // 保存到 localStorage
        localStorage.setItem('theme', 'dark')
    } else {
        html.className = ''
        html.removeAttribute('data-theme')
        localStorage.setItem('theme', 'light')
    }
    // 触发自定义事件，通知其他组件主题已改变
    window.dispatchEvent(new CustomEvent('theme-change', { detail: { theme: dark.value ? 'dark' : 'light' } }))
}

// 从 localStorage 读取主题设置
onMounted(() => {
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme === 'dark') {
        dark.value = true
        changeDark() // 应用暗黑模式
    }
})



const dark = ref<boolean>(false)
const color = ref('rgba(255, 69, 0, 0.68)')
const predefineColors = ref([
    '#ff4500',
    '#ff8c00',
    '#ffd700',
    '#90ee90',
    '#00ced1',
    '#1e90ff',
    '#c71585',
    'rgba(255, 69, 0, 0.68)',
    'rgb(255, 120, 0)',
    'hsv(51, 100, 98)',
    'hsva(120, 40, 94, 0.5)',
    'hsl(181, 100%, 37%)',
    'hsla(209, 100%, 56%, 0.73)',
    '#c7158577',
])

const setColor = () => {
    const html2 = document.documentElement
    html2.style.setProperty('--el-color-primary', color.value)

}
</script>

<style scoped lang="scss">
.dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
}

/* --- 新增：强制提升弹窗层级 --- */
/* 1. 提升遮罩层层级 */
:deep(.el-overlay) {
    z-index: 20260301 !important;
    /* 比 dialog 小 1 */
}

/* 2. 提升弹窗本体层级 */
:deep(.el-dialog) {
    z-index: 20260302 !important;
    /* 防止被父级 overflow 裁剪的额外保险 */
    position: fixed !important;
}

/* 3. 如果还是不行，检查是否有父级 overflow: hidden 影响了 body 的显示 */
/* 通常不需要，但如果项目有全局 body overflow 限制，需检查 */
</style>
