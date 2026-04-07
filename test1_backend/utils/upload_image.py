import os
import uuid
import aiofiles
from pathlib import Path
from typing import Optional, List
from fastapi import UploadFile, HTTPException
from PIL import Image
import io
from db.session import ASYNC_DATABASE_URL

from typing import Optional

class Settings:
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
    async def delete_old_avatar(filename: str, silent: bool = True) -> bool:
        """
        删除旧头像文件（支持同步和异步）

        Args:
            filename: 头像文件名
            silent: 是否静默失败（不抛出异常）

        Returns:
            bool: 是否删除成功
        """
        if not filename:
            return False

        # 保护默认头像
        if filename == DEFAULT_AVATAR_FILENAME:
            if not silent:
                print(f"[SKIP] 默认头像 '{filename}' 受到保护，不会删除")
            return False

        filepath = os.path.join(settings.UPLOAD_DIR, filename)

        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"[SUCCESS] 删除头像文件: {filename}")
                return True
            except Exception as e:
                if not silent:
                    raise HTTPException(
                        status_code=500,
                        detail=f"删除头像文件失败: {str(e)}"
                    )
                print(f"[ERROR] 删除头像失败: {filename}, 错误: {e}")
                return False
        else:
            print(f"[INFO] 头像文件不存在: {filepath}")
            return False

    @staticmethod
    async def delete_avatar_batch(filenames: List[str]) -> dict:
        """
        批量删除头像文件

        Returns:
            {
                "success": ["file1.jpg", "file2.jpg"],
                "failed": ["file3.jpg"]
            }
        """
        result = {"success": [], "failed": []}

        for filename in filenames:
            success = await AvatarUpload.delete_old_avatar(filename, silent=True)
            if success:
                result["success"].append(filename)
            else:
                result["failed"].append(filename)

        return result