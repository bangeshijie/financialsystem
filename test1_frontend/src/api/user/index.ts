// 统一管理项目用户相关的接口
import request from '@/utils/request';
import type { loginFormData, loginResponseData, userInfoResponseData, updatePasswordData, updatePasswordResponseData } from './type';
// 项目用户相关的请求地址
export const API = {
    LOGIN_URL: "/user/login",
    USERINFO_URL: "/user/info",
    LOGOUT_URL: "/user/logout",
    REGISTER_URL: "/user/register",     //暂时后端没写接口,前端也没界面不用
    CHANGE_PASSWORD_URL: "/user/password",
    UPLOAD_AVATAR_URL: "/user/avatar/upload",  // 新增：上传头像接口

} as const;
// 登录的接口
export const reqLogin = (data: loginFormData) => request.post<any, loginResponseData>(API.LOGIN_URL, data);

// 获取用户信息的接口

export const reqUserInfo = () => request.get<any, userInfoResponseData>(API.USERINFO_URL);
// 退出登录
export const reqLogout = () => request.post<any, any>(API.LOGOUT_URL)
// 修改密码
export const reqChangePassword = (data: updatePasswordData) => request.put<any, updatePasswordResponseData>(API.CHANGE_PASSWORD_URL, data)
// 上传头像
export const reqUploadAvatar = (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return request.post<any, any>(API.UPLOAD_AVATAR_URL, formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    });
};