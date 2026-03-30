<template>
    <!-- 修改点 1: 添加 @change="handleChange" -->
    <!-- 启用远程搜索，需要将filterable和remote设置为true，同时传入一个remote-method。 remote-method为一个Function，
      它会在输入值发生变化时调用，参数为当前输入值。 需要注意的是，如果 el-option 是通过 v-for 指令渲染出来的，
      此时需要为 el-option 添加 key 属性， 且其值需具有唯一性，比如这个例子中的 item.value -->
    <el-select v-model="selectedValue" :placeholder="placeholder" filterable remote :remote-method="handleSearch"
        :loading="loading" clearable style="width: 100%" @focus="handleFocus" @clear="handleClear"
        @change="handleChange" popper-class="company-search-popper">
        <el-option v-for="item in options" :key="item.company_code" :label="item.name" :value="item.company_code">
            <span style="float: left">{{ item.company_code }}</span>
            <span style="float: right;">{{ item.name }}</span>
        </el-option>

        <!-- 无数据时的提示 -->
        <template #empty>
            <div v-if="loading">加载中...</div>
            <div v-else-if="options.length === 0 && hasSearched">无匹配的公司</div>
            <div v-else>请点击或输入搜索</div>
        </template>
    </el-select>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { reqCompanyOptions } from '@/api/dimensions/dim_entity';
import type { CompanyOptions, CompanyOptionsRequest, CompanyOptionsResponse } from '@/api/dimensions/dim_entity/type';

// --- Props 定义 ---
interface Props {
    modelValue?: string | number | null;
    placeholder?: string;
    defaultLimit?: number;
}

const props = withDefaults(defineProps<Props>(), {
    modelValue: '',
    placeholder: '请选择或搜索公司',
    defaultLimit: 50,
});

// --- Emits 定义 ---
const emit = defineEmits<{
    (e: 'update:modelValue', val: string | number | null): void;
    (e: 'change', val: string | number | null): void;
}>();

// --- 状态管理 ---
const selectedValue = ref<string | number | null>(props.modelValue);
const options = ref<CompanyOptions[]>([]);
const loading = ref(false);
const hasSearched = ref(false);

// --- 核心逻辑 ---

/**
 * 修改点 2: 新增 handleChange 方法
 * 当 el-select 的值改变时（用户选中某项），触发此方法
 */
const handleChange = (val: string | number | null) => {
    console.log('🏢 [CompanySelect] 内部选中值变化:', val);

    // 1. 先发射 update:modelValue，确保父组件 form.company_code 立即更新
    emit('update:modelValue', val);

    // 2. 再发射 change，此时父组件拿到的 form.company_code 已经是新值了
    emit('change', val);
};

const fetchOptions = async (keyword: string = '') => {
    loading.value = true;
    try {
        const params: CompanyOptionsRequest = {
            keyword: keyword || undefined,
            limit: props.defaultLimit,
        };

        const res: CompanyOptionsResponse = await reqCompanyOptions(params);

        if (res.code === 200) {
            options.value = res.data || [];
            hasSearched.value = true;
        } else {
            ElMessage.warning(res.message || '获取公司列表失败');
            options.value = [];
        }
    } catch (error) {
        console.error('Fetch company options error:', error);
        ElMessage.error('网络异常，请稍后重试');
        options.value = [];
    } finally {
        loading.value = false;
    }
};

const handleSearch = (query: string) => {
    if (query !== '') {
        fetchOptions(query);
    } else {
        fetchOptions('');
    }
};

const handleFocus = () => {
    if (options.value.length === 0 && !hasSearched.value) {
        fetchOptions('');
    }
};

const handleClear = () => {
    // 清空时也要发射事件，值为 null
    emit('update:modelValue', null);
    emit('change', null);
    fetchOptions('');
};

// 监听外部 v-model 变化，同步内部状态
watch(
    () => props.modelValue,
    (newVal) => {
        // 避免死循环：只有当外部值和内部值不一致时才更新
        if (newVal !== selectedValue.value) {
            selectedValue.value = newVal;
        }
    }
);
</script>

<style scoped>
/* 样式保持不变 */
</style>