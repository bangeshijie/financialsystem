<template>
  <div class="project-container">
    <!-- 项目头部信息卡片 -->
    <el-card class="header-card" shadow="hover">
      <div class="header-content">
        <div class="project-title">
          <h1>{{ projectInfo.name }}</h1>
          <el-tag type="success" effect="dark" class="version-tag">v{{ projectInfo.currentVersion }}</el-tag>
        </div>
        <p class="project-desc">{{ projectInfo.description }}</p>

        <div class="tech-stack">
          <el-tag v-for="tech in projectInfo.techStack" :key="tech" class="tech-item">
            {{ tech }}
          </el-tag>
        </div>

        <div class="action-buttons">
          <el-button type="primary" icon="Download">查看文档</el-button>
          <el-button icon="PhoneFilled">联系我们</el-button>
        </div>
      </div>
    </el-card>

    <!-- 版本更新历史 -->
    <el-card class="history-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>更新日志</span>
        </div>
      </template>

      <el-timeline class="custom-timeline">
        <el-timeline-item v-for="(release, index) in releaseHistory" :key="index" :timestamp="release.date"
          placement="top" :type="index === 0 ? 'primary' : 'success'" :hollow="index !== 0">
          <div class="release-item">
            <div class="release-header">
              <h3>{{ release.version }}</h3>
              <el-tag size="small" :type="getTagType(release.type)">{{ release.type }}</el-tag>
            </div>

            <el-collapse accordion>
              <el-collapse-item name="1">
                <template #title>
                  <div class="changelog-summary">
                    <span v-if="release.features.length">✨ 新增 {{ release.features.length }} 项</span>
                    <span v-if="release.fixes.length" class="fix-count">🐛 修复 {{ release.fixes.length }} 项</span>
                  </div>
                </template>

                <div class="changelog-details">
                  <!-- 新增功能列表 -->
                  <div v-if="release.features.length" class="change-section">
                    <h4>新增功能</h4>
                    <ul>
                      <li v-for="(feat, idx) in release.features" :key="idx">{{ feat }}</li>
                    </ul>
                  </div>

                  <!-- 修复列表 -->
                  <div v-if="release.fixes.length" class="change-section">
                    <h4>Bug 修复</h4>
                    <ul>
                      <li v-for="(fix, idx) in release.fixes" :key="idx">{{ fix }}</li>
                    </ul>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

// --- 类型定义 ---
interface Release {
  version: string;
  date: string;
  type: 'Major' | 'Minor' | 'Patch';
  features: string[];
  fixes: string[];
}

interface ProjectInfo {
  name: string;
  currentVersion: string;
  description: string;
  techStack: string[];
}

// --- 模拟数据 ---
const projectInfo = ref<ProjectInfo>({
  name: '财经管理系统',
  currentVersion: '1.0.1',
  description: '这是一个前端基于 Vue 3 后端基于fastapi+mysql 构建的现代化企业级后台管理系统。主要功能包括用户权限管理、数据可视化大屏、财务报表分析等，旨在帮助企业高效管理财务数据和报表可视化。',
  techStack: ['Vue 3', 'TypeScript', 'Vite', 'Element Plus', 'Pinia', 'SCSS', 'ECharts', 'fastapi', 'mysql', 'redis']
});

const releaseHistory = ref<Release[]>([
  {
    version: 'v1.0.1',
    date: '2026-4-1',
    type: 'Minor',
    features: [
      '新增暗黑模式自动切换功能',
      '表格组件支持动态列配置',
      '集成 ECharts 5.0 数据可视化大屏'
    ],
    fixes: [
      '修复了移动端侧边栏无法收起的问题',
      '修复登录页面在高分屏下的样式错位'
    ]
  },
  {
    version: 'v1.0.0',
    date: '2026-03-30',
    type: 'Patch',
    features: [
      '优化了 axios 请求拦截器的错误处理机制'
    ],
    fixes: [
      '修复了用户管理页面删除操作不刷新的问题',
      '修复了部分文字颜色对比度不足的问题'
    ]
  }

]);

// --- 辅助函数 ---
const getTagType = (type: string) => {
  switch (type) {
    case 'Major': return 'danger';
    case 'Minor': return 'warning';
    default: return 'info';
  }
};
</script>

<style scoped lang="scss">
// 变量定义
$primary-color: #409eff;
$text-color-regular: #606266;
$border-color: #dcdfe6;

.project-container {
  max-width: 900px;

  padding: 0 20px;

  .header-card {
    margin-bottom: 30px;
    border-radius: 10px;

    .header-content {
      padding: 10px 0;

      .project-title {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 15px;

        h1 {
          margin: 0;
          font-size: 28px;
          color: #303133;
          font-weight: 600;
        }

        .version-tag {
          font-size: 14px;
        }
      }

      .project-desc {
        color: $text-color-regular;
        line-height: 1.6;
        margin-bottom: 20px;
        font-size: 16px;
      }

      .tech-stack {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-bottom: 25px;

        .tech-item {
          background-color: #f4f4f5;
          color: #909399;
          border: none;
          font-weight: 500;
        }
      }

      .action-buttons {
        display: flex;
        gap: 15px;
      }
    }
  }

  .history-card {
    border-radius: 10px;

    .card-header {
      font-size: 18px;
      font-weight: bold;
    }

    .custom-timeline {
      padding: 20px 0;

      // 深度选择器修改 Element UI 默认样式
      :deep(.el-timeline-item__node) {
        border-width: 4px;
      }

      .release-item {
        background: #fff;
        padding: 10px 0;

        .release-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 10px;

          h3 {
            margin: 0;
            font-size: 18px;
            color: #303133;
          }
        }

        .changelog-summary {
          font-size: 14px;
          color: $text-color-regular;
          width: 100%;

          .fix-count {
            margin-left: 10px;
          }
        }

        .changelog-details {
          padding: 10px 10px 0;
          background-color: #fcfcfc;
          border-radius: 4px;

          .change-section {
            margin-bottom: 15px;

            h4 {
              margin: 0 0 10px 0;
              font-size: 14px;
              color: #303133;
              border-left: 3px solid $primary-color;
              padding-left: 8px;
            }

            ul {
              margin: 0;
              padding-left: 20px;
              color: $text-color-regular;

              li {
                margin-bottom: 6px;
                line-height: 1.5;
                font-size: 13px;
              }
            }
          }
        }
      }
    }
  }
}

// 响应式适配
@media (max-width: 768px) {
  .project-container {
    padding: 0 10px;

    .header-content {
      .project-title {
        flex-direction: column;
        align-items: flex-start;
      }
    }
  }
}
</style>