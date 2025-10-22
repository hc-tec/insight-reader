# InsightReader 技术文档中心

## 📚 文档目录

### 核心架构文档

#### 🔄 [异步化架构设计](./ASYNC_ARCHITECTURE.md)
**详细程度**: ⭐⭐⭐⭐⭐

全面记录从同步阻塞架构到异步非阻塞架构的改造过程，包括：
- TaskManager 核心设计与实现
- SSEManager 实时通知系统
- AsyncOpenAI 集成方案
- 前端 SSE 监听与回调机制
- 最佳实践与注意事项
- 性能对比数据

**适用场景**：
- 理解项目异步化架构
- 开发新的异步任务
- 排查异步相关问题
- 性能优化参考

---

### 改造总结文档

#### 📊 [异步系统完整总结](../ASYNC_SYSTEM_COMPLETE_SUMMARY.md)
改造概览、问题总结、技术架构图

#### 🔐 [JWT 认证改造总结](../backend/JWT_AUTHENTICATION.md)
（待创建）JWT 全面改造方案

#### 🌐 [前端异步集成总结](../FRONTEND_ASYNC_INTEGRATION_SUMMARY.md)
前端适配异步 API 的完整流程

#### 📝 [前端迁移指南](../FRONTEND_MIGRATION_GUIDE.md)
从同步 API 迁移到异步 API 的步骤

---

### 问题修复文档

#### 🐛 [紧急 Bug 修复记录](../URGENT_BUG_FIXES.md)
重大 bug 修复历史

#### 💾 [数据库修复总结](../backend/DATABASE_FIX_SUMMARY.md)
数据库问题排查与修复

#### 📋 [日志系统完整迁移](../backend/LOGGING_COMPLETE_MIGRATION.md)
从 print 到 logging 的迁移

#### 🚀 [Vercel 部署修复](../backend/VERCEL_DEPLOYMENT_FIX.md)
Vercel 部署问题解决方案

---

## 🔧 快速导航

### 我想要...

**理解项目架构**
→ 阅读 [异步化架构设计](./ASYNC_ARCHITECTURE.md)

**开发新功能**
→ 查看 [最佳实践](./ASYNC_ARCHITECTURE.md#-最佳实践)

**排查问题**
→ 参考 [注意事项](./ASYNC_ARCHITECTURE.md#-注意事项) + [紧急 Bug 修复记录](../URGENT_BUG_FIXES.md)

**优化性能**
→ 查看 [性能对比](./ASYNC_ARCHITECTURE.md#-性能对比)

**迁移旧代码**
→ 遵循 [迁移指南](./ASYNC_ARCHITECTURE.md#-迁移指南)

---

## 📐 架构关键概念

### 异步任务流程

```
用户请求 → FastAPI 端点 → TaskManager.submit_task() → 返回 task_id
                                    ↓
                            独立线程执行任务
                                    ↓
                            SSEManager 推送结果
                                    ↓
                            前端 SSE 回调处理
```

### 核心组件

| 组件 | 职责 | 位置 |
|-----|------|-----|
| TaskManager | 任务提交、执行、回调 | `backend/app/core/task_manager.py` |
| SSEManager | SSE 连接管理、事件分发 | `backend/app/core/task_manager.py` |
| AsyncOpenAI | 异步 LLM API 调用 | `backend/app/services/ai_service.py` |
| useAnalysisNotifications | SSE 监听、回调注册 | `frontend/app/composables/useAnalysisNotifications.ts` |

---

## 🎯 技术栈

### 后端
- **Framework**: FastAPI
- **异步**: asyncio, threading
- **LLM**: AsyncOpenAI
- **Database**: PostgreSQL + SQLAlchemy
- **Auth**: JWT (OAuth2 Bearer)

### 前端
- **Framework**: Nuxt 3 (Vue 3)
- **实时通信**: Server-Sent Events (SSE)
- **HTTP Client**: $fetch (ofetch)
- **状态管理**: useState (Nuxt)

---

## 📊 性能指标

| 指标 | 改造前 | 改造后 | 提升 |
|-----|-------|-------|-----|
| HTTP 响应时间 | 30-60s | <100ms | **600倍** |
| 最大并发 | 5 | 100+ | **20倍** |
| 超时率 | 15% | <1% | **降低 15 倍** |
| 资源利用率 | 30% | 85% | **2.8倍** |

---

## 🤝 贡献指南

### 添加新文档

1. 在 `docs/` 目录创建 Markdown 文件
2. 在本 README 中添加链接
3. 使用统一的文档模板（见下方）

### 文档模板

```markdown
# 文档标题

## 📋 文档概述
**版本**: 1.0
**日期**: YYYY-MM-DD
**作者**: Your Name
**状态**: 草稿/审核中/已完成

## 🎯 背景

## 🏗️ 设计方案

## 💻 实现细节

## 📊 测试结果

## ⚠️ 注意事项

## 📚 相关文档
```

---

## 📝 更新日志

### 2025-10-22
- ✅ 创建异步化架构设计文档
- ✅ 完成 JWT 认证全面改造
- ✅ 建立文档中心索引

### 2025-XX-XX（之前）
- 完成异步系统重构
- 完成前端异步适配
- 修复数据库问题
- 完成日志系统迁移

---

## 🔗 外部资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Nuxt 3 官方文档](https://nuxt.com/)
- [Server-Sent Events 规范](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [OpenAI Python SDK](https://github.com/openai/openai-python)

---

**维护者**: Development Team
**最后更新**: 2025-10-22
