<template>



    <template v-for="(item) in menuList" :key="item.path">
        <!-- 没有子路由 -->
        <template v-if="!item.children">
            <el-menu-item :index="item.path" v-if="!item.meta.hidden" @click="goRoute">
                <el-icon>
                    <component :is="item.meta.icon"></component>
                </el-icon>
                <template #title>

                    <span>{{ item.meta.title }}</span>
                </template>
            </el-menu-item>


        </template>
        <!-- 有且只有1个子路由 -->
        <template v-if="item.children && item.children.length == 1">
            <el-menu-item :index="item.children[0].path" v-if="!item.children[0].meta.hidden" @click="goRoute">
                <el-icon>
                    <component :is="item.children[0].meta.icon"></component>
                </el-icon>
                <template #title>


                    <span>{{ item.children[0].meta.title }}</span>

                </template>

            </el-menu-item>
        </template>
        <!-- 有2个及其以上子路由 -->
        <el-sub-menu v-if="item.children && item.children.length > 1" :index="item.path">
            <template #title>
                <el-icon>
                    <component :is="item.meta.icon"></component>
                </el-icon>
                <span>{{ item.meta.title }}</span>
            </template>
            <Lmenu :menuList="item.children" />
        </el-sub-menu>

    </template>




</template>

<script setup lang="ts">

// 定义组件名
defineOptions({
    name: 'Lmenu'
})
import { useRouter } from 'vue-router';
// 获取父组件传递过来的全部路由数组
defineProps(['menuList']);


// 获取路由器对象
const $router = useRouter()
const goRoute = (vc: any) => {
    $router.push(vc.index)
}


</script>




<style scoped lang="scss"></style>