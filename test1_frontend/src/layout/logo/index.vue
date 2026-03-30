<template>
    <div class="logo" v-if="setting.logoShow">
        <img :src="setting.logo" alt="">
        <p>{{ setting.title }}</p>
    </div>

</template>

<script setup lang="ts">
// 定义组件名
defineOptions({
    name: 'Logo'
})

// 引入标题logo设置
import setting from '@/setting'
</script>
<style scoped lang="scss">
.logo {
    width: 100%;
    height: $base-menu-logo-height;
    color: rgb(255, 255, 255);
    display: flex;
    align-items: center;
    padding-left: 10px;
    padding-top: 10px;




    img {
        width: 40px;
        height: 40px;
    }

    ;

    p {
        font-size: $base-menu-logo-title-fontsize;
        white-space: nowrap;
        margin-left: 10px;

    }

}
</style>