<!-- src/components/MonthPicker.vue -->
<template>
    <el-date-picker v-model="selectedMonth" type="month" :placeholder="placeholder" :format="format"
        :value-format="valueFormat" :clearable="clearable" :disabled="disabled" :readonly="readonly"
        :editable="editable" :size="size" style="width: 100%" @change="handleChange" @focus="handleFocus"
        @blur="handleBlur" @clear="handleClear" />
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';

// --- Props 定义 ---
interface Props {
    modelValue?: string | null;           // v-model 绑定的值
    placeholder?: string;                  // 占位文本
    format?: string;                        // 显示格式，如 YYYY-MM
    valueFormat?: string;                   // 值格式，如 YYYY-MM
    clearable?: boolean;                     // 是否可清空
    disabled?: boolean;                      // 是否禁用
    readonly?: boolean;                      // 是否只读
    editable?: boolean;                      // 是否可编辑
    size?: 'large' | 'default' | 'small';    // 尺寸
}

const props = withDefaults(defineProps<Props>(), {
    modelValue: '',
    placeholder: '请选择期间',
    format: 'YYYY-MM',
    valueFormat: 'YYYY-MM',
    clearable: true,
    disabled: false,
    readonly: false,
    editable: true,
    size: 'default',
});

// --- Emits 定义 ---
const emit = defineEmits<{
    (e: 'update:modelValue', val: string | null): void;
    (e: 'change', val: string | null): void;
    (e: 'focus', event: FocusEvent): void;
    (e: 'blur', event: FocusEvent): void;
    (e: 'clear'): void;
}>();

// --- 状态管理 ---
const selectedMonth = ref<string | null>(props.modelValue);

// --- 事件处理 ---

/**
 * 值变化时的处理
 */
const handleChange = (val: string | null) => {


    // 更新内部状态
    selectedMonth.value = val;

    // 1. 发射 update:modelValue，更新父组件的 v-model
    emit('update:modelValue', val);

    // 2. 发射 change 事件，方便父组件监听变化
    emit('change', val);
};

/**
 * 获取焦点时的处理
 */
const handleFocus = (event: FocusEvent) => {
    emit('focus', event);
};

/**
 * 失去焦点时的处理
 */
const handleBlur = (event: FocusEvent) => {
    emit('blur', event);
};

/**
 * 清空时的处理
 */
const handleClear = () => {
    emit('update:modelValue', null);
    emit('change', null);
    emit('clear');
};

// --- 监听外部 v-model 变化 ---
watch(
    () => props.modelValue,
    (newVal) => {
        // 避免死循环：只有当外部值和内部值不一致时才更新
        if (newVal !== selectedMonth.value) {
            selectedMonth.value = newVal;
        }
    }
);
</script>