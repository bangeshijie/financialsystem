import os
import uuid
import aiofiles
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException
from PIL import Image
import io
from db.session import ASYNC_DATABASE_URL

from typing import Optional

class Settings():
    # 数据库配置
    DATABASE_URL: str = ASYNC_DATABASE_URL

    # 文件上传配置
    UPLOAD_DIR: str = "static/uploads/avatars"
    MAX_UPLOAD_SIZE: int = 2 * 1024 * 1024  # 2MB
    ALLOWED_EXTENSIONS: set = {"jpg", "jpeg", "png", "gif", "webp"}

    # 服务配置
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")




settings = Settings()

# 确保上传目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# 定义默认头像文件名常量
DEFAULT_AVATAR_FILENAME = "totoro.png"


class AvatarUpload:
    """头像上传处理类"""

    @staticmethod
    async def save_avatar(file: UploadFile) -> str:
        """
        保存头像文件
        返回: 保存的文件名
        """
        # 验证文件类型
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")

        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型，仅支持: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )

        # 验证文件大小
        content = await file.read()
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小不能超过 {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
            )

        # 生成唯一文件名
        filename = f"{uuid.uuid4().hex}.{file_extension}"
        filepath = os.path.join(settings.UPLOAD_DIR, filename)

        # 压缩并保存图片
        try:
            # 使用PIL压缩图片
            img = Image.open(io.BytesIO(content))

            # 转换为RGB（如果是RGBA）
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            # 设置最大尺寸为500x500
            max_size = 500
            if img.width > max_size or img.height > max_size:
                ratio = min(max_size / img.width, max_size / img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            # 压缩质量
            output = io.BytesIO()
            # 注意：如果原图是webp/gif，这里强制转为了PNG或JPEG，可能需要根据业务调整
            save_format = 'JPEG' if file_extension in ['jpg', 'jpeg'] else 'PNG'

            img.save(output, format=save_format, quality=85, optimize=True)
            compressed_content = output.getvalue()

            # 异步保存文件
            async with aiofiles.open(filepath, 'wb') as f:
                await f.write(compressed_content)

            return filename

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"图片处理失败: {str(e)}"
            )

    @staticmethod
    def get_avatar_url(filename: str) -> str:
        """获取头像的完整URL"""
        if not filename:
            return ""
        return f"/static/uploads/avatars/{filename}"

    @staticmethod
    async def delete_old_avatar(filename: str):
        """
        删除旧头像文件
        保护逻辑：如果文件名是默认头像 (totoro.png)，则不执行物理删除。
        """
        if not filename:
            return

        # 【关键修改】检查是否为默认头像
        if filename == DEFAULT_AVATAR_FILENAME:
            print(f"[SKIP] 尝试删除默认头像 '{filename}'，已跳过物理删除操作以保护资源。")
            return

        filepath = os.path.join(settings.UPLOAD_DIR, filename)

        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"[SUCCESS] 成功删除旧头像文件: {filename}")
            except Exception as e:
                print(f"[ERROR] 删除旧头像失败: {filename}, 错误信息: {e}")
        else:
            # 文件不存在可能是已经被删了，或者路径不对，通常不需要报错，记录一下即可
            print(f"[INFO] 未找到要删除的头像文件: {filepath}")
