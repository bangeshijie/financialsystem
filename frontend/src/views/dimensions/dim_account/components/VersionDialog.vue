<!-- src/views/account/components/VersionDialog.vue -->
<template>
    <el-dialog v-model="dialogVisible" :title="title" width="500px" @close="handleClose">
        <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
            <el-form-item label="版本编码" prop="version_code">
                <el-input v-model="formData.version_code" placeholder="请输入版本编码" :disabled="!!data" />
            </el-form-item>

            <el-form-item label="版本名称" prop="version_name">
                <el-input v-model="formData.version_name" placeholder="请输入版本名称" />
            </el-form-item>

            <el-form-item label="版本描述" prop="description">
                <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="请输入版本描述" />
            </el-form-item>

            <el-form-item label="生效日期" prop="effective_date">
                <el-date-picker v-model="formData.effective_date" type="date" placeholder="请选择生效日期" format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD" />
            </el-form-item>

            <el-form-item label="是否默认" prop="is_default">
                <el-switch v-model="formData.is_default" />
            </el-form-item>

            <el-form-item label="是否启用" prop="is_active">
                <el-switch v-model="formData.is_active" />
            </el-form-item>

            <el-form-item label="备注" prop="remark">
                <el-input v-model="formData.remark" type="textarea" :rows="2" placeholder="请输入备注" />
            </el-form-item>
        </el-form>

        <template #footer>
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" :loading="loading" @click="handleSubmit">
                确定
            </el-button>
        </template>
    </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ElForm, ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { AccountVersion, AccountVersionCreate, AccountVersionUpdate } from '@/api/dimensions/dim_account/type'
import { versionApi } from '@/api/dimensions/dim_account'

const props = defineProps<{
    visible: boolean
    data?: AccountVersion | null
}>()

const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void
    (e: 'success'): void
}>()

const formRef = ref<FormInstance>()
const loading = ref(false)

const dialogVisible = computed({
    get: () => props.visible,
    set: (val) => emit('update:visible', val)
})

const title = computed(() => props.data ? '编辑版本' : '新建版本')

const formData = reactive<AccountVersionCreate | AccountVersionUpdate>({
    version_code: '',
    version_name: '',
    description: '',
    is_default: false,
    is_active: true,
    effective_date: '',
    remark: ''
})

const rules: FormRules = {
    version_code: [
        { required: true, message: '请输入版本编码', trigger: 'blur' },
        { min: 1, max: 20, message: '长度在 1 到 20 个字符', trigger: 'blur' }
    ],
    version_name: [
        { required: true, message: '请输入版本名称', trigger: 'blur' },
        { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
    ]
}

// 重置表单
const resetForm = () => {
    formData.version_code = ''
    formData.version_name = ''
    formData.description = ''
    formData.is_default = false
    formData.is_active = true
    formData.effective_date = ''
    formData.remark = ''
}

// 加载数据
const loadData = () => {
    if (props.data) {
        Object.assign(formData, props.data)
    } else {
        resetForm()
    }
}

// 提交表单
const handleSubmit = async () => {
    if (!formRef.value) return

    await formRef.value.validate(async (valid) => {
        if (!valid) return

        loading.value = true
        try {
            if (props.data) {
                await versionApi.update(props.data.id, formData)
                ElMessage.success('更新成功')
            } else {
                await versionApi.create(formData as AccountVersionCreate)
                ElMessage.success('创建成功')
            }

            dialogVisible.value = false
            emit('success')
        } catch (error: any) {
            console.error('提交失败:', error)
            ElMessage.error(error.response?.data?.detail || '操作失败')
        } finally {
            loading.value = false
        }
    })
}

// 关闭弹窗
const handleClose = () => {
    resetForm()
    formRef.value?.clearValidate()
}

// 监听 visible 变化
watch(() => props.visible, (val) => {
    if (val) {
        loadData()
    }
})


</script>

<style lang="scss" scoped>
// 使用变量定义主题色和间距，方便后续维护
$primary-color: #409eff;
$border-color: #dcdfe6;
$spacing-md: 16px;

// 深度选择器用于穿透修改 el-dialog 的默认样式
:deep(.el-dialog) {
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);

    // 修改弹窗头部样式
    .el-dialog__header {
        border-bottom: 1px solid $border-color;
        padding: 16px 20px;
        margin-right: 0;

        .el-dialog__title {
            font-weight: 600;
            color: #303133;
        }
    }

    // 修改弹窗内容区域
    .el-dialog__body {
        padding: 24px 20px;
        max-height: 70vh; // 限制最大高度，超出可滚动
        overflow-y: auto;
    }

    // 修改弹窗底部样式
    .el-dialog__footer {
        border-top: 1px solid $border-color;
        padding: 12px 20px;
        text-align: right;
    }
}

// 表单样式优化
.el-form {

    // 表单项间距
    .el-form-item {
        margin-bottom: 20px;

        // 输入框聚焦时的过渡效果
        :deep(.el-input__inner),
        :deep(.el-textarea__inner) {
            transition: all 0.3s ease;

            &:focus {
                box-shadow: 0 0 0 2px rgba($primary-color, 0.2);
            }
        }

        // 文本域调整大小手柄
        :deep(.el-textarea) {
            resize: vertical;
        }
    }
}



// 响应式设计
@media (max-width: 768px) {
    :deep(.el-dialog) {
        width: 90% !important;
        margin-top: 10vh;

        .el-dialog__body {
            padding: 16px;
        }
    }
}

// 加载状态下的光标变化
.loading {
    cursor: not-allowed;
    opacity: 0.7;
}
</style>