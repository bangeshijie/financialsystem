<template>
    <div class="subject-tree">
        <el-tree ref="treeRef" :data="treeData" :props="treeProps" node-key="id"
            :default-expanded-keys="defaultExpandedKeys" :expand-on-click-node="false" highlight-current
            :filter-node-method="filterNode" @node-click="handleNodeClick">
            <template #default="{ data }">
                <div class="tree-node">
                    <div class="node-info">
                        <el-icon v-if="data.is_leaf">
                            <Document />
                        </el-icon>
                        <el-icon v-else>
                            <Folder />
                        </el-icon>
                        <span class="node-code">{{ data.code }}</span>
                        <span class="node-name">{{ data.name }}</span>
                        <el-tag v-if="!data.is_active" type="danger" size="small">禁用</el-tag>
                        <el-tag v-if="data.is_leaf" type="info" size="small" class="leaf-tag">末级</el-tag>
                    </div>
                    <div class="node-actions">
                        <el-button link type="primary" size="small" @click.stop="handleAdd(data)">
                            <el-icon>
                                <Plus />
                            </el-icon>
                            添加子级
                        </el-button>
                        <el-button link type="warning" size="small" @click.stop="handleEdit(data)">
                            <el-icon>
                                <Edit />
                            </el-icon>
                            编辑
                        </el-button>
                        <el-button link type="danger" size="small" @click.stop="handleDelete(data)">
                            <el-icon>
                                <Delete />
                            </el-icon>
                            删除
                        </el-button>
                    </div>
                </div>
            </template>
        </el-tree>
    </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElTree, ElMessageBox, ElMessage } from 'element-plus'
import { Document, Folder, Plus, Edit, Delete } from '@element-plus/icons-vue'
import type { AccountingSubject } from '@/api/dimensions/dim_account/type'
import { accountApi } from '@/api/dimensions/dim_account/index'

const props = defineProps<{
    versionId: number
}>()

const emit = defineEmits<{
    (e: 'node-click', node: AccountingSubject): void
    (e: 'add', parent: AccountingSubject | null): void
    (e: 'edit', node: AccountingSubject): void
    (e: 'delete', node: AccountingSubject): void
    (e: 'refresh'): void
}>()

const treeRef = ref<InstanceType<typeof ElTree>>()
const treeData = ref<AccountingSubject[]>([])
const defaultExpandedKeys = ref<number[]>([])

const treeProps = {
    children: 'children',
    label: 'name'
}

// 加载树数据
const loadTree = async () => {
    if (!props.versionId) return

    try {
        const res = await accountApi.getTree(props.versionId)
        treeData.value = res.data

        // 默认展开第一层
        if (treeData.value.length > 0) {
            defaultExpandedKeys.value = treeData.value.map(item => item.id)
        }
    } catch (error) {
        console.error('加载科目树失败:', error)
        ElMessage.error('加载科目树失败')
    }
}

// 节点点击
const handleNodeClick = (data: AccountingSubject) => {
    emit('node-click', data)
}

// 添加子级
const handleAdd = (data: AccountingSubject) => {
    emit('add', data)
}

// 编辑
const handleEdit = (data: AccountingSubject) => {
    emit('edit', data)
}

// 删除
const handleDelete = async (data: AccountingSubject) => {
    try {
        await ElMessageBox.confirm(
            `确定要删除科目 "${data.name}" 吗？${data.is_leaf ? '' : '（非末级科目无法删除）'}`,
            '提示',
            {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            }
        )

        if (!data.is_leaf) {
            ElMessage.warning('请先删除所有子科目')
            return
        }

        await accountApi.delete(data.id)
        ElMessage.success('删除成功')
        emit('delete', data)
        await loadTree()
    } catch (error) {
        if (error !== 'cancel') {
            console.error('删除失败:', error)
            ElMessage.error('删除失败')
        }
    }
}

// 刷新树
const refresh = () => {
    loadTree()
}



// 添加 filter 方法
const filterNode = (value: string, data: any) => {
    if (!value) return true
    return data.name.includes(value) || data.code.includes(value)
}




// 监听版本变化
watch(() => props.versionId, () => {
    loadTree()
}, { immediate: true })

// 暴露方法
defineExpose({
    refresh,
    filter: (value: string) => {
        treeRef.value?.filter(value)
    }
})

</script>

<style scoped>
.subject-tree {
    height: 100%;
    overflow: auto;
}

.tree-node {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    padding-right: 16px;
}

.node-info {
    display: flex;
    align-items: center;
    gap: 8px;
}

.node-code {
    color: #606266;
    font-family: monospace;
    font-size: 12px;
    background-color: #f5f7fa;
    padding: 2px 6px;
    border-radius: 4px;
}

.node-name {
    font-size: 14px;
    font-weight: 500;
}

.leaf-tag {
    margin-left: 8px;
}

.node-actions {
    display: none;
    gap: 4px;
}

.tree-node:hover .node-actions {
    display: flex;
}
</style>
