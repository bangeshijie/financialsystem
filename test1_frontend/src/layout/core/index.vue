<template>

    <!-- 路由组件的出口的位置 -->
    <router-view v-slot="{ Component }">
        <transition name="fade">
            <!-- 渲染layout一级路由组件的子路由 -->
            <component :is="Component" v-if="flag" />
        </transition>
    </router-view>

</template>



<script setup lang="ts">
// 定义组件名
defineOptions({
    name: 'Core'
})
import { watch, ref, nextTick } from 'vue'
import useLayoutSettingStore from '@/store/modules/setting';
let layOutSettingStore = useLayoutSettingStore();

// 控制当前组件是否销毁重建
let flag = ref(true);



//监听仓库数据是否发生变化,变化就说明点击过刷新按钮
watch(() => layOutSettingStore.refsh, () => {
    flag.value = false;


    nextTick(() => {
        flag.value = true
    })

})





</script>



<style scoped lang="scss">
.fade-enter-from {
    opacity: 0;
    transform: scale(0);
}

.fade-enter-active {
    transition: all 1s;
}

.fade-enter-to {
    opacity: 1;
    transform: scale(1);
}
</style>