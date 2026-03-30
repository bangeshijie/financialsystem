<template>
    <div>
        <el-card>
            <el-form :inline="true" class="form">
                <el-form-item label="职位搜索">
                    <el-input placeholder="请你输入搜索职位关键字" v-model="keyword"></el-input>
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" size="default" :disabled="keyword ? false : true"
                        @click="search">搜索</el-button>
                    <el-button type="primary" size="default" @click="reset">重置</el-button>
                </el-form-item>
            </el-form>
        </el-card>
        <el-card style="margin: 10px 0px;">
            <el-button type="primary" size="default" icon="Plus" @click="addRole">添加职位</el-button>
            <el-table border style="margin: 10px 0px;" :data="allRole">
                <el-table-column type="index" align="center" label="#"></el-table-column>
                <el-table-column label="ID" align="center" prop="role_id" width="80px"></el-table-column>
                <el-table-column label="职位名称" align="center" prop="role_name" show-overflow-tooltip
                    width="200px"></el-table-column>
                <el-table-column label="职位描述" align="center" prop="remark" show-overflow-tooltip></el-table-column>
                <el-table-column label="创建时间" align="center" show-overflow-tooltip
                    prop="created_time"></el-table-column>
                <el-table-column label="更新时间" align="center" show-overflow-tooltip
                    prop="updated_time"></el-table-column>
                <el-table-column label="操作" width="280px" align="center">
                    <!-- row:已有的职位对象 -->
                    <template #="{ row }">
                        <el-button type="primary" size="small" icon="User" @click="setPermisstion(row)">分配权限</el-button>
                        <el-button type="primary" size="small" icon="Edit" @click="updateRole(row)">编辑</el-button>
                        <el-popconfirm :title="`你确定要删除${row.role_name}?`" width="260px"
                            @confirm="removeRole(row.role_id)">
                            <template #reference>
                                <el-button type="danger" size="small" icon="Delete">删除</el-button>
                            </template>
                        </el-popconfirm>
                    </template>
                </el-table-column>
            </el-table>
            <el-pagination v-model:current-page="pageNo" v-model:page-size="pageSize" :page-sizes="[5, 10, 20, 50]"
                :background="true" layout="prev, pager, next, jumper,->,sizes,total" :total="roleTotal"
                @current-change="getHasRole" @size-change="sizeChange" />
        </el-card>
        <!-- 添加职位与更新已有职位的结构:对话框 -->
        <el-dialog v-model="dialogVisite" :title="RoleParams.role_id ? '更新职位' : '添加职位'">
            <el-form :model="RoleParams" :rules="rules" ref="form">
                <el-form-item label="职位名称" prop="role_name">
                    <el-input placeholder="请你输入职位名称" v-model="RoleParams.role_name"></el-input>
                </el-form-item>
                <el-form-item label="职位描述" prop="remark">
                    <el-input placeholder="请你输入职位描述" v-model="RoleParams.remark"></el-input>
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button type="primary" size="default" @click="dialogVisite = false">取消</el-button>
                <el-button type="primary" size="default" @click="save">确定</el-button>
            </template>
        </el-dialog>
        <!-- 抽屉组件:分配职位的菜单权限与按钮的权限 -->
        <el-drawer v-model="showDrawer">
            <template #header>
                <h4>分配菜单与按钮的权限</h4>
            </template>


            <template #default>
                <!-- 树形控件 -->
                <!-- show-checkbox 是复选框  -->
                <!-- node-key 每个树节点用来作为唯一标识的属性，整棵树应该是唯一的 -->
                <!-- default-expand-all 默认全部展开 -->
                <el-tree ref="tree" :data="menuArr" show-checkbox node-key="menu_id" default-expand-all
                    :default-checked-keys="selectArr" :props="defaultProps" />
            </template>


            <template #footer>
                <div style="flex: auto">
                    <el-button @click="showDrawer = false">取消</el-button>
                    <el-button type="primary" @click="handler">确定</el-button>
                </div>
            </template>
        </el-drawer>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, nextTick } from 'vue';
//请求方法
import { reqRemoveRole, reqAllRoleList, reqAddOrUpdateRole, reqAllMenuList, reqAssignMenuPermissions } from '@/api/acl/role';
import type { RoleListResponse, RoleItem, RoleData, MenuList } from '@/api/acl/role/type'
//引入骨架的仓库
import useLayOutSettingStore from '@/store/modules/setting';
import { ElMessage, type FormInstance } from 'element-plus';
const settingStore = useLayOutSettingStore();
//当前页码
const pageNo = ref<number>(1);
//一页展示几条数据
const pageSize = ref<number>(10);
//搜索职位关键字
const keyword = ref<string>('');
//存储全部已有的职位
const allRole = ref<RoleItem[]>([]);
//职位总个数
const roleTotal = ref<number>(0);
//控制对话框的显示与隐藏
const dialogVisite = ref<boolean>(false);
//获取form组件实例
const form = ref<FormInstance>();
//控制抽屉显示与隐藏
const showDrawer = ref<boolean>(false);
//收集新增岗位数据
const RoleParams = reactive<RoleData>({
    role_name: '',
    remark: ''
})
//准备一个数组:数组用于存储勾选的节点的ID(四级的)
const selectArr = ref<number[]>([]);
//定义数组存储用户权限的数据
const menuArr = ref<MenuList>([]);
//获取tree组件实例
const tree = ref<any>();
//树形控件的映射
const defaultProps = {
    id: 'menu_id',      // 指定使用 menu_id 作为唯一标识
    children: 'children',
    label: 'name',
}
//组件挂载完毕
onMounted(() => {
    //获取职位请求
    getHasRole();
});
//获取全部用户信息的方法|分页器当前页码发生变化的回调
const getHasRole = async (pager = 1) => {
    //修改当前页码
    pageNo.value = pager;
    let result: RoleListResponse = await reqAllRoleList(pageNo.value, pageSize.value, keyword.value);
    if (result.code == 200) {
        roleTotal.value = result.data.total;
        allRole.value = result.data.items;
    }
}
//下拉菜单的回调
const sizeChange = () => {
    getHasRole();
}
//搜索按钮的回调
const search = () => {
    //再次发请求根据关键字
    getHasRole();
    keyword.value = '';
}
//重置按钮的回调
const reset = () => {
    settingStore.refsh = !settingStore.refsh;
}
//添加职位按钮的回调
const addRole = () => {
    //对话框显示出来
    dialogVisite.value = true;
    // 清空数据
    Object.assign(RoleParams, {
        role_name: '',
        remark: '',
        role_id: 0,
    });
    //清空上一次表单校验错误结果
    nextTick(() => {
        form.value?.clearValidate('role_name');
    })

}
//更新已有的职位按钮的回调
const updateRole = (row: RoleData) => {
    //显示出对话框
    dialogVisite.value = true;
    //存储已有的职位----带有ID的
    Object.assign(RoleParams, row);
    //清空上一次表单校验错误结果
    nextTick(() => {
        form.value?.clearValidate('role_name');
    })
}
//自定义校验规则的回调
const validatorRoleName = (_rule: any, value: any, callBack: any) => {
    if (value.trim().length >= 2) {
        callBack();
    } else {
        callBack(new Error('职位名称至少两位'))
    }
}
//职位校验规则
const rules = {
    role_name: [
        { required: true, trigger: 'blur', validator: validatorRoleName }
    ]
}

//确定按钮的回调
const save = async () => {
    //表单校验结果,结果通过在发请求、结果没有通过不应该在发生请求
    await form.value?.validate();
    //添加职位|更新职位的请求
    let result: any = await reqAddOrUpdateRole(RoleParams);
    if (result.code == 200) {
        //提示文字
        ElMessage({ type: 'success', message: RoleParams.role_id ? '更新成功' : '添加成功' });
        //对话框显示
        dialogVisite.value = false;
        //再次获取全部的已有的职位
        getHasRole(RoleParams.role_id ? pageNo.value : 1);
    }
}

// 辅助函数：递归收集选中的节点ID
const collectCheckedIds = (menuList: any, ids: number[] = []) => {
    if (!menuList || menuList.length === 0) return ids;

    menuList.forEach((item: any) => {
        if (item.selected) {
            ids.push(item.menu_id);
        }
        if (item.children && item.children.length > 0) {
            collectCheckedIds(item.children, ids);
        }
    });

    return ids;
}

// 分配权限按钮的回调
const setPermisstion = async (row: RoleData) => {
    showDrawer.value = true;
    Object.assign(RoleParams, row);

    // 清空之前的数据
    selectArr.value = [];
    menuArr.value = [];

    // 获取菜单树数据
    let result: any = await reqAllMenuList((RoleParams.role_id as number));

    if (result.code == 200) {
        // 打印完整的数据结构
        console.log('完整返回数据:', result);
        console.log('菜单树数据:', JSON.stringify(result.data, null, 2));

        // 检查第一个节点是否有 selected 字段
        if (result.data && result.data.length > 0) {
            console.log('第一个节点:', result.data[0]);
            console.log('第一个节点是否有selected字段:', 'selected' in result.data[0]);
            console.log('第一个节点的selected值:', result.data[0].selected);
        }

        menuArr.value = result.data;

        // 收集选中的节点ID并设置默认勾选
        const selectedIds = collectCheckedIds(result.data);
        console.log('收集到的选中节点ID:', selectedIds);

        selectArr.value = selectedIds;
    }
}



// 抽屉确定按钮的回调
const handler = async () => {
    const role_id = (RoleParams.role_id as number);
    // 获取所有选中的节点ID（包括半选和全选）
    let checkedKeys = tree.value.getCheckedKeys();
    let halfCheckedKeys = tree.value.getHalfCheckedKeys();
    let permissionId = [...checkedKeys, ...halfCheckedKeys];

    let result: any = await reqAssignMenuPermissions(role_id, permissionId);

    if (result.code == 200) {
        showDrawer.value = false;
        ElMessage({ type: 'success', message: '分配权限成功' });
    }
}

//删除已有的职位
const removeRole = async (role_id: number) => {
    let result: any = await reqRemoveRole(role_id);
    if (result.code == 200) {
        //提示信息
        ElMessage({ type: 'success', message: '删除成功' });
        getHasRole(allRole.value.length > 1 ? pageNo.value : pageNo.value - 1);
    }
}
</script>

<style scoped>
.form {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 50px;
}
</style>