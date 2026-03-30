


// https://vite.dev/config/
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

import { createSvgIconsPlugin } from 'vite-plugin-svg-icons'
import path from 'path'



export default defineConfig(({ mode }) => {
  // 获取各种环境下对应的变量
  let env = loadEnv(mode, process.cwd());

  return {
    plugins: [
      vue(),
      // 引入mock

      createSvgIconsPlugin({
        // 指定需要缓存的图标文件夹
        iconDirs: [path.resolve(process.cwd(), 'src/assets/icons')],
        // 指定symbolId格式
        symbolId: 'icon-[name]',
      })
    ],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
      },
      extensions: ['.mjs', '.js', '.mts', '.ts', '.jsx', '.tsx', '.json', '.vue', '.scss', '.css']
    },
    // scss 全局变量
    css: {
      preprocessorOptions: {
        scss: {

          additionalData: `@use "@/styles/variable.scss"as *;`,
        },
      },
    },
    // 代理跨域
    server: {
      port: 5173,
      open: true,
      proxy: {
        [env.VITE_APP_BASE_API]: {
          // 获取数据的服务器地址
          target: env.VITE_SERVE,
          // 需要代理跨域
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
        }
      }
    }
  }
})