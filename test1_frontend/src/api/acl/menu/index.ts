import request from '@/utils/request'
import type { PermisstionResponseData, MenuParams } from './type'
//枚举地址
export const API = {
  //获取全部菜单与按钮的标识数据
  ALLPERMISSTION_URL: '/user/menus/tree',
  //给某一级菜单新增一个子菜单
  ADDMENU_URL: '/user/addmenu',
  //更新某一个已有的菜单
  UPDATE_URL: '/user/updatemenu/',
  //删除已有的菜单
  DELETEMENU_URL: '/user/inactivemenu/',
} as const
//获取菜单数据
export const reqAllPermisstion = () =>
  request.get<any, PermisstionResponseData>(API.ALLPERMISSTION_URL)
//添加与更新菜单的方法
export const reqAddOrUpdateMenu = (data: MenuParams) => {
  if (data.menu_id) {
    return request.put<any, any>(API.UPDATE_URL + data.menu_id, data)
  } else {
    return request.post<any, any>(API.ADDMENU_URL, data)
  }
}

//删除某一个已有的菜单
export const reqRemoveMenu = (menu_id: number) =>
  request.delete<any, any>(API.DELETEMENU_URL + menu_id)
