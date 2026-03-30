//用户管理模块的接口
import request from '@/utils/request'
import type {
  UserResponseData,
  User,
  AllRoleResponseData,
  SetRoleData,

} from './type'
//枚举地址
export const API = {
  //获取全部已有用户账号信息
  ALLUSER_URL: '/user/acl/userlist',
  //添加一个新的用户账号
  ADDUSER_URL: '/user/acl/adduser',
  //重置一个用户密码
  RESETEUSER_URL: '/user/acl/resetpwd/',
  //删除某一个账号
  DELETEUSER_URL: '/user/acl/deleteuser/',

  //获取全部职位,当前账号拥有的职位接口
  ALLROLEURL: '/user/acl/role/',

  //给已有的用户分配角色接口
  SETROLE_URL: '/user/acl/assignRole/',




  //批量删除的接口
  DELETEALLUSER_URL: '/user/deleteusers',
} as const
//获取用户账号信息的接口




export const reqUserInfo = (page: number, limit: number, username: string) => {
  return request.get<any, UserResponseData>(API.ALLUSER_URL, {
    params: {
      page,
      limit,
      username: username || undefined // 如果为空字符串，传 undefined 让后端忽略该参数
    }
  });
};


//添加用户用户的接口
export const reqAddUser = (data: User) => request.post<any, any>(API.ADDUSER_URL, data)

//  重置用户密码
export const reqResetPassword = (username: string) => request.post<any, any>(API.RESETEUSER_URL + username)



//获取全部职位以及包含当前用户的已有的职位
export const reqAllRole = (username: string) => request.get<any, AllRoleResponseData>(API.ALLROLEURL + username)


//分配职位
export const reqSetUserRole = (username: string, data: SetRoleData) => request.put<any, any>(API.SETROLE_URL + username, data)


//删除某一个账号的信息
export const reqRemoveUser = (username: string) =>
  request.delete<any, any>(API.DELETEUSER_URL + username)



/**
 * 删除用户（支持单个和批量）
 * @param username 可以是单个用户名 'zhangsan' 或 用户名列表 ['zhangsan', 'lisi']
 */
export const reqSelectUser = (username: string | string[]) => {
  return request.post<any, any>(API.DELETEALLUSER_URL, { username: username });
};












// //批量删除的接口
// export const reqSelectUser = (idList: number[]) =>
//   request.delete(API.DELETEALLUSER_URL, { data: idList })


