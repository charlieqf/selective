# UI/UX 设计指南

## 1. 设计原则

### 1.1 核心原则

**简洁高效（Simplicity First）**
- 学生使用场景：在做题间隙快速上传，不能打断学习流程
- 界面简洁，核心功能突出
- 减少点击次数，优化操作流程

**移动优先（Mobile First）**
- 主要上传场景在移动端（手机拍照）
- 触摸友好的设计
- 大按钮、清晰的视觉层次

**激励导向（Motivation Driven）**
- 学习进度可视化
- 成就系统（连续学习天数、完成目标）
- 积极的反馈和鼓励

**家长友好（Parent Friendly）**
- 家长角色需要快速了解孩子学习情况
- 清晰的统计报告
- 重要信息突出显示

## 2. 视觉设计

### 2.1 色彩系统

#### 主色调（Primary Colors）
```css
/* 学习蓝 - 专注、专业 */
--primary-50: #eff6ff;
--primary-100: #dbeafe;
--primary-200: #bfdbfe;
--primary-300: #93c5fd;
--primary-400: #60a5fa;
--primary-500: #3b82f6;  /* 主色 */
--primary-600: #2563eb;
--primary-700: #1d4ed8;
--primary-800: #1e40af;
--primary-900: #1e3a8a;
```

#### 科目色彩（Subject Colors）
```css
/* Reading - 温暖的橙色（阅读、温馨）*/
--reading: #f97316;
--reading-light: #fed7aa;
--reading-dark: #c2410c;

/* Writing - 创意紫色（写作、创造）*/
--writing: #a855f7;
--writing-light: #e9d5ff;
--writing-dark: #7e22ce;

/* Maths - 逻辑绿色（数学、精确）*/
--maths: #10b981;
--maths-light: #a7f3d0;
--maths-dark: #047857;

/* Thinking Skills - 智慧靛蓝（思维、深度）*/
--thinking: #6366f1;
--thinking-light: #c7d2fe;
--thinking-dark: #4338ca;
```

#### 语义色彩（Semantic Colors）
```css
/* 成功 */
--success: #10b981;
--success-light: #d1fae5;

/* 警告 */
--warning: #f59e0b;
--warning-light: #fef3c7;

/* 错误 */
--error: #ef4444;
--error-light: #fee2e2;

/* 信息 */
--info: #3b82f6;
--info-light: #dbeafe;
```

#### 中性色（Neutral Colors）
```css
--gray-50: #f9fafb;
--gray-100: #f3f4f6;
--gray-200: #e5e7eb;
--gray-300: #d1d5db;
--gray-400: #9ca3af;
--gray-500: #6b7280;
--gray-600: #4b5563;
--gray-700: #374151;
--gray-800: #1f2937;
--gray-900: #111827;
```

### 2.2 排版系统

#### 字体家族
```css
/* 主要字体 - 现代、清晰 */
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* 数字字体 - 统计数据 */
--font-mono: 'JetBrains Mono', 'Monaco', 'Courier New', monospace;

/* 标题字体（可选）*/
--font-heading: 'Poppins', 'Inter', sans-serif;
```

#### 字体大小
```css
--text-xs: 0.75rem;    /* 12px - 辅助信息 */
--text-sm: 0.875rem;   /* 14px - 次要内容 */
--text-base: 1rem;     /* 16px - 正文 */
--text-lg: 1.125rem;   /* 18px - 强调内容 */
--text-xl: 1.25rem;    /* 20px - 小标题 */
--text-2xl: 1.5rem;    /* 24px - 卡片标题 */
--text-3xl: 1.875rem;  /* 30px - 页面标题 */
--text-4xl: 2.25rem;   /* 36px - 大标题 */
```

#### 字重
```css
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### 2.3 间距系统

```css
--spacing-1: 0.25rem;   /* 4px */
--spacing-2: 0.5rem;    /* 8px */
--spacing-3: 0.75rem;   /* 12px */
--spacing-4: 1rem;      /* 16px */
--spacing-5: 1.25rem;   /* 20px */
--spacing-6: 1.5rem;    /* 24px */
--spacing-8: 2rem;      /* 32px */
--spacing-10: 2.5rem;   /* 40px */
--spacing-12: 3rem;     /* 48px */
--spacing-16: 4rem;     /* 64px */
```

### 2.4 圆角与阴影

#### 圆角
```css
--radius-sm: 0.25rem;   /* 4px - 小元素 */
--radius-md: 0.5rem;    /* 8px - 按钮、输入框 */
--radius-lg: 0.75rem;   /* 12px - 卡片 */
--radius-xl: 1rem;      /* 16px - 大卡片 */
--radius-2xl: 1.5rem;   /* 24px - 模态框 */
--radius-full: 9999px;  /* 圆形 */
```

#### 阴影
```css
--shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
--shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
```

## 3. 组件设计规范

### 3.1 按钮（Button）

#### 主要按钮（Primary Button）
```vue
<!-- 用途：主要操作（上传题目、提交答案） -->
<n-button type="primary" size="large">
  上传题目
</n-button>

<!-- 或使用Tailwind自定义样式 -->
<button class="
  px-6 py-3 
  bg-primary-500 hover:bg-primary-600 
  text-white font-medium 
  rounded-lg 
  shadow-md hover:shadow-lg 
  transition-all duration-200
  active:scale-95
">
  上传题目
</button>
```

#### 次要按钮（Secondary Button）
```vue
<!-- 用途：次要操作（取消、返回） -->
<n-button type="default">
  取消
</n-button>

<!-- 或自定义 -->
<button class="
  px-6 py-3 
  bg-gray-100 hover:bg-gray-200 
  text-gray-700 font-medium 
  rounded-lg 
  transition-all duration-200
">
  取消
</button>
```

#### 图标按钮（Icon Button）
```vue
<!-- 用途：工具栏操作 -->
<n-button text>
  <template #icon>
    <n-icon><Edit /></n-icon>
  </template>
</n-button>
```

### 3.2 卡片（Card）

#### 题目卡片
```vue
<template>
  <n-card 
    hoverable 
    class="cursor-pointer"
    @click="handleClick"
  >
    <!-- 缩略图 -->
    <img 
      :src="question.thumbnail_url" 
      class="w-full h-48 object-cover rounded-t-lg"
    />
    
    <!-- 内容区 -->
    <template #header>
      <n-tag 
        :type="getSubjectType(question.subject)" 
        size="small"
      >
        {{ question.subject }}
      </n-tag>
    </template>
    
    <!-- 标题 -->
    <h3 class="text-lg font-semibold text-gray-900">
      {{ question.title || '题目 ' + question.id }}
    </h3>
    
    <!-- 元数据 -->
    <template #footer>
      <div class="flex items-center gap-4 text-sm text-gray-500">
        <span>⭐ 难度 {{ question.difficulty }}</span>
        <span>📅 {{ formatDate(question.created_at) }}</span>
      </div>
    </template>
  </n-card>
</template>
```

#### 统计卡片
#### 统计卡片
```vue
<template>
  <n-card
    class="bg-gradient-to-br from-primary-500 to-primary-600 text-white"
    :bordered="false"
  >
    <div class="flex items-center justify-between">
      <div>
        <p class="text-white/80 text-sm">已答题目</p>
        <p class="text-4xl font-bold mt-2">128</p>
      </div>
      <div class="p-4 bg-white/20 rounded-lg">
        <n-icon size="32">
          <Checkmark />
        </n-icon>
      </div>
    </div>
  </n-card>
</template>

<script setup>
import { Checkmark } from '@vicons/ionicons5'
</script>
```

### 3.3 输入框（Input）

```vue
<template>
  <div class="space-y-2">
    <label class="block text-sm font-medium text-gray-700">
      题目标题
    </label>
    <n-input
      v-model:value="title"
      placeholder="输入题目标题（可选）"
      size="large"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
const title = ref('')
</script>
```

### 3.4 标签（Badge/Tag）

```vue
<!-- 科目标签 -->
<n-tag type="warning" size="medium">
  <template #icon>
    <n-icon><Book /></n-icon>
  </template>
  Reading
</n-tag>

<!-- 状态标签 -->
<n-tag type="success" size="small">
  已掌握
</n-tag>

<!-- 难题标记 -->
<n-tag type="error" size="small">
  🔥 难题
</n-tag>
```
```

### 3.5 Progress Bar

```vue
<template>
  <div class="space-y-2">
    <div class="flex justify-between text-sm">
      <span class="text-gray-700">学习进度</span>
      <span class="text-primary-600 font-semibold">{{ progress }}%</span>
    </div>
    <n-progress
      type="line"
      :percentage="progress"
      :show-indicator="false"
      :height="12"
      border-radius="6px"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
const progress = ref(75)
</script>
```

## 4. 页面布局设计

### 4.1 移动端布局（主要）

```
┌─────────────────────┐
│  Header (固定)       │
│  Logo | 通知 | 头像  │
├─────────────────────┤
│                     │
│   Main Content      │
│                     │
│   (可滚动)          │
│                     │
│                     │
│                     │
│                     │
│                     │
├─────────────────────┤
│  Bottom Nav (固定)  │
│  📊 📚 ➕ 🔍 👤    │
└─────────────────────┘
```

#### Bottom Navigation Icons
- 📊 Dashboard（仪表板）
- 📚 My Questions（我的题目）
- ➕ Upload（上传 - 突出显示）
- 🔍 Search（搜索）
- 👤 Profile（个人）

### 4.2 桌面端布局

```
┌──────────────────────────────────┐
│  Header                          │
│  Logo | Search | Notification | Avatar │
├────────┬─────────────────────────┤
│        │                         │
│ Side   │   Main Content          │
│ bar    │                         │
│        │   (可滚动)              │
│ - Dashboard                     │
│ - Reading                       │
│ - Writing                       │
│ - Maths                         │
│ - Thinking                      │
│ - Profile                       │
│        │                         │
└────────┴─────────────────────────┘
```

## 5. 关键页面设计

### 5.1 Dashboard（仪表板）

#### 布局结构
```
1. 欢迎信息 + 快速统计（卡片网格）
   [总题目] [已答题目] [正确率] [连续天数]

2. 今日推荐复习（横向滚动卡片）
   [题目卡片1] [题目卡片2] [题目卡片3] →

3. 学习趋势图表
   [正确率趋势折线图]

4. 各科目进度
   Reading:    [进度条 75%]
   Writing:    [进度条 60%]
   Maths:      [进度条 85%]
   Thinking:   [进度条 70%]

5. 最近活动
   - 今天上传了3道题目
   - 昨天完成了5道题目
   - 导师给"代数问题1"添加了讲解
```

### 5.2 题目上传页面

#### 流程设计
```
Step 1: 拍照/选择图片
┌─────────────────────┐
│                     │
│   📷 拍照上传       │
│   或                │
│   📁 选择图片       │
│                     │
└─────────────────────┘

Step 2: 图片预览与编辑
┌─────────────────────┐
│  [图片预览]         │
│  [裁剪] [旋转]      │
└─────────────────────┘

Step 3: 填写信息
- 科目选择（必选）
- 标题（可选）
- 标签（可选）
- 难度（可选）

Step 4: 确认上传
[上传] [取消]
```

### 5.3 题目详情页

#### 布局
```
┌─────────────────────┐
│  [题目高清图片]     │
│  (支持缩放、手势)   │
├─────────────────────┤
│  Maths • 难度⭐⭐⭐⭐ │
│  上传于 2天前        │
│                     │
│  标签: #代数 #方程   │
│                     │
│  🔥 已标记为难题    │
├─────────────────────┤
│  📝 我的答题记录 (2) │
│  [查看答题历史]      │
├─────────────────────┤
│  💬 评论与讨论 (5)  │
│  [查看所有评论]      │
├─────────────────────┤
│  [开始答题] [分享]  │
└─────────────────────┘
```

### 5.4 科目板块页面

#### 每个科目页面结构
```
┌─────────────────────┐
│  📚 Reading          │
│  总计 45题           │
├─────────────────────┤
│  [筛选] [排序]      │
├─────────────────────┤
│  📊 学习概况        │
│  正确率: 78%         │
│  需复习: 12题        │
├─────────────────────┤
│  题目列表            │
│  [题目卡片1]        │
│  [题目卡片2]        │
│  [题目卡片3]        │
│  ...                │
└─────────────────────┘
```

## 6. 交互设计

### 6.1 微交互（Micro-interactions）

#### 按钮点击
```vue
<!-- 缩放效果 -->
<n-button class="active:scale-95 transition-transform">
  点击我
</n-button>

<!-- 背景变化 -->
<n-button
  type="primary"
  class="hover:bg-primary-600 transition-colors duration-200"
>
  上传
</n-button>
```

#### 加载状态
```vue
<template>
  <n-button :loading="isLoading" type="primary">
    上传
  </n-button>
</template>

<script setup>
import { ref } from 'vue'
const isLoading = ref(false)
</script>
```

#### 图片上传进度
```vue
<template>
  <div class="relative">
    <img :src="preview" :class="{ 'opacity-50': uploading }" />
    <div v-if="uploading" class="absolute inset-0 flex items-center justify-center">
      <n-progress
        type="circle"
        :percentage="uploadProgress"
        :stroke-width="8"
      />
    </div>
  </div>
</template>
```

### 6.2 动画效果

#### 页面过渡
```vue
<template>
  <Transition
    name="fade"
    mode="out-in"
  >
    <div :key="currentView">
      {{ content }}
    </div>
  </Transition>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-leave-to {
  opacity: 0;
}
</style>
```

#### 列表项淡入
```vue
<template>
  <TransitionGroup name="list" tag="div">
    <QuestionCard
      v-for="(question, index) in questions"
      :key="question.id"
      :question="question"
      :style="{ '--delay': index * 0.05 + 's' }"
    />
  </TransitionGroup>
</template>

<style scoped>
.list-enter-active {
  transition: all 0.3s ease;
  transition-delay: var(--delay);
}

.list-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}
</style>
```
```

### 6.3 手势支持（移动端）

- **下拉刷新**：在列表页面下拉刷新数据
- **左滑操作**：题目卡片左滑显示快捷操作（删除、分享）
- **双指缩放**：题目图片支持双指缩放
- **长按**：长按题目卡片显示更多选项

## 7. 响应式设计

### 7.1 断点（Breakpoints）

```css
/* 移动端 */
@media (max-width: 640px) { /* sm */ }

/* 平板 */
@media (min-width: 641px) and (max-width: 1024px) { /* md, lg */ }

/* 桌面 */
@media (min-width: 1025px) { /* xl, 2xl */ }
```

### 7.2 适配策略

#### 移动端（优先）
- 单列布局
- 更大的触摸区域（最小44x44px）
- 底部导航
- 全屏模态框

#### 平板
- 两列布局
- 侧边栏可收起
- 利用更多横向空间

#### 桌面
- 三列布局（侧边栏 + 主内容 + 右侧详情）
- 固定侧边栏
- 顶部导航
- 模态框居中显示

## 8. 无障碍设计（Accessibility）

### 8.1 基本要求

- **颜色对比度**：至少 4.5:1（WCAG AA标准）
- **键盘导航**：所有功能可通过键盘访问
- **屏幕阅读器**：正确的ARIA标签
- **焦点指示**：清晰的焦点状态

### 8.2 实现示例

```vue
<!-- 按钮无障碍 -->
<template>
  <n-button
    aria-label="上传题目"
    class="focus:ring-2 focus:ring-primary-500 focus:outline-none"
  >
    <template #icon>
      <n-icon><Upload /></n-icon>
    </template>
  </n-button>
</template>

<!-- 图片无障碍 -->
<template>
  <img 
    :src="questionImage" 
    alt="数学代数题目：解方程 2x + 5 = 15"
  />
</template>
```

## 9. 性能优化

### 9.1 图片优化

```vue
<!-- 使用原生img标签 + Cloudinary优化 -->
<template>
  <img
    :src="optimizedImageUrl"
    :alt="question.title"
    loading="lazy"
    class="w-full h-auto"
  />
</template>

<script setup>
// Cloudinary会自动优化图片
const optimizedImageUrl = computed(() => {
  // Cloudinary URL已包含优化参数（q_auto, f_auto等）
  return props.question.thumbnail_url
})
</script>
```

### 9.2 代码分割

```vue
<!-- 动态导入大型组件 -->
<script setup>
import { defineAsyncComponent } from 'vue'

const ChartComponent = defineAsyncComponent({
  loader: () => import('@/components/Chart.vue'),
  loadingComponent: LoadingSpinner,
  delay: 200
})
</script>
```

## 10. 设计系统实现

### 10.1 使用 Naive UI

Naive UI 提供了完整的Vue 3组件库：

```bash
npm install naive-ui
npm install @vicons/ionicons5
```

**在main.js中配置**：
```javascript
import { createApp } from 'vue'
import naive from 'naive-ui'
import App from './App.vue'

const app = createApp(App)
app.use(naive)
app.mount('#app')
```

### 10.2 自定义主题

```typescript
// tailwind.config.ts
export default {
  theme: {
    extend: {
      colors: {
        primary: {
          // 蓝色主题
          50: '#eff6ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        },
        reading: '#f97316',
        writing: '#a855f7',
        maths: '#10b981',
        thinking: '#6366f1',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
};
```

## 11. 图标系统

**推荐使用**: @vicons/ionicons5（Naive UI 官方推荐）

### 安装
```bash
npm install @vicons/ionicons5
```

### 使用示例
```vue
<template>
  <!-- 在Naive UI组件中使用 -->
  <n-button>
    <template #icon>
      <n-icon><Upload /></n-icon>
    </template>
    上传
  </n-button>

  <!-- 独立使用图标 -->
  <n-icon size="24" color="#3b82f6">
    <Checkmark />
  </n-icon>

  <!-- 图标列表 -->
  <div class="flex gap-2">
    <n-icon><Upload /></n-icon>
    <n-icon><Checkmark /></n-icon>
    <n-icon><Close /></n-icon>
    <n-icon><ChevronForward /></n-icon>
    <n-icon><Star /></n-icon>
  </div>
</template>

<script setup>
import {
  Upload,
  Checkmark,
  Close,
  ChevronForward,
  Star
} from '@vicons/ionicons5'
</script>
```

### 其他图标库选项

**@iconify/vue** - 包含所有图标集
```bash
npm install @iconify/vue
```

```vue
<template>
  <Icon icon="mdi:upload" :width="24" />
  <Icon icon="heroicons:check-20-solid" />
</template>

<script setup>
import { Icon } from '@iconify/vue'
</script>
```

**推荐**: 优先使用 `@vicons/ionicons5`，因为它与 Naive UI 完美集成。

## 12. 设计检查清单

开发每个页面时，检查以下项目：

- [ ] 移动端和桌面端都已测试
- [ ] 加载状态已实现
- [ ] 错误状态已处理
- [ ] 空状态设计（没有数据时）
- [ ] 颜色对比度符合标准
- [ ] 所有交互元素都有hover/active状态
- [ ] 表单验证反馈清晰
- [ ] 图片有alt文本
- [ ] 按钮有合适的aria-label
- [ ] 动画流畅（60fps）
- [ ] 触摸目标足够大（移动端）

---

## 参考资源

- **shadcn/ui**: https://ui.shadcn.com
- **Tailwind CSS**: https://tailwindcss.com
- **Lucide Icons**: https://lucide.dev
- **Radix UI**: https://www.radix-ui.com
- **Material Design**: https://m3.material.io
- **Apple Human Interface Guidelines**: https://developer.apple.com/design
