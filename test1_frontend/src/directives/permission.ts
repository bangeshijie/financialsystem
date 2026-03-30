// directives/permission.ts
import { useUserStore } from '@/store/modules/user'
import type { Directive, DirectiveBinding } from 'vue'

/**
 * 权限指令
 * 用法：v-permission="['btn.add', 'btn.update']" 或 v-permission="'btn.add'"
 * 如果用户没有权限，元素会被移除
 */
export const permission: Directive = {
    mounted(el: HTMLElement, binding: DirectiveBinding) {
        const { value } = binding
        const userStore = useUserStore()
        const userButtons = userStore.buttons || []

        // 如果没有传入权限值，默认不显示
        if (!value) {
            el.parentNode?.removeChild(el)
            return
        }

        // 获取权限值（支持数组或字符串）
        const requiredPermissions = Array.isArray(value) ? value : [value]

        // 检查用户是否拥有任一权限
        const hasPermission = requiredPermissions.some(permission =>
            userButtons.includes(permission)
        )

        // 如果没有权限，移除元素
        if (!hasPermission) {
            el.parentNode?.removeChild(el)
        }
    }
}

/**
 * 权限指令（隐藏模式）
 * 用法：v-permission-hide="['btn.add', 'btn.update']"
 * 如果用户没有权限，元素会被隐藏（display: none）
 */
export const permissionHide: Directive = {
    mounted(el: HTMLElement, binding: DirectiveBinding) {
        const { value } = binding
        const userStore = useUserStore()
        const userButtons = userStore.buttons || []

        if (!value) {
            el.style.display = 'none'
            return
        }

        const requiredPermissions = Array.isArray(value) ? value : [value]
        const hasPermission = requiredPermissions.some(permission =>
            userButtons.includes(permission)
        )

        if (!hasPermission) {
            el.style.display = 'none'
        }
    }
}