# InsightReader 前端

基于 Nuxt 4 + Vue 3 + Shadcn-vue 构建的现代化阅读辅助工具前端。

## 特性

- ✅ **极简设计**: 专注核心功能，无干扰阅读体验
- ✅ **划词交互**: 直观的文本选中和意图按钮
- ✅ **流式响应**: 实时展示 AI 生成的洞察内容
- ✅ **TypeScript**: 完整的类型支持

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，设置后端 API 地址
```

### 3. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

### 4. 构建生产版本

```bash
npm run build
npm run preview
```

## 核心 Composables

- `useArticle()` - 文章状态管理
- `useSelection()` - 划词选中逻辑
- `useInsightGenerator()` - 洞察生成
- `useSSE()` - SSE 流式响应

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `NUXT_PUBLIC_API_BASE` | 后端 API 地址 | http://localhost:8000 |

## 文档

更多信息请查看 [设计文档](../2.4-前端架构设计.md)
