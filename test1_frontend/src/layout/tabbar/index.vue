<script setup lang="ts">

// 定义组件名
defineOptions({
    name: 'Tabbar'
})
import Breadcrumb from './breadcrumb/index.vue'
import Setting from './setting/index.vue'




</script>

<template>
    <div class="tabbar">
        <!-- 顶部左边 -->
        <div class="tabbar_left">

            <!-- 顶部左边面包屑 -->
            <Breadcrumb></Breadcrumb>

        </div>

        <!-- 顶部右边 -->
        <div class="tabbar_right">
            <Setting></Setting>

        </div>

    </div>

</template>

<style scoped lang="scss">
.tabbar {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: space-between;
    background-image: linear-gradient(to right, rgb(3, 143, 152), rgb(99, 86, 150), rgb(26, 22, 114));


}


.tabbar_left {
    display: flex;
    align-items: center;
    margin-left: 20px;
}

.tabbar_right {
    display: flex;

    align-items: center;


}
</style>
