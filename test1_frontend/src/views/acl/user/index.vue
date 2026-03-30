<template>
    <div>
        <el-card>
            <el-form :inline="true" class="form">
                <el-form-item>
                    <el-input placeholder="请输入搜索用户名" v-model="keyword"></el-input>
                </el-form-item>
                <el-form-item>
                    <el-button @click="search" type="primary" size="default"
                        :disabled="keyword ? false : true">搜索</el-button>
                    <el-button @click="reset" type="primary" size="default">重置</el-button>
                </el-form-item>

            </el-form>
        </el-card>
        <el-card style="margin: 10px 0px">
            <el-button type="primary" size="default" @click="addUser">添加用户</el-button>
            <el-button @click="deleteSelectUser()" type="primary" size="default"
                :disabled="selectUsernameArr.length ? false : true">批量删除</el-button>

            <!-- table展示用户信息 -->
            <!-- selection-change是table的选中事件，当用户点击table的复选框时，会触发selection-change事件，
 -->
            <el-table @selection-change="selectChange" style="margin: 10px 0px" border :data="userArr"
                :tooltip-formatter="tableRowFormatter">
                <el-table-column type="selection" align="center"></el-table-column>
                <el-table-column label="#" type="index" align="center"></el-table-column>
                <el-table-column label="ID" prop="id" width="80" align="center"></el-table-column>
                <el-table-column label="用户姓名" prop="username" width="120" align="center"></el-table-column>
                <el-table-column label="用户昵称" prop="nickname" width="120" align="center"></el-table-column>


                <el-table-column label="用户角色" prop="roles"
                    :tooltip-formatter="({ row }: { row: User }) => row.roles?.join(', ') || ''" width="240"
                    align="center">
                    <template #default="{ row }">
                        <el-tag v-for="tag in row.roles" :key="tag" class="tag-item" type="primary">
                            {{ tag }}
                        </el-tag>
                    </template>

                </el-table-column>







                <el-table-column label="创建时间" show-overflow-tooltip prop="created_time" width="180"
                    align="center"></el-table-column>
                <el-table-column label="更新时间" show-overflow-tooltip prop="updated_time" width="180"
                    align="center"></el-table-column>
                <el-table-column label="操作" width="300" align="center">
                    <template #="{ row }">
                        <el-button type="primary" size="small" icon="user" @click="setRole(row)">分配角色</el-button>


                        <el-popconfirm :title="`你确定要重置${row.username}的密码吗?`" width="260px"
                            @confirm="ResetUserpwd(row.username)">
                            <template #reference>
                                <el-button type="primary" size="small" icon="RefreshLeft">重置密码</el-button>
                            </template>
                        </el-popconfirm>

                        <el-popconfirm :title="`你确定要删除${row.username}?`" width="260px"
                            @confirm="deleteSelectUser(row.username)">
                            <template #reference>
                                <el-button type="danger" size="small" icon="Delete">删除</el-button>
                            </template>
                        </el-popconfirm>
                    </template>
                </el-table-column>

            </el-table>
            <!-- 分页器 -->
            <el-pagination @change="getHasUser" v-model:current-page="pageNo" v-model:page-size="pageLimit"
                :page-sizes="[5, 10, 20]" size="small" :disabled="disabled" :background="true"
                layout=" prev, pager, next, jumper ,->, sizes,total" :total="userTotal"></el-pagination>



        </el-card>
        <!-- 抽屉结构 -->
        <el-drawer v-model="showDrawer">
            <template #header>
                <h4>添加用户</h4>
            </template>
            <template #default>
                <el-form :model="userParams" :rules="rules" ref="formRef">
                    <el-form-item label="用户姓名:" prop="username">
                        <el-input placeholder="请输入用户姓名" v-model="userParams.username"></el-input>
                    </el-form-item>
                    <el-form-item label="用户昵称:" prop="nickname">
                        <el-input placeholder="请输入用户昵称" v-model="userParams.nickname"></el-input>
                    </el-form-item>
                    <el-form-item label="用户密码:" prop="password">
                        <el-input placeholder="请输入用户密码" v-model="userParams.password"></el-input>
                    </el-form-item>
                </el-form>
            </template>
            <template #footer>
                <div style="flex: auto;">
                    <el-button @click="cancel"> 取消</el-button>
                    <el-button type="primary" @click="save">确认</el-button>
                </div>

            </template>



        </el-drawer>
        <!-- 抽屉结构:用户某一个已有的账号进行职位分配 -->
        <el-drawer v-model="showDrawer1">
            <template #header>
                <h4>分配角色(职位)</h4>
            </template>
            <template #default>
                <el-form>
                    <el-form-item label="用户姓名">
                        <el-input v-model="userParams.username" :disabled="true"></el-input>
                    </el-form-item>
                    <el-form-item label="职位列表">
                        <el-checkbox @change="handleCheckAllChange" v-model="checkAll"
                            :indeterminate="isIndeterminate">全选</el-checkbox>
                        <!-- 显示职位的的复选框 -->
                        <el-checkbox-group v-model="userRole" @change="handleCheckedCitiesChange">
                            <el-checkbox v-for="(role, index) in allRole" :key="index" :value="role"
                                :label="role.role_name" />
                        </el-checkbox-group>
                    </el-form-item>
                </el-form>
            </template>
            <template #footer>
                <div style="flex: auto">
                    <el-button @click="showDrawer1 = false">取消</el-button>
                    <el-button type="primary" @click="updateSave">确定</el-button>
                </div>
            </template>
        </el-drawer>

    </div>
</template>
<script setup lang="ts">

import { ref, onMounted, reactive, nextTick } from 'vue';
import { reqSelectUser, reqUserInfo, reqAllRole, reqSetUserRole, reqResetPassword, reqAddUser } from '@/api/acl/user'
import type { SetRoleData, UserResponseData, Records, User, AllRoleResponseData, AllRole } from '@/api/acl/user/type';
import useLayoutSettingStore from '@/store/modules/setting';
import { ElMessage } from 'element-plus';
import type { CheckboxValueType, TableTooltipData } from 'element-plus'

// 当前页码
const pageNo = ref<number>(1)
// 每一页展示多少数据
const pageLimit = ref<number>(5)
// 存储已有品牌的数据总数
const userTotal = ref<number>(0)

const keyword = ref<string>('')

const disabled = ref(false)   //分页器是否禁用
const userArr = ref<Records>([])

const userParams = reactive<User>({
    username: '',
    nickname: '',
    password: ''

})
// 组件挂载完毕
onMounted(() => {
    getHasUser()
})


// 格式化角色显示（将数组转为分号分隔的字符串）


const tableRowFormatter = (data: TableTooltipData<User[]>) => {
    return `${data.cellValue}: table formatter`
}

const getHasUser = async () => {
    //收集当前页码

    let result: UserResponseData = await reqUserInfo(pageNo.value, pageLimit.value, keyword.value)

    if (result.code == 200) {

        console.log(result)
        userTotal.value = result.data.total
        userArr.value = result.data.items

    }
}
// 1搜索功能
const search = () => {
    getHasUser()
    // 清空关键字
    keyword.value = ''
}



// 2重置功能
const settingStore = useLayoutSettingStore()
const reset = () => {
    settingStore.refsh = !settingStore.refsh

}

// 3添加用户功能
const showDrawer = ref<boolean>(false)
//获取form组件实例
const formRef = ref<any>();
const addUser = () => {
    showDrawer.value = true
    Object.assign(userParams, {
        id: undefined,
        username: '',
        nickname: '',
        password: ''
    })
    //清除上一次的错误的提示信息   clearValidate是el-form的方法清理某个字段的表单验证信息。
    nextTick(() => {
        formRef.value.clearValidate('username');
        formRef.value.clearValidate('nickname');
        formRef.value.clearValidate('password');
    });

}


const save = async () => {
    await formRef.value.validate()
    // 表单验证成功
    // 添加用户
    // console.log(userParams)


    let result: any = await reqAddUser(userParams)
    if (result.code == 201) {
        ElMessage.success('添加用户成功')
        showDrawer.value = false
        getHasUser()

    } else {
        ElMessage.error('添加用户失败')
    }
}
const cancel = () => {
    showDrawer.value = false
}

//校验用户名字回调函数
const validatorUsername = (_rule: any, value: any, callBack: any) => {
    //用户名字|昵称,长度至少五位
    if (value.trim().length >= 5) {
        callBack();
    } else {
        callBack(new Error('用户名字至少五位'))
    }
}
//校验用户名字回调函数
const validatorNickname = (_rule: any, value: any, callBack: any) => {
    //用户名字|昵称,长度至少五位
    if (value.trim().length >= 5) {
        callBack();
    } else {
        callBack(new Error('用户昵称至少五位'))
    }
}
const validatorPassword = (_rule: any, value: any, callBack: any) => {
    //用户名字|昵称,长度至少五位
    if (value.trim().length >= 6) {
        callBack();
    } else {
        callBack(new Error('用户密码至少六位'))
    }
}
//表单校验的规则对象
const rules = {
    //用户名字
    username: [{ required: true, trigger: 'blur', validator: validatorUsername }],
    //用户昵称
    nickname: [{ required: true, trigger: 'blur', validator: validatorNickname }],
    //用户的密码
    password: [{ required: true, trigger: 'blur', validator: validatorPassword }],
}

// 5重置用户密码功能
const ResetUserpwd = async (username: string) => {

    let result: any = await reqResetPassword(username)
    if (result.code == 200) {
        ElMessage.success('重置密码成功')
    }

}

// 6分配角色功能

// 分配角色抽屉的显示隐藏
const showDrawer1 = ref<boolean>(false)
// 获取所有角色
const allRole = ref<AllRole>([])
const userRole = ref<AllRole>([])
const setRole = async (row: User) => {


    Object.assign(userParams, row)
    let result: AllRoleResponseData = await reqAllRole((userParams.username as string))
    console.log(result)

    if (result.code == 200) {
        allRole.value = result.data.all_roles
        userRole.value = result.data.assign_roles
        showDrawer1.value = true
    }
}

const checkAll = ref<boolean>(false)

// el组件属性 :设置不确定状态,仅负责样式控制

const isIndeterminate = ref<boolean>(true)
// 全选复选框的change事件
const handleCheckAllChange = (val: CheckboxValueType) => {
    userRole.value = val ? allRole.value : []
    isIndeterminate.value = false
}
const handleCheckedCitiesChange = (value: CheckboxValueType[]) => {
    const checkedCount = value.length
    checkAll.value = checkedCount === allRole.value.length
    isIndeterminate.value = checkedCount > 0 && checkedCount < allRole.value.length
}


// 抽屉里 修改保存按钮的请求
const updateSave = async () => {
    // 收集参数
    let data: SetRoleData = {

        role_ids: userRole.value.map(item => {
            return item.role_id as number
        })
    }


    let result = await reqSetUserRole((userParams.username as string), data)

    if (result.code == 200) {


        ElMessage({
            type: 'success',
            message: '分配角色成功'
        })
        showDrawer1.value = false
        getHasUser()
    }
}





// 准备一个数组来存储复选框勾选的变量
const selectUsernameArr = ref<string[]>([])
// 复选框勾选会触发的事件

const selectChange = (value: User[]) => {
    selectUsernameArr.value = value.map(item => item.username as string)

    console.log(value)
    console.log(selectUsernameArr.value)
}

// 批量删除按钮的回调
const deleteSelectUser = async (usernames?: string | string[]) => {
    // 如果没有传入参数，则使用选中的用户名数组
    // 如果传入了参数，则使用传入的用户名（单个或数组）
    const targetUsernames = usernames || selectUsernameArr.value

    // 检查是否有要删除的用户
    if (!targetUsernames || (Array.isArray(targetUsernames) && targetUsernames.length === 0)) {
        ElMessage.warning('请选择要删除的用户')
        return
    }

    try {
        let result = await reqSelectUser(targetUsernames)
        // 成功的情况
        console.log('成功:', result)
        if (result.code == 200) {
            ElMessage.success(result.message)
            getHasUser()
            // 清空选中的用户（如果是批量删除）
            if (!usernames) {
                selectUsernameArr.value = []
            }
        }
    } catch (error: any) {
        // 错误的情况 - 现在 error 就是后端返回的数据对象
        ElMessage.error(error.message || '删除用户失败')
    }
}

</script>



<style scoped lang="scss">
.form {
    display: flex;
    justify-content: space-between;
    align-items: center;
}



.tag-item+.tag-item {
    margin-left: 5px;
}
</style>
