<template>
    <el-dialog v-model="dialogVisible" :title="title" width="600px" @close="handleClose">
        <el-form ref="formRef" :model="formData" :rules="rules" label-width="120px">
            <el-form-item label="科目编码" prop="code">
                <el-input v-model="formData.code" placeholder="请输入科目编码，如：1001、1002" :disabled="!!data" />
                <div class="form-tip">同一版本内科目编码必须唯一</div>
            </el-form-item>

            <el-form-item label="科目名称" prop="name">
                <el-input v-model="formData.name" placeholder="请输入科目名称，如：库存现金、银行存款" />
            </el-form-item>

            <el-form-item label="显示名称" prop="display_name">
                <el-input v-model="formData.display_name" placeholder="请输入显示名称（可选）" />
                <div class="form-tip">显示名称用于界面展示，不填则使用科目名称</div>
            </el-form-item>

            <el-form-item label="父科目" prop="parent_id">
                <el-tree-select v-model="formData.parent_id" :data="parentTreeData" :props="treeSelectProps"
                    placeholder="请选择父科目（不选则为根科目）" clearable check-strictly filterable :default-expand-all="false"
                    :expand-on-click-node="false">
                    <template #default="{ data }">
                        <span class="tree-select-node">
                            <el-icon v-if="data.is_leaf">
                                <Document />
                            </el-icon>
                            <el-icon v-else>
                                <Folder />
                            </el-icon>
                            <span class="node-code">{{ data.code }}</span>
                            <span class="node-name">{{ data.name }}</span>
                        </span>
                    </template>
                </el-tree-select>
                <div class="form-tip">选择父科目后，科目级次和完整路径会自动计算</div>
            </el-form-item>

            <el-form-item label="余额方向" prop="balance_direction">
                <el-radio-group v-model="formData.balance_direction">
                    <el-radio value="debit">
                        <span style="color: #f56c6c;">借方</span>
                        <span class="direction-tip">（资产、成本、费用类）</span>
                    </el-radio>
                    <el-radio value="credit">
                        <span style="color: #67c23a;">贷方</span>
                        <span class="direction-tip">（负债、所有者权益、收入类）</span>
                    </el-radio>
                </el-radio-group>
            </el-form-item>

            <el-form-item label="是否启用" prop="is_active">
                <el-switch v-model="formData.is_active" active-text="启用" inactive-text="禁用" />
                <div class="form-tip">禁用的科目在凭证录入时不可选择</div>
            </el-form-item>

            <el-form-item label="科目版本" prop="account_version_id" v-if="!data">
                <el-select v-model="formData.account_version_id" placeholder="请选择科目版本" :disabled="!!data"
                    @change="handleVersionChange">
                    <el-option v-for="version in versions" :key="version.id" :label="version.version_name"
                        :value="version.id">
                        <span>{{ version.version_name }}</span>
                        <span v-if="version.is_default" class="default-tag">（默认）</span>
                    </el-option>
                </el-select>
                <div class="form-tip">版本一旦创建不可修改</div>
            </el-form-item>

            <!-- 只读信息展示 -->
            <el-divider v-if="data || formData.parent_id" content-position="left">自动计算信息</el-divider>

            <el-form-item v-if="formData.level" label="科目级次">
                <el-tag type="info">{{ formData.level }} 级科目</el-tag>
            </el-form-item>

            <el-form-item v-if="formData.full_name" label="完整路径">
                <el-input :value="formData.full_name" disabled type="textarea" :rows="2" class="full-name-input" />
            </el-form-item>
        </el-form>

        <template #footer>
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" :loading="loading" @click="handleSubmit">
                {{ data ? '保存修改' : '创建科目' }}
            </el-button>
        </template>
    </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElForm, ElMessage } from 'element-plus'
import { Document, Folder } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import type {
    AccountingSubject,
    AccountingSubjectCreate,
    AccountingSubjectUpdate,
} from '@/api/dimensions/dim_account/type'
import type { AccountVersion } from '@/api/dimensions/dim_account/type'
import { accountApi, versionApi } from '@/api/dimensions/dim_account/index'




const props = defineProps<{
    visible: boolean
    data?: AccountingSubject | null
    parent?: AccountingSubject | null
    versionId?: number
}>()

const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void
    (e: 'success'): void
}>()

const formRef = ref<FormInstance>()
const loading = ref(false)
const versions = ref<AccountVersion[]>([])
const parentTreeData = ref<AccountingSubject[]>([])
const allSubjects = ref<AccountingSubject[]>([])

const dialogVisible = computed({
    get: () => props.visible,
    set: (val) => emit('update:visible', val)
})

const title = computed(() => {
    if (props.data) return `编辑科目 - ${props.data.name}`
    if (props.parent) return `添加子科目 - ${props.parent.name}`
    return '新建根科目'
})

const treeSelectProps = {
    children: 'children',
    label: 'name',
    value: 'id',
    disabled: (data: AccountingSubject) => {
        // 编辑时不能选择自己及自己的子级作为父级
        if (props.data) {
            return data.id === props.data.id || isDescendant(data.id, props.data.id)
        }
        return false
    }
}

const formData = reactive<AccountingSubjectCreate | AccountingSubjectUpdate>({
    code: '',
    name: '',
    display_name: '',
    parent_id: null,
    balance_direction: 'debit',
    is_active: true,
    account_version_id: 0,
    level: 1,
    full_name: ''
})

const rules: FormRules = {
    code: [
        { required: true, message: '请输入科目编码', trigger: 'blur' },
        { min: 1, max: 20, message: '长度在 1 到 20 个字符', trigger: 'blur' },
        {
            pattern: /^[A-Za-z0-9_\-]+$/,
            message: '科目编码只能包含字母、数字、下划线和中划线',
            trigger: 'blur'
        }
    ],
    name: [
        { required: true, message: '请输入科目名称', trigger: 'blur' },
        { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
    ],
    account_version_id: [
        {
            required: true, message: '请选择科目版本', trigger: 'change', validator: (_rule, value, callback) => {
                if (!value || value === 0) {
                    callback(new Error('请选择科目版本'))
                } else {
                    callback()
                }
            }
        }
    ]
}

// 检查是否为后代节点
const isDescendant = (_parentId: number, childId: number): boolean => {
    const findChild = (nodes: AccountingSubject[]): boolean => {
        for (const node of nodes) {
            if (node.id === childId) return true
            if (node.children && findChild(node.children)) return true
        }
        return false
    }
    return findChild(parentTreeData.value)
}

// 加载版本列表
const loadVersions = async () => {
    try {
        const res = await versionApi.getList({ is_active: true })
        versions.value = res.data.items

        // 如果有默认版本，自动选中
        if (!formData.account_version_id && !props.data) {
            const defaultVersion = versions.value.find(v => v.is_default)
            if (defaultVersion) {
                formData.account_version_id = defaultVersion.id
                await loadParentTree()
            }
        }
    } catch (error) {
        console.error('加载版本失败:', error)
        ElMessage.error('加载版本列表失败')
    }
}

// 加载所有科目（用于父级选择）
const loadAllSubjects = async (versionId: number) => {
    if (!versionId) return

    try {
        const res = await accountApi.getTree(versionId)
        parentTreeData.value = res.data
        allSubjects.value = flattenTree(res.data)
    } catch (error) {
        console.error('加载科目树失败:', error)
    }
}

// 扁平化树结构
const flattenTree = (nodes: AccountingSubject[]): AccountingSubject[] => {
    let result: AccountingSubject[] = []
    for (const node of nodes) {
        result.push(node)
        if (node.children && node.children.length) {
            result = result.concat(flattenTree(node.children))
        }
    }
    return result
}

// 加载父科目树
const loadParentTree = async () => {
    if (!formData.account_version_id && formData.account_version_id !== 0) return

    await loadAllSubjects(formData.account_version_id as number)
}

// 计算科目级次和完整路径
const calculateLevelAndFullName = async () => {
    if (formData.parent_id) {
        const parent = allSubjects.value.find(s => s.id === formData.parent_id)
        if (parent) {
            formData.level = parent.level + 1
            const parentFullName = parent.full_name || parent.name
            formData.full_name = `${parentFullName}/${formData.name}`
        }
    } else {
        formData.level = 1
        formData.full_name = formData.name
    }
}

// 监听科目名称变化
watch(() => formData.name, (newName) => {
    if (newName && formData.parent_id !== undefined) {
        calculateLevelAndFullName()
    }
})

// 监听父科目变化
watch(() => formData.parent_id, async () => {
    await calculateLevelAndFullName()
})

// 监听版本变化
const handleVersionChange = async () => {
    await loadParentTree()
    formData.parent_id = null
}

// 重置表单
const resetForm = () => {
    formData.code = ''
    formData.name = ''
    formData.display_name = ''
    formData.parent_id = null
    formData.balance_direction = 'debit'
    formData.is_active = true
    formData.account_version_id = props.versionId || 0
    formData.level = 1
    formData.full_name = ''
}

// 加载数据到表单
const loadData = () => {
    if (props.data) {
        // 编辑模式：填充现有数据
        Object.assign(formData, {
            code: props.data.code,
            name: props.data.name,
            display_name: props.data.display_name || '',
            parent_id: props.data.parent_id,
            balance_direction: props.data.balance_direction,
            is_active: props.data.is_active,
            account_version_id: props.data.account_version_id,
            level: props.data.level,
            full_name: props.data.full_name || ''
        })
        // 加载对应版本的父级树
        loadAllSubjects(props.data.account_version_id)
    } else {
        // 新建模式
        resetForm()
        if (props.parent) {
            formData.parent_id = props.parent.id
            // 计算级次和路径
            setTimeout(() => {
                calculateLevelAndFullName()
            }, 100)
        }
        if (props.versionId && !formData.account_version_id) {
            formData.account_version_id = props.versionId
            loadAllSubjects(props.versionId)
        }
    }
}

// 验证编码唯一性
const validateCodeUnique = async (): Promise<boolean> => {
    if (!formData.code || !formData.account_version_id) return true

    try {
        const res = await accountApi.getList({
            account_version_id: formData.account_version_id,
            search: formData.code,
            limit: 1
        })

        const existing = res.data.items.find(item =>
            item.code === formData.code &&
            (!props.data || item.id !== props.data.id)
        )

        if (existing) {
            ElMessage.error(`编码 ${formData.code} 在当前版本中已存在`)
            return false
        }
        return true
    } catch (error) {
        console.error('验证编码失败:', error)
        return true
    }
}

// 提交表单
const handleSubmit = async () => {
    if (!formRef.value) return

    await formRef.value.validate(async (valid) => {
        if (!valid) return

        // 验证编码唯一性
        if (!props.data && !(await validateCodeUnique())) {
            return
        }

        loading.value = true
        try {
            // 清理提交数据
            const submitData = {
                code: formData.code,
                name: formData.name,
                display_name: formData.display_name || undefined,
                parent_id: formData.parent_id || null,
                balance_direction: formData.balance_direction,
                is_active: formData.is_active,
                account_version_id: formData.account_version_id
            }

            if (props.data) {
                // 编辑模式
                await accountApi.update(props.data.id, submitData)
                ElMessage.success('科目更新成功')
            } else {
                // 新建模式
                await accountApi.create(submitData as AccountingSubjectCreate)
                ElMessage.success('科目创建成功')
            }

            dialogVisible.value = false
            emit('success')
        } catch (error: any) {
            console.error('提交失败:', error)
            const detail = error.response?.data?.detail
            if (typeof detail === 'string') {
                ElMessage.error(detail)
            } else if (detail?.message) {
                ElMessage.error(detail.message)
            } else {
                ElMessage.error(props.data ? '更新失败' : '创建失败')
            }
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
        if (!versions.value.length) {
            loadVersions()
        }
        loadData()
    }
})

// 初始化
onMounted(() => {
    loadVersions()
})
</script>

<style scoped>
.form-tip {
    font-size: 12px;
    color: #909399;
    line-height: 1.5;
    margin-top: 4px;
}

.direction-tip {
    font-size: 12px;
    color: #909399;
    margin-left: 8px;
}

.default-tag {
    font-size: 12px;
    color: #e6a23c;
    margin-left: 8px;
}

.tree-select-node {
    display: flex;
    align-items: center;
    gap: 8px;
}

.tree-select-node .node-code {
    font-size: 12px;
    color: #606266;
    background-color: #f5f7fa;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: monospace;
}

.tree-select-node .node-name {
    font-size: 14px;
}

.full-name-input :deep(.el-textarea__inner) {
    background-color: #f5f7fa;
    font-family: monospace;
    font-size: 12px;
}
</style>