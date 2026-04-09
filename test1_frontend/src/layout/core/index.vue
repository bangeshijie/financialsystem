<template>
    <div class="core-container">
        <!-- 路由组件的出口的位置 -->
        <router-view v-slot="{ Component }">
            <transition name="fade">
                <!-- 渲染layout一级路由组件的子路由 -->
                <component :is="Component" v-if="flag" />
            </transition>
        </router-view>

        <!-- 底部备案号区域 -->

        <footer class="site-footer">
            <div class="footer-content">
                <!-- 公安备案 -->
                <a href="https://beian.mps.gov.cn/#/query/webSearch?code=33010902004606" rel="noreferrer"
                    target="_blank" class="footer-link">

                    <img src="@/assets/images/gongan.png"
                        style="width: 16px; height: 16px; display: inline-block; vertical-align: middle; margin-right: 4px; border: 0;"
                        alt="" />
                    浙公网安备33010902004606号
                </a>

                <!-- 分隔符 -->
                <span class="divider">|</span>

                <!-- 工信部备案 -->
                <a href="https://beian.miit.gov.cn/" target="_blank" class="footer-link">
                    浙ICP备2026020450号-1
                </a>
            </div>
        </footer>
    </div>
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
.core-container {
    // 确保容器至少占满全屏高度，这样 footer 才能被推到底部
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

// 如果需要 footer 始终在底部，可以使用 flex 布局
// router-view 部分占据剩余空间
// 这里假设 router-view 渲染的内容会自动撑开，或者您希望 footer 紧随内容之后
// 如果需要固定底部，可以使用 position: fixed; bottom: 0; width: 100%;

.site-footer {
    width: 100%;
    padding: 20px 0;
    background-color: #f5f5f5; // 背景色，根据设计需求调整
    border-top: 1px solid #eaeaea; // 顶部边框
    margin-top: auto; // 如果使用 flex 布局，这行可以将 footer 推到底部

    .footer-content {
        display: flex;
        justify-content: center; // 内容居中
        align-items: center;
        font-size: 12px;
        color: #666;

        .divider {
            margin: 0 10px;
            color: #dcdcdc;
        }

        .footer-link {
            color: #666;
            text-decoration: none;
            transition: color 0.3s;

            &:hover {
                color: #409eff; // 鼠标悬停颜色，根据主题色调整
            }
        }
    }
}

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