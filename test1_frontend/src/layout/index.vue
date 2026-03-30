<template>
    <div class="layout_container">
        <!-- 左侧菜单 -->
        <div class="layout_slider" :class="{ fold: layoutSettingStore.fold }">

            <Logo />
            <!-- 展示菜单 -->

            <!-- 滚动组件 -->
            <el-scrollbar class="scrollbar">
                <!-- 菜单组件 -->
                <!-- $route是宏函数可以不引用 -->
                <el-menu :collapse="layoutSettingStore.fold" :default-active="$route.path" class="scrollbarmenu"
                    active-text-color="yellowgreen">
                    <!-- 根据路由动态生成菜单 -->
                    <Lmenu :menuList="userStore.menuRoutes" />
                </el-menu>

            </el-scrollbar>



        </div>

        <!-- 顶部导航 -->
        <div class="layout_tabbar" :class="{ fold: layoutSettingStore.fold }">
            <Tabbar />

        </div>
        <!-- 主要内容区域 -->
        <div class="layout_main" :class="{ fold: layoutSettingStore.fold }">

            <Core />
        </div>

    </div>

</template>



<script setup lang="ts">
// 定义组件名
defineOptions({
    name: 'Layout'
})


// 引入左侧菜单logo子组件
import Logo from './logo/index.vue'
import Lmenu from './menu/index.vue'
// 引入右侧菜单logo子组件
import Tabbar from './tabbar/index.vue'

import Core from './core/index.vue'

// 导入 store
import { useUserStore } from '@/store/modules/user'
import useLayoutSettingStore from '@/store/modules/setting'


// 获取用户相关的小仓库

let userStore = useUserStore()
let layoutSettingStore = useLayoutSettingStore()

</script>





<style scoped lang="scss">
.layout_container {
    position: relative;
    width: 100%;
    height: 100vh;



}

.layout_slider {
    color: white;
    width: $base-menu-width;
    height: 100vh;
    background-color: $base-slider-bg-color;
    transition: all 0.3s;

    .scrollbar {
        width: 100%;
        height: calc(100vh - $base-menu-logo-height);

        .el-menu {
            border-right: none;
        }

        ;

        .scrollbarmenu {
            --el-menu-bg-color: #001529;
            --el-menu-text-color: white;
        }

    }



    &.fold {
        width: $base-menu-min-width
    }

}

.layout_tabbar {
    position: fixed;
    width: calc(100% - $base-menu-width);
    height: $base-tabbar-height;
    background-color: $base-tabbar-bg-color;
    top: 0px;
    left: $base-menu-width;
    transition: all 0.3s;

    &.fold {
        width: calc(100vw - $base-menu-min-width);
        left: $base-menu-min-width
    }


}

.layout_main {
    position: absolute;
    width: calc(100% - $base-menu-width);
    height: calc(100vh - $base-tabbar-height);
    background-color: $layout-main-bg-color;
    left: $base-menu-width;
    top: $base-tabbar-height;
    padding: 20px;
    overflow: auto;
    transition: all 0.3s;

    &.fold {
        width: calc(100vw - $base-menu-min-width);
        left: $base-menu-min-width
    }

}
</style>