//角色管理模块的的接口
import request from '@/utils/request'
import type { RoleListResponse, RoleData, MenuResponseData } from './type'
//枚举地址
export const API = {
  //获取全部的职位接口
  ALLROLE_URL: '/user/rolelist',

  //新增岗位的接口地址
  ADDROLE_URL: '/user/role/addrole',

  //更新已有的职位
  UPDATEROLE_URL: '/user/role/',
  //删除已有的职位
  REMOVEROLE_URL: '/user/deleterole/',





  //获取全部的菜单与按钮的数据
  ALLPERMISSTION: '/user/menus/role/',
  //给相应的职位分配权限
  SETPERMISTION_URL: '/user/menus/assign_menu/',

} as const
//获取全部的角色


export const reqAllRoleList = (page: number, limit: number, role_name: string) => {
  return request.get<any, RoleListResponse>(API.ALLROLE_URL, {
    params: {
      page,
      limit,
      role_name: role_name || undefined // 如果为空字符串，传 undefined 让后端忽略该参数
    }
  });
};




//添加职位与更新已有职位接口
export const reqAddOrUpdateRole = (data: RoleData) => {
  if (data.role_id) {
    return request.put<any, any>(API.UPDATEROLE_URL + data.role_id, data)
  } else {
    return request.post<any, any>(API.ADDROLE_URL, data)
  }
}

//删除已有的职位
export const reqRemoveRole = (role_id: number) =>
  request.delete<any, any>(API.REMOVEROLE_URL + role_id)










//获取全部菜单与按钮权限数据
export const reqAllMenuList = (role_id: number) =>
  request.get<any, MenuResponseData>(API.ALLPERMISSTION + role_id)


//给相应的职位下发权限
export const reqAssignMenuPermissions = (role_id: number, permissionId: number[]) =>
  request.post(
    API.SETPERMISTION_URL + role_id, permissionId
  )
