//账号信息的ts类型
export interface ResponseData {
  code: number
  message: string
  ok: boolean
}



//代表一个账号信息的ts类型
export interface User {
  id?: number
  user_id?: number
  created_time?: string
  updated_time?: string
  username?: string
  password?: string
  nickname?: string
  phone?: null
  roles?: string[]
}
//数组包含全部的用户信息
export type Records = User[]
//获取全部用户信息接口返回的数据ts类型
export interface UserResponseData extends ResponseData {
  data: {
    items: Records
    total: number
    size: number
    current: number
    pages: number
  }
}


export interface UserDeleterequest {
  username: string | string[];
}











//代表一个职位的ts类型
export interface RoleData {
  role_id?: number
  role_name: string
  remark: null
}
//全部职位的列表
export type AllRole = RoleData[]
//获取全部职位的接口返回的数据ts类型
export interface AllRoleResponseData extends ResponseData {
  data: {

    username: string
    assign_roles: AllRole
    all_roles: AllRole
  }
}






export interface SetRoleData {
  role_ids: number[];
}
