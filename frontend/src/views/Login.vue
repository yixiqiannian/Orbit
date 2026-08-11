<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

async function handleLogin() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await userStore.login(form.username, form.password)
      ElMessage.success('登录成功')
      router.push('/')
    } catch (e: any) {
      ElMessage.error(e?.response?.data?.detail || '登录失败')
    } finally {
      loading.value = false
    }
  })
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-title">
        <span class="login-logo">Orbit</span>
      </div>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="0"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            size="large"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item class="login-btn-item">
          <el-button
            type="primary"
            size="large"
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
/* ==========================================================================
   登录页 — 玻璃拟态（MASTER.md: Glassmorphism）
   浅色：极浅底 + 蓝/橙氛围光斑；深色：深蓝紫底 + 大光晕
   ========================================================================== */
.login-page {
  position: relative;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background-color: var(--color-background, #f8fafc);
  /* 基础氛围光斑（与 Layout 一致的蓝/橙 radial-gradient） */
  background-image:
    radial-gradient(900px 620px at 10% -8%, rgba(37, 99, 235, 0.16), transparent 62%),
    radial-gradient(760px 520px at 96% 6%, rgba(249, 115, 22, 0.14), transparent 62%),
    radial-gradient(700px 540px at 82% 104%, rgba(59, 130, 246, 0.12), transparent 60%);
  transition: background-color 0.3s ease;
}

/* 大光晕光斑（增强玻璃折射质感）：左上蓝、右下橙 */
.login-page::before {
  content: '';
  position: absolute;
  left: 8%;
  top: 14%;
  width: 520px;
  height: 520px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(37, 99, 235, 0.5), rgba(37, 99, 235, 0.16) 48%, transparent 70%);
  filter: blur(72px);
  pointer-events: none;
}

.login-page::after {
  content: '';
  position: absolute;
  right: 9%;
  bottom: 12%;
  width: 460px;
  height: 460px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(249, 115, 22, 0.42), rgba(249, 115, 22, 0.14) 48%, transparent 70%);
  filter: blur(72px);
  pointer-events: none;
}

/* ---------- 深色模式：深蓝紫氛围底 + 更亮的光晕 ---------- */
html[data-theme='dark'] .login-page {
  background-image:
    radial-gradient(900px 640px at 12% -6%, rgba(37, 99, 235, 0.28), transparent 62%),
    radial-gradient(760px 540px at 94% 8%, rgba(249, 115, 22, 0.18), transparent 62%),
    radial-gradient(760px 600px at 84% 104%, rgba(124, 58, 237, 0.2), transparent 62%);
}

html[data-theme='dark'] .login-page::before {
  background: radial-gradient(circle, rgba(59, 130, 246, 0.6), rgba(59, 130, 246, 0.18) 48%, transparent 70%);
}

html[data-theme='dark'] .login-page::after {
  background: radial-gradient(circle, rgba(249, 115, 22, 0.5), rgba(249, 115, 22, 0.16) 48%, transparent 70%);
}

/* ---------- 玻璃登录卡片 ---------- */
.login-card {
  position: relative;
  z-index: 1;
  width: 400px;
  padding: 44px 40px 36px;
  background: var(--surface, rgba(255, 255, 255, 0.55));
  backdrop-filter: var(--glass-filter, blur(20px));
  -webkit-backdrop-filter: var(--glass-filter, blur(20px));
  border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.6));
  border-radius: 32px; /* 24–40px 大圆角 */
  box-shadow:
    0 24px 50px -12px rgba(15, 23, 42, 0.28),
    0 0 44px -8px rgba(37, 99, 235, 0.35); /* 蓝色光晕阴影 */
  transition: background-color 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
}

html[data-theme='dark'] .login-card {
  box-shadow:
    0 24px 50px -12px rgba(0, 0, 0, 0.6),
    0 0 48px -6px rgba(59, 130, 246, 0.4);
}

/* ---------- Orbit 文字 Logo（Fredoka + 品牌渐变） ---------- */
.login-title {
  text-align: center;
  margin: 0 0 32px;
}

.login-logo {
  font-family: var(--font-display, 'Fredoka', 'DM Sans', sans-serif);
  font-size: 42px;
  font-weight: 700;
  letter-spacing: 1px;
  background: var(--gradient-brand, linear-gradient(90deg, #2563eb, #3b82f6, #f97316));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
}

/* ---------- 玻璃质感输入框 ---------- */
.login-card :deep(.el-input__wrapper) {
  min-height: 46px;
  padding: 2px 14px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  box-shadow: 0 0 0 1px var(--el-border-color, #e5e7eb) inset;
  transition: background-color 0.2s ease, box-shadow 0.2s ease;
}

.login-card :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--color-primary, #2563eb) inset;
}

.login-card :deep(.el-input__wrapper.is-focus) {
  background: rgba(255, 255, 255, 0.85);
  box-shadow:
    0 0 0 1px var(--color-primary, #2563eb) inset,
    0 0 14px rgba(37, 99, 235, 0.28);
}

html[data-theme='dark'] .login-card :deep(.el-input__wrapper) {
  background: rgba(30, 41, 59, 0.5);
}

html[data-theme='dark'] .login-card :deep(.el-input__wrapper.is-focus) {
  background: rgba(30, 41, 59, 0.8);
}

.login-btn-item {
  margin-top: 4px;
}

/* ---------- 渐变登录按钮（#2563EB→#3B82F6 + 圆角 12px + hover 发光） ---------- */
.login-btn.el-button--primary {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 2px;
  border: none;
  border-radius: 12px;
  color: #fff;
  background: var(--gradient-brand-blue, linear-gradient(90deg, #2563eb, #3b82f6));
  box-shadow: 0 8px 20px -6px rgba(37, 99, 235, 0.5);
  transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
}

.login-btn.el-button--primary:hover {
  color: #fff;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  box-shadow: 0 0 26px rgba(37, 99, 235, 0.55), 0 8px 20px -6px rgba(37, 99, 235, 0.5);
  transform: translateY(-1px);
  filter: brightness(1.05);
}

.login-btn.el-button--primary:active {
  transform: translateY(0);
  box-shadow: 0 4px 14px -4px rgba(37, 99, 235, 0.5);
  filter: brightness(0.97);
}

html[data-theme='dark'] .login-btn.el-button--primary {
  box-shadow: 0 8px 24px -6px rgba(37, 99, 235, 0.6);
}

html[data-theme='dark'] .login-btn.el-button--primary:hover {
  box-shadow: 0 0 30px rgba(59, 130, 246, 0.6), 0 8px 24px -6px rgba(37, 99, 235, 0.55);
}

/* 移动端适配 */
@media (max-width: 480px) {
  .login-card {
    width: calc(100vw - 48px);
    padding: 36px 28px 30px;
  }

  .login-logo {
    font-size: 36px;
  }
}
</style>
