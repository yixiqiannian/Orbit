# Orbit Design System — Glass Morphism（以 uupm.cc 配色为标准）

> 2026-08-11 更新：推翻第一版 Data-Dense 风格，改为 **玻璃拟态 (Glassmorphism) + 拟物化 + 极简 + 大圆角**。
> 配色实测自 https://www.uupm.cc/ 的 CSS（#2563EB 主蓝 + #F97316 橙色强调）。

## 风格定位

| 维度 | 选择 |
|------|------|
| 风格 | Glassmorphism（玻璃拟态）主 + Skeuomorphism（拟物化光影）辅 + Minimalism（极简） |
| 圆角 | 大圆角：16px（卡片）~ 40px（登录卡片/按钮） |
| 玻璃 | `backdrop-filter: blur(20px)` + 半透明背景 + 1px 半透明白边框 + 蓝色光晕阴影 |
| 模式 | 浅色 / 深色 双模式（`data-theme` 属性 + localStorage 持久化，默认浅色） |
| 动画 | hover 过渡 150-300ms、shimmer 微光、卡片 stagger 入场、渐变 CTA 发光 |

## 配色 Token（实测 uupm.cc）

### 浅色模式
| Role | Hex | 用途 |
|------|-----|------|
| Primary | `#2563EB` | 主色/按钮/链接/激活态 |
| Secondary | `#3B82F6` | 次级蓝/渐变搭档 |
| Accent | `#F97316` | 强调/CTA 橙色 |
| Background | `#F8FAFC` | 页面背景 |
| Surface | `rgba(255,255,255,0.55)` | 玻璃卡片（半透明白） |
| Border | `rgba(255,255,255,0.6)` / `#E5E7EB` | 玻璃描边 |
| Text | `#0F172A` | 主文字（slate-900） |
| Text Muted | `#94A3B8` | 次要文字（slate-400） |
| Destructive | `#FB2C36` | 危险 |

### 深色模式
| Role | Hex | 用途 |
|------|-----|------|
| Primary | `#3B82F6` | 主色（浅蓝，深底上更亮） |
| Secondary | `#60A5FA` | 次级蓝 |
| Accent | `#F97316` | 强调橙（不变） |
| Background | `#0F172A` | 页面背景（slate-900） |
| Surface | `#111827D9`（`rgba(17,24,39,0.85)`） | 玻璃卡片 |
| Border | `rgba(255,255,255,0.1)` | 玻璃描边 |
| Text | `#F1F5F9` | 主文字 |
| Text Muted | `#94A3B8` | 次要文字 |
| Destructive | `#F87171` | 危险 |

### 渐变（CTA/品牌）
```css
background: linear-gradient(90deg, #2563eb, #3b82f6);        /* 双蓝 */
background: linear-gradient(90deg, #2563eb, #3b82f6, #f97316); /* 蓝→蓝→橙 品牌渐变 */
background: linear-gradient(to bottom right, rgba(37,99,235,0.2), transparent, rgba(249,115,22,0.2)); /* 玻璃氛围光 */
```

## 字体
- **正文**: DM Sans（uupm.cc 实际字体）`https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,100..1000&display=swap`
- **标题**: Fredoka（uupm.cc 标题字体）`https://fonts.googleapis.com/css2?family=Fredoka:wght@300..700&display=swap`
- **数据/代码**: Fira Code 或系统 mono

## 玻璃拟态 CSS 范式

```css
.glass-card {
  background: var(--surface);                    /* 半透明 */
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border);
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1);
}
.glass-card-hover:hover {
  background: rgba(255,255,255,0.95);            /* 浅色 hover 实底 */
  box-shadow: 0 0 20px rgba(37,99,235,0.3);      /* 蓝色光晕 */
}
.dark .glass-card { background: rgba(17,24,39,0.85); }
```

## 动画范式

```css
/* hover 过渡（150-300ms） */
.card { transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease; }
.card:hover { transform: translateY(-2px); }

/* shimmer 微光（加载/按钮） */
@keyframes shimmer { to { transform: translateX(100%); } }

/* 卡片 stagger 入场 */
.fade-in-up { animation: fadeInUp 0.4s ease both; }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: none; } }

/* CTA 发光脉冲 */
@keyframes glowPulse { 0% { box-shadow: 0 0 20px rgba(37,99,235,0.3); } 50% { box-shadow: 0 0 40px rgba(37,99,235,0.6); } 100% { box-shadow: 0 0 20px rgba(37,99,235,0.3); } }
```

## 主题切换机制
- `<html data-theme="light|dark">`，默认 light
- localStorage key: `orbit-theme`，启动时读取，未设置默认 light
- Header 放切换按钮（太阳/月亮图标），点击切换并持久化
- `prefers-reduced-motion: reduce` 时禁用动画

## 注意
- 玻璃拟态 Accessibility 需保证文字对比度 4.5:1（卡片 hover 实底化有助于此）
- 不要用 emoji 当图标（用 Element Plus 图标或 SVG）
- 背景可加渐变氛围光（蓝色/橙色 radial-gradient 大光斑），增强玻璃质感
