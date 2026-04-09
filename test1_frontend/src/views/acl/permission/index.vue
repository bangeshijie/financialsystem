<template>
    <div>
        <!-- indent 展示树形数据时，树节点的缩进长度  :indent="16" - JavaScript 表达式，会被解析为数字,不能用 indent=16 -->
        <el-table :data="permisstionArr" style="width: 100%; margin-bottom: 20px" row-key="menu_id" border :indent="16">
            <el-table-column prop="name" label="名称" width="200px"></el-table-column>
            <el-table-column prop="code" label="权限值" width="200px"></el-table-column>
            <el-table-column prop="updateTime" label="修改时间" width="150px" show-overflow-tooltip></el-table-column>
            <el-table-column label="操作" width="300px" align="right">
                <template #="{ row }">
                    <el-button @click="addPermission(row)" type="primary" size="small" icon="plus"
                        :disabled="row.level == 4 ? true : false">{{
                            row.level == 3 ? "添加功能" : " 添加菜单" }}</el-button>
                    <el-button @click="updatePermission(row)" type="primary" size="small" icon="edit"
                        :disabled="row.level == 1 ? true : false">编辑</el-button>

                    <el-popconfirm :title="`你确定要删除${row.name}?`" width="200px" @confirm="removeMenu(row.menu_id)">
                        <template #reference>
                            <el-button type="danger" size="small"
                                :disabled="row.level == 1 ? true : false">删除</el-button>
                        </template>
                    </el-popconfirm>

                </template>


            </el-table-column>
        </el-table>

        <!-- 对话框显示 -->
        <el-dialog v-model="showDialog" :title="menuData.menu_id ? '更新菜单' : '添加菜单'">
            <!-- 表单组件 -->
            <el-form>
                <el-form-item label="名称">
                    <el-input placeholder="请输入菜单名称" v-model="menuData.name"></el-input>

                </el-form-item>
                <el-form-item label="权限">
                    <el-input placeholder="请输入权限数值" v-model="menuData.code"></el-input>

                </el-form-item>

            </el-form>
            <span class="dialog-footer">
                <el-button @click="showDialog = false">取消</el-button>
                <el-button @click="save" type="primary">确定 </el-button>
            </span>



        </el-dialog>
    </div>
</template>










<script setup lang="ts">


import { ref, onMounted, reactive } from 'vue'
import { reqAddOrUpdateMenu, reqAllPermisstion, reqRemoveMenu } from '@/api/acl/menu';
import type { PermisstionResponseData, Permisstion, MenuParams } from '@/api/acl/menu/type'
import { ElMessage } from 'element-plus';



// 存储菜单数据
const permisstionArr = ref<Permisstion[]>([])
//控制对话框显示和隐藏
const showDialog = ref<boolean>(false)




onMounted(() => {
    getHasPermisstion()
})
// 获取菜单数据的方法
const getHasPermisstion = async () => {
    let result: PermisstionResponseData = await reqAllPermisstion()
    if (result.code == 200) {
        permisstionArr.value = result.data

        console.log(permisstionArr.value)

    }
}

//携带的参数
let menuData = reactive<MenuParams>({
    code: "",
    level: 0,
    name: "",
    pid: 0,  //父亲的id  parentid
    type: 1,
    to_code: "",
    status: "active"

})


//添加按钮 
const addPermission = (row: Permisstion) => {
    // 清空数据
    Object.assign(menuData,
        // 清空数据  id也清掉
        {
            menu_id: 0,
            code: "",
            level: 0,
            name: "",
            pid: 0,
        }
    )
    showDialog.value = true
    menuData.level = row.level + 1
    if (row.level === 3) {
        menuData.type = 2
    }
    // 给谁追加子菜单
    menuData.pid = row.menu_id as number

}



//编辑按钮 
const updatePermission = (row: Permisstion) => {
    showDialog.value = true
    Object.assign(menuData, row)
}


// 确定按钮的回调
const save = async () => {
    let result = await reqAddOrUpdateMenu(menuData)


    if (result.code == 200 || result.code == 201) {


        showDialog.value = false
        ElMessage({
            type: 'success',
            message: menuData.menu_id ? '更新成功' : '添加成功'
        })
        getHasPermisstion()
    }

}


// 删除
const removeMenu = async (menu_id: number) => {
    let result: any = await reqRemoveMenu(menu_id)

    if (result.code == 200 || result.code == 204) {
        ElMessage({
            type: 'success',
            message: '删除成功'
        })
        getHasPermisstion()
    }




}




</script>






<style scoped lang="scss"></style>
