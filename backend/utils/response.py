# utils/response.py
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Any, Optional

def success_response(
    message: str = "操作成功",
    data: Any = None,
    status_code: int = 200
):
    """
    统一成功响应
    :param message: 提示信息
    :param data: 数据 payload
    :param status_code: HTTP 状态码 (默认 200, 创建资源时用 201)
    """
    content = {
        "code": status_code,  # 业务代码通常与 HTTP 状态码同步，也可根据需求固定
        "message": message,
        "data": data,
        "ok": True
    }

    return JSONResponse(
        content=jsonable_encoder(content),
        status_code=status_code
    )

def error_response(
    message: str = "操作失败",
    status_code: int = 400,
    data: Any = None
):
    content = {
        "code": status_code,
        "message": message,
        "data": data,
        "ok": False
    }
    return JSONResponse(
        content=jsonable_encoder(content),
        status_code=status_code
    )