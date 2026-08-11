import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './assets/design-tokens.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import { useThemeStore } from './stores/theme'

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

const pinia = createPinia()
app.use(pinia)

// 启动时读取 localStorage('orbit-theme') 并设置 data-theme（默认 light；
// index.html 内联脚本已预置，这里通过 store 兜底并同步状态）
useThemeStore(pinia).applyStoredTheme()

app.use(router)
app.use(ElementPlus)
app.mount('#app')
