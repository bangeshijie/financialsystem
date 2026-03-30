<template>
    <div>
        <el-card style="max-width: 1440px">
            <!-- 卡片顶部添加的公司按钮 -->
            <el-button v-permission="'btn.Company.add'" type="primary" size="default" icon="plus"
                @click="addCompany">添加公司</el-button>

            <!-- 表格组件 展示数据-->
            <el-table style="margin: 10px 0px;" border :data="companyList">
                <el-table-column label="序号" width="80" align="center" type="index"></el-table-column>
                <el-table-column label="公司代码" width="120" prop="company_code" align="center"></el-table-column>

                <el-table-column label="公司名称" width="200" align="center">
                    <template #="{ row }">
                        <pre style="color:hotpink ; font-weight: bold">{{ row.name }}</pre>
                    </template>
                </el-table-column>

                <el-table-column label="公司简介" width="180" prop="description" align="center"
                    show-overflow-tooltip></el-table-column>
                <el-table-column label="公司地址" width="180" prop="address" align="center"
                    show-overflow-tooltip></el-table-column>
                <el-table-column label="公司规模" width="180" prop="scale" align="center"></el-table-column>
                <el-table-column label="添加人" width="180" prop="creator_name" align="center"></el-table-column>

                <el-table-column label="操作" width="180" align="center" fixed="right">
                    <template #="{ row }">
                        <el-button v-permission="'btn.Company.upd'" type="primary" size="small" icon="edit"
                            @click="updateCompany(row)" circle></el-button>
                        <el-popconfirm :title="`您确定要删除 ${row.name} 吗?`" width="240px" icon="Delete" icon-color="red"
                            @confirm="deleteCompany(row)">
                            <template #reference>
                                <el-button v-permission="'btn.Company.del'" type="danger" size="small" icon="Delete"
                                    circle></el-button>
                            </template>
                        </el-popconfirm>
                    </template>
                </el-table-column>
            </el-table>

            <!-- 分页器组件 -->
            <el-pagination @change="getCompanyList" v-model:current-page="pageNo" v-model:page-size="limit"
                :page-sizes="[3, 5, 10, 20]" size="small" :background="true"
                layout="prev, pager, next, jumper, ->, sizes, total" :total="total">
            </el-pagination>
        </el-card>

        <!-- 对话框组件 -->
        <!-- 动态标题 -->
        <el-dialog v-model="dialogFormVisible" :title="companyParams.id ? '编辑公司' : '添加公司'" width="500px">
            <el-form ref="formRef" :model="companyParams" :rules="formRules" label-width="100px">
                <el-form-item label="公司名称" prop="name">
                    <el-input v-model="companyParams.name" placeholder="请输入公司名称"></el-input>
                </el-form-item>
                <el-form-item label="公司代码" prop="company_code">
                    <el-input v-model="companyParams.company_code" placeholder="请输入公司代码"></el-input>
                </el-form-item>
                <el-form-item label="公司地址" prop="address">
                    <el-input v-model="companyParams.address" placeholder="请输入公司地址"></el-input>
                </el-form-item>
                <el-form-item label="联系人" prop="contact_person">
                    <el-input v-model="companyParams.contact_person" placeholder="请输入联系人"></el-input>
                </el-form-item>
                <el-form-item label="联系电话" prop="contact_phone">
                    <el-input v-model="companyParams.contact_phone" placeholder="请输入联系电话"></el-input>
                </el-form-item>
                <el-form-item label="联系邮箱" prop="contact_email">
                    <el-input v-model="companyParams.contact_email" placeholder="请输入联系邮箱"></el-input>
                </el-form-item>
                <el-form-item label="所属行业" prop="industry">
                    <el-input v-model="companyParams.industry" placeholder="请输入所属行业"></el-input>
                </el-form-item>
                <el-form-item label="公司规模" prop="scale">
                    <el-input v-model="companyParams.scale" placeholder="请输入规模 (如: small)"></el-input>
                </el-form-item>
                <el-form-item label="公司简介" prop="description">
                    <el-input type="textarea" v-model="companyParams.description" placeholder="请输入公司简介"></el-input>
                </el-form-item>
            </el-form>

            <template #footer>
                <el-button @click="cancel">取消</el-button>
                <el-button type="primary" @click="confirm" :loading="confirmLoading">确定</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
// 假设你的 API 路径正确
import { reqCompanyList, reqAddCompany, reqUpdateCompany, reqDeleteCompany } from '@/api/dimensions/dim_entity'
import type {
    CompanyDetailObj,
    CompanyListResponse,
    CompanyCreateRequest,
    CompanyUpdateRequest
} from '@/api/dimensions/dim_entity/type'

// --- 状态定义 ---
const pageNo = ref<number>(1)
const limit = ref<number>(10)
const searchKeyword = ref<string>('')
const total = ref<number>(0)
const companyList = ref<CompanyDetailObj[]>([])
const dialogFormVisible = ref<boolean>(false)
const confirmLoading = ref<boolean>(false)
const formRef = ref<FormInstance>()


// 定义一个扩展类型，包含 id 用于编辑模式
type CompanyFormType = CompanyCreateRequest & { id?: number }

// 表单数据
const companyParams = reactive<CompanyFormType>({
    name: '',
    company_code: '',
    address: '',
    contact_person: '',
    contact_phone: '',
    contact_email: '',
    industry: '',
    scale: 'small', // 默认值
    description: '',
    id: undefined // 编辑时会有值
})

// 简单的表单验证规则
const formRules = reactive<FormRules>({
    name: [{ required: true, message: '请输入公司名称', trigger: 'blur' }],
    company_code: [{ required: true, message: '请输入公司代码', trigger: 'blur' }]
})



// --- 方法定义 ---

// 获取列表
const getCompanyList = async () => {

    const result: CompanyListResponse = await reqCompanyList(pageNo.value, limit.value, searchKeyword.value)
    if (result.code === 200 && result.data) {
        total.value = result.data.total
        companyList.value = result.data.items
    }
}

// 初始化
import { onMounted } from 'vue'
onMounted(() => {
    getCompanyList()
})

// 点击“添加”
const addCompany = () => {
    dialogFormVisible.value = true
    // 重置表单和数据
    companyParams.id = undefined
    companyParams.name = ''
    companyParams.company_code = ''
    companyParams.address = ''
    companyParams.contact_person = ''
    companyParams.contact_phone = ''
    companyParams.contact_email = ''
    companyParams.industry = ''
    companyParams.scale = 'small'
    companyParams.description = ''

    nextTick(() => {
        formRef.value?.clearValidate()
    })
}

// 点击“修改”
const updateCompany = (row: CompanyDetailObj) => {
    dialogFormVisible.value = true

    // 使用 Object.assign 复制数据，并确保 id 被复制
    // 注意：row 中必须有 id 字段
    Object.assign(companyParams, row)

    // 如果后端返回的 id 字段名不是 id 而是 company_id，需要手动映射
    // companyParams.id = row.id || row.company_id 

    nextTick(() => {
        formRef.value?.clearValidate()
    })
}

// 点击“确定” (核心修改逻辑)
const confirm = async () => {
    // 1. 表单校验
    if (!formRef.value) return
    await formRef.value.validate(async (valid) => {
        if (!valid) return

        confirmLoading.value = true
        try {
            let result
            // 2. 判断是新增还是修改
            if (companyParams.id) {
                // --- 修改逻辑 ---
                // 构造更新数据 (排除掉一些不需要更新的字段，或者只传变化的字段)
                // 注意：reqUpdateCompany 需要两个参数：id 和 data
                const updateData: CompanyUpdateRequest = {
                    name: companyParams.name,
                    address: companyParams.address,
                    contact_person: companyParams.contact_person,
                    contact_phone: companyParams.contact_phone,
                    contact_email: companyParams.contact_email,
                    industry: companyParams.industry,
                    scale: companyParams.scale,
                    description: companyParams.description,



                    // status 如果需要更新也可以加上
                }

                result = await reqUpdateCompany(companyParams.id, updateData)

                if (result.code === 200) {
                    ElMessage.success('修改成功')
                } else {
                    ElMessage.error(result.message || '修改失败')
                }
            } else {
                // --- 新增逻辑 ---
                // 构造新增数据 (确保没有 id 字段)
                const createData: CompanyCreateRequest = {
                    name: companyParams.name,
                    company_code: companyParams.company_code,
                    address: companyParams.address,
                    contact_person: companyParams.contact_person,
                    contact_phone: companyParams.contact_phone,
                    contact_email: companyParams.contact_email,
                    industry: companyParams.industry,
                    scale: companyParams.scale,
                    description: companyParams.description,

                }

                result = await reqAddCompany(createData)

                if (result.code === 200) {
                    ElMessage.success('添加成功')
                } else {
                    ElMessage.error(result.message || '添加失败')
                }
            }

            // 3. 成功后关闭弹窗并刷新列表
            if (result && result.code === 200) {
                dialogFormVisible.value = false
                getCompanyList()
                // 如果是修改后回到第一页，或者保持当前页，视需求而定
                // 如果新增导致页数变化，可能需要重新计算 pageNo，这里简单处理重新加载
            }
        } catch (error) {
            console.error(error)
            ElMessage.error('操作发生异常')
        } finally {
            confirmLoading.value = false
        }
    })
}

// 点击“取消”
const cancel = () => {
    dialogFormVisible.value = false
    formRef.value?.resetFields()
}

// 删除公司 (补充实现)
const deleteCompany = async (row: CompanyDetailObj) => {
    const result = await reqDeleteCompany(row.id)
    if (result.code === 200) {
        ElMessage.success('删除成功')
        getCompanyList()
    } else {
        ElMessage.error(result.message || '删除失败')
    }
}
</script>

<style scoped lang="scss"></style>