//登录接口需要携带参数ts类型

export interface loginFormData {
    username: string;
    password: string;
}

// 用户登录界面 登陆时表单数据校验规则ts类型
export interface ValidationRule {
    required?: boolean;
    message?: string;
    trigger?: string;
    validator?: (rule: any, value: string, callback: (error?: Error) => void) => void;
}


export interface ResponseData {
    code: number;

    message: string;
    ok: boolean



}
//用户信息返回数据ts类型
export interface loginResponseData<T = any> extends ResponseData {
    data: T;
}


export interface userInfoResponseData extends ResponseData {

    data: {


        id: number,
        user_id: number,
        username: string,
        nickname: string,
        avatar: string,
        gender: string,
        bio: string,
        email: string,
        created_time: string,
        updated_time: string,


        roles?: string[],
        routes?: string[],
        buttons?: string[],


    };

}

// 用户修改密码参数ts类型
export interface updatePasswordData {
    oldPassword: string;
    newPassword: string;
}

export interface updatePasswordResponseData extends ResponseData {
    data: null;

}