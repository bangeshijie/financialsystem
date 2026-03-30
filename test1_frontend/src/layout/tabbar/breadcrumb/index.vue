<template>


    <!-- 顶部左边静态图标 -->
    <el-icon style="margin-right: 10px;" @click="changeIcon">
        <component :is="LayoutSettingStore.fold ? 'fold' : Expand"></component>
    </el-icon>

    <!-- 顶部左边面包屑 -->
    <el-breadcrumb :separator-icon="ArrowRight">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>

        <template v-for="(item, index) in $route.matched" :key="index">
            <el-breadcrumb-item v-if="item.meta.title" :to="item.path">
                <!-- 图标 -->
                <el-icon style="vertical-align:top;">
                    <component :is="item.meta.icon"></component>
                </el-icon>
                <!-- 标题 -->
                <span style="margin:0px 5px; ">{{ item.meta?.title || '' }}</span>
            </el-breadcrumb-item>
        </template>

    </el-breadcrumb>
</template>



<script setup lang="ts">
// 定义组件名
defineOptions({
    name: 'Breadcrumb'
})

import { ArrowRight, Expand } from '@element-plus/icons-vue';

import useLayoutSettingStore from '@/store/modules/setting';


//获取layout配置相关的仓库
let LayoutSettingStore = useLayoutSettingStore();

// 图标切换

const changeIcon = () => {
    LayoutSettingStore.fold = !LayoutSettingStore.fold
}



</script>



<style scoped lang="scss"></style>
