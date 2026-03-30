



//------------------------------登录界面验证输入账号密码相关代码---------------------//

// 引入数据类型
import type { ValidationRule } from "@/api/user/type";

export const validateUsername: ValidationRule['validator'] = (_rule: any, value: string, callback: any) => {
    if (!value || value.trim() === '') {
        callback(new Error('用户名不能为空'));
        return;
    }

    if (value.length <= 4) {
        callback(new Error('用户名长度必须大于4位'));
        return;
    }

    const userReg = /^[a-zA-Z0-9_]+$/;
    if (!userReg.test(value)) {
        callback(new Error('用户名只能包含字母、数字和下划线'));
    } else {
        callback();
    }
};

export const validatePassword: ValidationRule['validator'] = (_rule: any, value: string, callback: any) => {
    if (!value || value.trim() === '') {
        callback(new Error('密码不能为空'));
        return;
    }

    if (value.length <= 5) {
        callback(new Error('密码长度必须大于5位'));
        return;
    }

    const pwdReg = /^[a-zA-Z0-9_]+$/;
    if (!pwdReg.test(value)) {
        callback(new Error('密码只能包含字母、数字和下划线'));
    } else {
        callback();
    }
};
