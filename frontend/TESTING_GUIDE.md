# UI Automation Testing Guide (Playwright)

本文档基于项目实战排查经验总结，旨在帮助开发者编写更稳定、易维护的 Playwright UI 测试。

## 1. 选择器策略 (Selectors)

### ✅ 推荐：使用 `data-testid`
这是最稳健的方式。UI 组件的样式（class）和文本内容（text）可能会频繁变化，但 `data-testid` 是专门为测试保留的。

**Vue 组件示例:**
```html
<!-- 推荐 -->
<div data-testid="question-card" @click="...">
  <h3 data-testid="question-title">{{ title }}</h3>
</div>
```

**测试脚本示例:**
```javascript
// 推荐
await page.locator('[data-testid="question-card"]').click()
await expect(page.locator('[data-testid="question-title"]')).toHaveText('Expected Title')
```

### ❌ 避免：依赖通用 Class 或 模糊文本
*   **避免** `.card`：可能匹配到布局容器、过滤器容器等非目标元素。
*   **避免** `text=Maths`：如果页面上有多个 "Maths"（如标签、标题、正文），会导致 `strict mode violation` 或点击错误元素。

---

## 2. 认证与全局状态 (Authentication)

### 全局登录 (Global Setup)
本项目在 `playwright.config.js` 中配置了 `storageState`，默认所有测试都会复用登录状态。

### 测试注册/登录流程
**关键点**：测试注册或登录页面时，必须**禁用**全局登录状态，否则会直接跳转到 Dashboard。

**如何禁用:**
在测试文件开头添加 `test.use` 配置：
```javascript
test.describe('Authentication Flow', () => {
    // 强制清除 storageState，确保以未登录状态开始
    test.use({ storageState: { cookies: [], origins: [] } })

    test('should register...', async ({ page }) => {
        await page.goto('/login') // 现在可以看到登录页了
    })
})
```

---

## 3. 导航与数据验证 (Navigation & Data)

### ✅ 推荐：UI 驱动测试 (UI-Driven)
模拟真实用户路径：**列表页 -> 点击 -> 详情页**。
*   **优点**：无需关心具体的 URL ID，无需手动同步 API 数据。
*   **做法**：在列表页抓取预期数据（如标题），点击进入详情页，验证显示的数据是否与刚才抓取的一致。

```javascript
// 1. 在列表页获取预期值
const expectedTitle = await card.locator('[data-testid="card-title"]').innerText()

// 2. 点击跳转
await card.click()

// 3. 在详情页验证
await expect(page.locator('[data-testid="question-title"]')).toHaveText(expectedTitle)
```

### ⚠️ 慎用：API 驱动跳转
直接访问 `/questions/123`。
*   **风险**：如果 ID 为 123 的数据被删除或未加载，测试会直接失败。需要配合 API Mock 或严格的数据 Setup/Teardown 使用。

---

## 4. Naive UI 组件交互

Naive UI 等组件库通常会封装原生 HTML 元素，导致选择器层级变深。

*   **输入框 (Input)**：通常可以直接用 placeholder 定位。
    ```javascript
    await page.fill('input[placeholder="Username"]', 'testuser')
    ```
*   **下拉框 (Select)**：
    *   点击触发器：`page.click('.n-base-selection')` (最好加 data-testid)
    *   选择选项：`page.click('.n-base-select-option:has-text("Option Name")')`
    *   **注意**：下拉选项通常渲染在 `body` 根节点的 `div` 中，而不是原本的 DOM 树位置。

---

## 5. 调试技巧 (Debugging)

### 开启浏览器日志
测试失败时，浏览器的 Console Log 往往能直接通过报错信息（如 API 400/500）揭示原因。

```javascript
test.beforeEach(async ({ page }) => {
    page.on('console', msg => console.log(`BROWSER: ${msg.text()}`))
})
```

### 可视化调试
*   **Headed Mode**: `npx playwright test --headed` (肉眼观察)
*   **UI Mode**: `npx playwright test --ui` (时间轴回溯，查看每一步的 DOM 快照)
*   **Trace Viewer**: 配置 `trace: 'retain-on-failure'`，失败后查看 trace.zip。

## 6. 等待机制 (Waiting)

*   **隐式等待**：Playwright 的 `click`, `fill` 等操作会自动等待元素 Visible + Actionable。
*   **显式等待**：
    *   等待 URL 变化：`await page.waitForURL(/\/dashboard/)`
    *   等待特定请求：`await page.waitForResponse(...)`
    *   **避免**：`await page.waitForTimeout(5000)` (除非调试，否则尽量不要硬等待)
