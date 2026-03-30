import type { RouteRecordRaw } from "vue-router";



// 定义小仓库state类型
export interface UserState {
    token: string | null;
    menuRoutes: RouteRecordRaw[];
    bio: string | null;
    nickname: string | null;
    gender: string | null;
    avatar: string | null;
    user_id: number | null;
    username: string;


    buttons: string[]
    routes: string[]
    roles: string[]

}
