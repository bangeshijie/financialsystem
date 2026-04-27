<!-- src/views/dimensions/AccountManagement.vue -->
<template>
    <div class="account-management">
        <el-card>
            <template #header>
                <div class="card-header">
                    <span>会计科目管理</span>
                    <div class="header-actions">
                        <el-button type="primary" @click="handleAddVersion">
                            <el-icon>
                                <Plus />
                            </el-icon>
                            新建版本
                        </el-button>
                    </div>
                </div>
            </template>

            <!-- 版本管理区域 -->
            <div class="version-section">
                <div class="section-header">
                    <span class="section-title">科目版本</span>
                    <div class="version-tools">
                        <el-form :inline="true" class="search-form">
                            <el-form-item>
                                <el-select v-model="versionSearch.is_active" clearable placeholder="状态"
                                    style="width: 100px;">
                                    <el-option label="启用" :value="true" />
                                    <el-option label="禁用" :value="false" />
                                </el-select>
                            </el-form-item>
                            <el-form-item>
                                <el-input v-model="versionSearch.search" placeholder="编码/名称" clearable
                                    @keyup.enter="loadVersions" />
                            </el-form-item>
                            <el-form-item>
                                <el-button type="primary" @click="loadVersions">查询</el-button>
                                <el-button @click="resetVersionSearch">重置</el-button>
                            </el-form-item>
                        </el-form>
                    </div>
                </div>

                <el-table :data="versions" v-loading="versionLoading" stripe size="small"
                    @row-click="handleVersionClick" highlight-current-row>
                    <el-table-column prop="version_code" label="版本编码" width="120" />
                    <el-table-column prop="version_name" label="版本名称" width="150" />
                    <el-table-column prop="description" label="描述" show-overflow-tooltip />
                    <el-table-column prop="effective_date" label="生效日期" width="100" />
                    <el-table-column label="默认" width="70" align="center">
                        <template #default="{ row }">
                            <el-tag :type="row.is_default ? 'success' : 'info'" size="small">
                                {{ row.is_default ? '是' : '否' }}
                            </el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column label="状态" width="70" align="center">
                        <template #default="{ row }">
                            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
                                {{ row.is_active ? '启用' : '禁用' }}
                            </el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column label="操作" width="200" fixed="right">
                        <template #default="{ row }">
                            <el-button link type="primary" size="small" @click.stop="handleEditVersion(row)">
                                编辑
                            </el-button>
                            <el-button v-if="!row.is_default" link type="success" size="small"
                                @click.stop="handleSetDefault(row)">
                                设为默认
                            </el-button>
                            <el-button link type="danger" size="small" @click.stop="handleDeleteVersion(row)">
                                删除
                            </el-button>
                        </template>
                    </el-table-column>
                </el-table>

                <el-pagination v-model:current-page="versionPage.page" v-model:page-size="versionPage.limit"
                    :total="versionPage.total" :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next"
                    @size-change="loadVersions" @current-change="loadVersions" class="version-pagination" />
            </div>

            <!-- 科目管理区域 - 仅在选中版本后显示 -->
            <div class="subject-section" v-if="selectedVersion">
                <div class="section-header">
                    <span class="section-title">
                        科目管理
                        <el-tag type="primary" size="small" class="version-tag">{{ selectedVersion.version_name
                            }}</el-tag>
                    </span>
                    <div class="subject-tools">
                        <el-button type="primary" size="small" @click="handleAddRoot">
                            <el-icon>
                                <Plus />
                            </el-icon>
                            新建根科目
                        </el-button>
                        <el-button type="success" size="small" @click="handleBatchImport">
                            <el-icon>
                                <Upload />
                            </el-icon>
                            批量导入
                        </el-button>
                        <el-button size="small" @click="handleExport">
                            <el-icon>
                                <Download />
                            </el-icon>
                            导出
                        </el-button>
                    </div>
                </div>

                <div class="subject-container">
                    <!-- 科目树 -->
                    <div class="subject-tree-panel">
                        <div class="panel-header">
                            <span>科目树</span>
                            <el-input v-model="searchKeyword" placeholder="搜索科目" clearable size="small"
                                style="width: 180px;" @input="handleSearchTree" />
                        </div>
                        <AccountTree ref="treeRef" :version-id="selectedVersion.id" @node-click="handleNodeClick"
                            @add="handleAddChild" @edit="handleEdit" @delete="handleDeleteSuccess"
                            @refresh="loadTree" />
                    </div>

                    <!-- 科目详情/编辑表单 -->
                    <div class="subject-form-panel">
                        <div class="panel-header">
                            <span>{{ selectedNode ? '编辑科目' : '科目详情' }}</span>
                            <el-button v-if="selectedNode" link type="primary" size="small" @click="handleRefreshForm">
                                刷新
                            </el-button>
                        </div>

                        <el-form v-if="selectedNode" ref="formRef" :model="formData" :rules="formRules"
                            label-width="100px" class="subject-form">
                            <el-form-item label="科目编码" prop="code">
                                <el-input v-model="formData.code" disabled />
                                <div class="form-tip">科目编码不可修改</div>
                            </el-form-item>

                            <el-form-item label="科目名称" prop="name">
                                <el-input v-model="formData.name" placeholder="请输入科目名称" />
                            </el-form-item>

                            <el-form-item label="显示名称" prop="display_name">
                                <el-input v-model="formData.display_name" placeholder="请输入显示名称" />
                                <div class="form-tip">显示名称用于界面展示，不填则使用科目名称</div>
                            </el-form-item>

                            <el-form-item label="余额方向" prop="balance_direction">
                                <el-radio-group v-model="formData.balance_direction">
                                    <el-radio value="debit">
                                        <span style="color: #f56c6c;">借方</span>
                                    </el-radio>
                                    <el-radio value="credit">
                                        <span style="color: #67c23a;">贷方</span>
                                    </el-radio>
                                </el-radio-group>
                            </el-form-item>

                            <el-form-item label="是否启用" prop="is_active">
                                <el-switch v-model="formData.is_active" active-text="启用" inactive-text="禁用" />
                            </el-form-item>

                            <el-form-item label="科目级次">
                                <el-input v-model="formData.level" disabled />
                            </el-form-item>

                            <el-form-item label="完整路径">
                                <el-input v-model="formData.full_name" disabled type="textarea" :rows="2" />
                            </el-form-item>

                            <el-form-item>
                                <el-button type="primary" :loading="saveLoading" @click="handleSave">
                                    保存修改
                                </el-button>
                                <el-button @click="handleCancelEdit">取消</el-button>
                            </el-form-item>
                        </el-form>

                        <el-empty v-else description="请从左侧选择科目" />
                    </div>
                </div>
            </div>

            <!-- 未选择版本时的提示 -->
            <el-empty v-else description="请从上方选择一个科目版本" style="margin-top: 40px;" />
        </el-card>

        <!-- 版本弹窗 -->
        <VersionDialog v-model:visible="versionDialogVisible" :data="currentVersion" @success="handleVersionSuccess" />

        <!-- 科目弹窗 -->
        <AccountDialog v-model:visible="accountDialogVisible" :data="currentSubject" :parent="parentSubject"
            :version-id="selectedVersion?.id" @success="handleAccountSuccess" />

        <!-- 批量导入弹窗 -->
        <el-dialog v-model="importVisible" title="批量导入科目" width="600px">
            <el-upload drag action="#" :auto-upload="false" :on-change="handleFileChange" :limit="1"
                :before-upload="() => false">
                <el-icon class="el-icon--upload">
                    <UploadFilled />
                </el-icon>
                <div class="el-upload__text">
                    将 Excel 文件拖到此处，或 <em>点击上传</em>
                </div>
                <template #tip>
                    <div class="el-upload__tip">
                        请上传 Excel 文件，包含 code, name, parent_code, balance_direction 等列
                        <br />
                        <el-button link type="primary" size="small" @click="downloadTemplate">下载导入模板</el-button>
                    </div>
                </template>
            </el-upload>
            <template #footer>
                <el-button @click="importVisible = false">取消</el-button>
                <el-button type="primary" :loading="importLoading" @click="handleImport">导入</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, Download, UploadFilled } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { AccountingSubject, AccountingSubjectUpdate, AccountVersion } from '@/api/dimensions/dim_account/type'
import { accountApi, versionApi } from '@/api/dimensions/dim_account'

import AccountTree from './components/AccountTree.vue'
import AccountDialog from './components/AccountDialog.vue'
import VersionDialog from './components/VersionDialog.vue'
import * as XLSX from 'xlsx'

// ==================== 版本管理相关 ====================
const versions = ref<AccountVersion[]>([])
const versionLoading = ref(false)
const versionDialogVisible = ref(false)
const currentVersion = ref<AccountVersion | null>(null)
const selectedVersion = ref<AccountVersion | null>(null)

const versionSearch = reactive({
    is_active: null as boolean | null,
    search: ''
})

const versionPage = reactive({
    page: 1,
    limit: 20,
    total: 0
})

// 加载版本列表
const loadVersions = async () => {
    versionLoading.value = true
    try {
        const res = await versionApi.getList({
            skip: (versionPage.page - 1) * versionPage.limit,
            limit: versionPage.limit,
            is_active: versionSearch.is_active ?? undefined,
            search: versionSearch.search || undefined
        })
        versions.value = res.data.items
        versionPage.total = res.data.total
    } catch (error) {
        console.error('加载版本失败:', error)
        ElMessage.error('加载版本列表失败')
    } finally {
        versionLoading.value = false
    }
}

// 重置版本搜索
const resetVersionSearch = () => {
    versionSearch.is_active = null
    versionSearch.search = ''
    versionPage.page = 1
    loadVersions()
}

// 新增版本
const handleAddVersion = () => {
    currentVersion.value = null
    versionDialogVisible.value = true
}

// 编辑版本
const handleEditVersion = (row: AccountVersion) => {
    currentVersion.value = row
    versionDialogVisible.value = true
}

// 设为默认
const handleSetDefault = async (row: AccountVersion) => {
    try {
        await ElMessageBox.confirm(`确定要将 "${row.version_name}" 设为默认版本吗？`, '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'info'
        })
        await versionApi.setDefault(row.id)
        ElMessage.success('设置成功')
        loadVersions()

        // 如果当前选中的版本被修改了默认状态，刷新选中状态的显示
        if (selectedVersion.value?.id === row.id) {
            selectedVersion.value = { ...row, is_default: true }
        }
    } catch (error) {
        if (error !== 'cancel') {
            console.error('设置失败:', error)
            ElMessage.error('设置失败')
        }
    }
}

// 删除版本
const handleDeleteVersion = async (row: AccountVersion) => {
    try {
        await ElMessageBox.confirm(
            `确定要删除版本 "${row.version_name}" 吗？如果版本下有科目将无法删除。`,
            '提示',
            {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            }
        )
        await versionApi.delete(row.id)
        ElMessage.success('删除成功')

        // 如果删除的是当前选中的版本，清空选中状态
        if (selectedVersion.value?.id === row.id) {
            selectedVersion.value = null
        }
        loadVersions()
    } catch (error) {
        if (error !== 'cancel') {
            console.error('删除失败:', error)
            ElMessage.error('删除失败')
        }
    }
}

// 点击版本行
const handleVersionClick = (row: AccountVersion) => {
    selectedVersion.value = row
    // 重置科目相关状态
    selectedNode.value = null
    searchKeyword.value = ''
    formRef.value?.resetFields()
}

// 版本操作成功回调
const handleVersionSuccess = () => {
    loadVersions()
}

// ==================== 科目管理相关 ====================
const treeRef = ref()
const formRef = ref<FormInstance>()
const selectedNode = ref<AccountingSubject | null>(null)
const saveLoading = ref(false)
const accountDialogVisible = ref(false)
const currentSubject = ref<AccountingSubject | null>(null)
const parentSubject = ref<AccountingSubject | null>(null)
const searchKeyword = ref('')
const importVisible = ref(false)
const importLoading = ref(false)
const importFile = ref<File | null>(null)

const formData = reactive<AccountingSubjectUpdate>({
    code: '',
    name: '',
    display_name: '',
    balance_direction: 'debit',
    is_active: true,
    level: 1,
    full_name: ''
})

const formRules: FormRules = {
    code: [
        { required: true, message: '请输入科目编码', trigger: 'blur' },
        { min: 1, max: 20, message: '长度在 1 到 20 个字符', trigger: 'blur' }
    ],
    name: [
        { required: true, message: '请输入科目名称', trigger: 'blur' },
        { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
    ]
}

// 加载树
const loadTree = () => {
    if (selectedVersion.value) {
        treeRef.value?.refresh()
    }
}

// 节点点击
const handleNodeClick = (node: AccountingSubject) => {
    selectedNode.value = node
    Object.assign(formData, {
        code: node.code,
        name: node.name,
        display_name: node.display_name || '',
        balance_direction: node.balance_direction,
        is_active: node.is_active,
        level: node.level,
        full_name: node.full_name || ''
    })
}

// 新增根科目
const handleAddRoot = () => {
    if (!selectedVersion.value) {
        ElMessage.warning('请先选择科目版本')
        return
    }
    parentSubject.value = null
    currentSubject.value = null
    accountDialogVisible.value = true
}

// 新增子科目
const handleAddChild = (parent: AccountingSubject | null) => {
    if (!selectedVersion.value) {
        ElMessage.warning('请先选择科目版本')
        return
    }
    if (!parent) {
        ElMessage.warning('父科目信息有误')
        return
    }
    parentSubject.value = parent
    currentSubject.value = null
    accountDialogVisible.value = true
}

// 编辑科目
const handleEdit = (node: AccountingSubject) => {
    if (!selectedVersion.value) {
        ElMessage.warning('请先选择科目版本')
        return
    }
    currentSubject.value = node
    parentSubject.value = null
    accountDialogVisible.value = true
}

// 刷新表单
const handleRefreshForm = () => {
    if (selectedNode.value) {
        handleNodeClick(selectedNode.value)
        ElMessage.success('已刷新')
    }
}

// 保存修改
const handleSave = async () => {
    if (!formRef.value || !selectedNode.value) return

    await formRef.value.validate(async (valid) => {
        if (!valid) return

        saveLoading.value = true
        try {
            const updateData = {
                name: formData.name,
                display_name: formData.display_name || undefined,
                balance_direction: formData.balance_direction,
                is_active: formData.is_active
            }
            await accountApi.update(selectedNode.value!.id, updateData)
            ElMessage.success('保存成功')
            loadTree()

            // 更新选中的节点数据
            Object.assign(selectedNode.value!, {
                name: formData.name,
                display_name: formData.display_name,
                balance_direction: formData.balance_direction,
                is_active: formData.is_active
            })

            selectedNode.value = null
            formRef.value?.resetFields()
        } catch (error: any) {
            console.error('保存失败:', error)
            ElMessage.error(error.response?.data?.detail || '保存失败')
        } finally {
            saveLoading.value = false
        }
    })
}

// 取消编辑
const handleCancelEdit = () => {
    selectedNode.value = null
    formRef.value?.resetFields()
    ElMessage.info('已取消编辑')
}

// 删除成功回调
const handleDeleteSuccess = () => {
    if (selectedNode.value) {
        selectedNode.value = null
        formRef.value?.resetFields()
    }
    loadTree()
}

// 科目弹窗操作成功
const handleAccountSuccess = () => {
    loadTree()
}

// 导出
const handleExport = async () => {
    if (!selectedVersion.value) {
        ElMessage.warning('请先选择科目版本')
        return
    }

    try {
        const treeRes = await accountApi.getTree(selectedVersion.value.id)

        if (!treeRes.data || !Array.isArray(treeRes.data) || treeRes.data.length === 0) {
            ElMessage.warning('没有可导出的数据')
            return
        }

        const flattenTree = (nodes: any[]): any[] => {
            const result: any[] = []
            for (const node of nodes) {
                result.push({
                    code: node.code,
                    name: node.name,
                    display_name: node.display_name || '',
                    level: node.level,
                    balance_direction: node.balance_direction,
                    is_active: node.is_active,
                    full_name: node.full_name || '',
                    parent_id: node.parent_id || '',
                    is_leaf: node.is_leaf,
                    id: node.id
                })
                if (node.children && node.children.length > 0) {
                    result.push(...flattenTree(node.children))
                }
            }
            return result
        }

        const allSubjects = flattenTree(treeRes.data)

        const excelData = allSubjects.map((item: any) => ({
            '科目编码': item.code,
            '科目名称': item.name,
            '显示名称': item.display_name || '',
            '科目级次': item.level,
            '余额方向': item.balance_direction === 'debit' ? '借方' : '贷方',
            '状态': item.is_active ? '启用' : '禁用',
            '完整路径': item.full_name || '',
            '父科目ID': item.parent_id || '',
            '是否叶子节点': item.is_leaf ? '是' : '否'
        }))

        const ws = XLSX.utils.json_to_sheet(excelData)
        ws['!cols'] = [
            { wch: 15 }, { wch: 20 }, { wch: 20 }, { wch: 10 },
            { wch: 10 }, { wch: 8 }, { wch: 40 }, { wch: 12 }, { wch: 12 }
        ]

        const wb = XLSX.utils.book_new()
        XLSX.utils.book_append_sheet(wb, ws, `科目表_${selectedVersion.value.version_name}`)

        const versionInfo = [
            { '项目': '版本ID', '值': selectedVersion.value.id },
            { '项目': '版本名称', '值': selectedVersion.value.version_name },
            { '项目': '版本编码', '值': selectedVersion.value.version_code || '' },
            { '项目': '导出时间', '值': new Date().toLocaleString() },
            { '项目': '科目总数', '值': excelData.length }
        ]
        const wsInfo = XLSX.utils.json_to_sheet(versionInfo)
        XLSX.utils.book_append_sheet(wb, wsInfo, '版本信息')

        XLSX.writeFile(wb, `科目表_${selectedVersion.value.version_name}_${Date.now()}.xlsx`)
        ElMessage.success(`导出成功，共 ${excelData.length} 条科目`)
    } catch (error: any) {
        console.error('导出失败:', error)
        ElMessage.error(error.response?.data?.message || error.message || '导出失败')
    }
}

// 批量导入
const handleBatchImport = () => {
    if (!selectedVersion.value) {
        ElMessage.warning('请先选择科目版本')
        return
    }
    importVisible.value = true
}

// 文件选择
const handleFileChange = (file: any) => {
    importFile.value = file.raw
}

// 下载模板
const downloadTemplate = () => {
    const templateData = [
        { code: '1001', name: '库存现金', display_name: '', parent_code: '', balance_direction: 'debit', is_active: true },
        { code: '1002', name: '银行存款', display_name: '', parent_code: '', balance_direction: 'debit', is_active: true },
        { code: '1122', name: '应收账款', display_name: '', parent_code: '', balance_direction: 'debit', is_active: true },
        { code: '100201', name: '工商银行', display_name: '', parent_code: '1002', balance_direction: 'debit', is_active: true }
    ]

    const ws = XLSX.utils.json_to_sheet(templateData)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '科目模板')
    XLSX.writeFile(wb, `subject_template_${Date.now()}.xlsx`)
}

// 导入
const handleImport = async () => {
    if (!importFile.value) {
        ElMessage.warning('请选择文件')
        return
    }
    if (!selectedVersion.value) {
        ElMessage.warning('请先选择科目版本')
        return
    }

    importLoading.value = true
    try {
        const data = await importFile.value.arrayBuffer()
        const workbook = XLSX.read(data)

        if (!workbook.SheetNames || workbook.SheetNames.length === 0) {
            throw new Error('Excel文件中没有工作表')
        }
        const firstSheetName = workbook.SheetNames[0]
        if (!firstSheetName) {
            throw new Error('无法获取第一个工作表的名称')
        }

        // 修复：使用非空断言操作符 (!) 告诉 TS 此处 firstSheetName 必定存在
        // 或者使用 as string 进行类型断言
        const worksheet = workbook.Sheets[firstSheetName!]
        if (!worksheet) {
            throw new Error('无法读取工作表内容')
        }

        let jsonData = XLSX.utils.sheet_to_json<any>(worksheet)

        if (jsonData.length === 0) {
            throw new Error('Excel文件中没有数据')
        }

        jsonData = jsonData.map((row: any) => {
            let code = row.code || row['编码'] || row['科目编码'] || row['科目代码'] || row['CODE']
            let name = row.name || row['名称'] || row['科目名称'] || row['NAME']
            let parent_code = row.parent_code || row['父编码'] || row['父科目编码'] || row['上级编码'] || row['PARENT_CODE']
            let display_name = row.display_name || row['显示名称'] || row['展示名称']
            let balance_direction = row.balance_direction || row['余额方向'] || row['方向']
            let is_active = row.is_active !== undefined ? row.is_active : row['是否启用']

            code = code ? String(code).trim() : ''
            name = name ? String(name).trim() : ''
            parent_code = parent_code ? String(parent_code).trim() : ''

            return {
                code,
                name,
                parent_code,
                display_name: display_name ? String(display_name).trim() : '',
                balance_direction: balance_direction ? String(balance_direction).trim() : '',
                is_active: is_active === '是' || is_active === '启用' || is_active === true || is_active === 'true'
            }
        })

        jsonData = jsonData.filter(row => row.code && row.name)

        if (jsonData.length === 0) {
            throw new Error('Excel文件中没有有效的科目数据。请确保包含"编码"和"名称"列')
        }

        const treeRes = await accountApi.getTree(selectedVersion.value.id)

        const flattenTree = (nodes: any[]): any[] => {
            let result: any[] = []
            if (!Array.isArray(nodes)) return result
            for (const node of nodes) {
                if (node) {
                    const { children, ...nodeWithoutChildren } = node
                    result.push(nodeWithoutChildren)
                    if (children && Array.isArray(children) && children.length > 0) {
                        result = result.concat(flattenTree(children))
                    }
                }
            }
            return result
        }

        const allSubjects = flattenTree(Array.isArray(treeRes.data) ? treeRes.data : [])
        const codeToIdMap = new Map()
        allSubjects.forEach((item: any) => {
            if (item.code && item.id) {
                codeToIdMap.set(item.code, item.id)
            }
        })

        const subjects: any[] = []
        const errors: string[] = []

        for (let i = 0; i < jsonData.length; i++) {
            const row = jsonData[i]

            if (!row.code || !row.name) {
                errors.push(`第 ${i + 1} 行: 缺少编码或名称`)
                continue
            }

            let parentId = null
            if (row.parent_code) {
                parentId = codeToIdMap.get(row.parent_code)
                if (!parentId) {
                    errors.push(`第 ${i + 1} 行: 父科目编码不存在: ${row.parent_code} (子科目: ${row.code})`)
                    continue
                }
            }

            let balanceDirection = 'debit'
            if (row.balance_direction) {
                const direction = row.balance_direction.toLowerCase()
                if (direction === 'credit' || direction === '贷方' || direction === '贷') {
                    balanceDirection = 'credit'
                }
            }

            subjects.push({
                code: row.code,
                name: row.name,
                display_name: row.display_name || row.name,
                parent_id: parentId,
                balance_direction: balanceDirection,
                is_active: row.is_active !== false,
                account_version_id: selectedVersion.value.id
            })
        }

        if (errors.length > 0) {
            ElMessage.warning(`以下数据有问题:\n${errors.slice(0, 5).join('\n')}`)
        }

        if (subjects.length === 0) {
            throw new Error('没有有效的科目数据')
        }

        await accountApi.batchCreate(subjects)
        ElMessage.success(`导入成功 ${subjects.length} 条${errors.length > 0 ? `，失败 ${errors.length} 条` : ''}`)
        importVisible.value = false
        loadTree()
    } catch (error: any) {
        console.error('导入失败:', error)
        ElMessage.error(error.message || '导入失败')
    } finally {
        importLoading.value = false
        importFile.value = null
    }
}

// 搜索树
const handleSearchTree = () => {
    if (treeRef.value && treeRef.value.filter) {
        treeRef.value.filter(searchKeyword.value)
    }
}

// 初始化
onMounted(() => {
    loadVersions()
})
</script>

<style lang="scss" scoped>
.account-management {
    padding: 20px;
    min-height: calc(100vh - 100px);

    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .version-section {
        margin-bottom: 24px;
        border-bottom: 1px solid #ebeef5;
        padding-bottom: 16px;
    }

    .subject-section {
        margin-top: 16px;
    }

    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;

        .section-title {
            font-size: 16px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;

            .version-tag {
                margin-left: 8px;
            }
        }
    }

    .version-pagination {
        margin-top: 16px;
        display: flex;
        justify-content: flex-end;
    }

    .search-form {
        margin-bottom: 0;

        :deep(.el-form-item) {
            margin-bottom: 0;
            margin-right: 12px;
        }
    }

    .subject-container {
        display: flex;
        gap: 20px;
        min-height: 500px;

        .subject-tree-panel,
        .subject-form-panel {
            flex: 1;
            border: 1px solid #ebeef5;
            border-radius: 4px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .subject-tree-panel {
            .panel-header {
                flex-shrink: 0;
                padding: 12px 16px;
                border-bottom: 1px solid #ebeef5;
                background-color: #f5f7fa;
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 12px;

                >span {
                    font-weight: 500;
                    white-space: nowrap;
                }
            }

            :deep(.subject-tree) {
                flex: 1;
                overflow: auto;
                padding: 12px;
                max-height: 600px;
            }
        }

        .subject-form-panel {
            .panel-header {
                padding: 12px 16px;
                border-bottom: 1px solid #ebeef5;
                background-color: #f5f7fa;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-weight: 500;
                flex-shrink: 0;
            }
        }

        .subject-form {
            padding: 20px;
            overflow: auto;
            max-height: 600px;
        }
    }

    .form-tip {
        font-size: 12px;
        color: #909399;
        line-height: 1.5;
        margin-top: 4px;
    }
}

:deep(.el-table__row) {
    cursor: pointer;
}
</style>