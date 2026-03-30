<template>
  <div>
    <el-card class="box">
      <div class="container">
        <!-- 左侧：图片 -->
        <div class="left-section">
          <el-upload class="avatar-uploader" action="#" :show-file-list="false" :http-request="handleCustomUpload"
            :before-upload="beforeAvatarUpload" :disabled="uploading">
            <div class="avatar-wrapper" :class="{ 'is-uploading': uploading }">
              <img v-if="imageUrl" :src="imageUrl" class="avatar" />
              <div v-else class="avatar-placeholder">
                <el-icon v-if="!uploading" class="avatar-uploader-icon">
                  <Plus />
                </el-icon>
                <el-icon v-else class="avatar-uploader-icon">
                  <Loading />
                </el-icon>
              </div>
              <!-- 遮罩层 -->
              <div v-if="imageUrl && !uploading" class="avatar-mask">
                <el-icon class="edit-icon">
                  <Edit />
                </el-icon>
                <span class="edit-text">修改头像</span>
              </div>
            </div>
          </el-upload>
          <div v-if="uploading" class="upload-tip">上传中...</div>
        </div>

        <!-- 右侧：文字信息 -->
        <div class="right-section">
          <h3 class="greeting">{{ getTimeState() }} {{ userStore.username }}</h3>
          <p class="welcome-text">欢迎来到XX平台</p>
          <p class="welcome-text">个性签名：{{ userStore.bio }}</p>
        </div>
      </div>
    </el-card>
    <div class="bottom">
      <svg-icon name="welcome" width="500px" height="500px"> </svg-icon>
    </div>
  </div>
</template>

<script setup lang="ts">
// 引入用户相关的仓库
import { useUserStore } from '@/store/modules/user';
import { getTimeState } from '@/utils/time'

import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Loading, Edit } from '@element-plus/icons-vue'

import type { UploadProps, UploadRequestOptions } from 'element-plus'
import { reqUploadAvatar } from '@/api/user/index'

const userStore = useUserStore()

const imageUrl = computed(() => userStore.avatar)
const uploading = ref(false)

// 自定义上传方法
const handleCustomUpload = async (options: UploadRequestOptions) => {
  const formData = new FormData()
  formData.append('file', options.file)

  try {
    uploading.value = true

    const result = await reqUploadAvatar(options.file)

    // 根据你的后端返回结构解析
    if (result.code === 200) {
      // 使用后端返回的完整 URL 更新 store
      userStore.avatar = result.data.avatar
      ElMessage.success('头像更新成功')
    } else {
      ElMessage.error(result.data.message || '头像更新失败')
    }
  } catch (error: any) {
    console.error('上传失败:', error)
    ElMessage.error(error.message || '上传失败，请重试')
  } finally {
    uploading.value = false
  }
}

// 文件上传前的校验
const beforeAvatarUpload: UploadProps['beforeUpload'] = (rawFile) => {
  // 支持更多图片格式
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
  const fileType = rawFile.type

  if (!allowedTypes.includes(fileType)) {
    ElMessage.error('请上传 JPG、PNG、GIF 或 WEBP 格式的图片！')
    return false
  } else if (rawFile.size / 1024 / 1024 > 2) {
    ElMessage.error('头像大小不能超过 2MB！')
    return false
  }
  return true
}

</script>

<style scoped lang="scss">
.box {
  padding: 20px;

  .container {
    display: flex;
    align-items: center;
    gap: 24px;

    .left-section {
      flex-shrink: 0;
      text-align: center;

      .avatar-uploader {
        cursor: pointer;
        display: inline-block;
      }

      .avatar-wrapper {
        position: relative;
        width: 100px;
        height: 100px;

        &.is-uploading {
          opacity: 0.7;
          pointer-events: none;
        }
      }

      .avatar {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #e6f7ff;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      }

      .avatar-placeholder {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background-color: #f5f7fa;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 3px solid #e6f7ff;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        cursor: pointer;

        &:hover {
          background-color: #ecf5ff;
        }
      }

      // 遮罩层样式
      .avatar-mask {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        border-radius: 50%;
        background: rgba(0, 0, 0, 0.6);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.3s ease;
        cursor: pointer;

        .edit-icon {
          font-size: 24px;
          color: #fff;
          margin-bottom: 4px;
        }

        .edit-text {
          font-size: 12px;
          color: #fff;
        }
      }

      // 鼠标悬停时显示遮罩
      .avatar-wrapper:hover .avatar-mask {
        opacity: 1;
      }

      .upload-tip {
        text-align: center;
        font-size: 12px;
        color: #999;
        margin-top: 8px;
      }
    }

    .right-section {
      flex: 1;

      .greeting {
        margin: 0 0 12px 0;
        font-size: 20px;
        color: #333;
        font-weight: 600;

        :deep(time-state) {
          color: #1890ff;
        }
      }

      .welcome-text {
        margin: 0 0 16px 0;
        font-size: 16px;
        color: #666;
      }
    }
  }
}

.bottom {
  display: flex;
  justify-content: center;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
}
</style>