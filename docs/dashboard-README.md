# 个人认知仪表盘 - 文档索引

## 📚 文档概览

本目录包含 InsightReader 个人认知仪表盘功能的完整文档,涵盖从设计到实施的全过程。

## 📖 文档列表

### 1. 用户文档

#### [用户指南 (User Guide)](./dashboard-user-guide.md)
**适用对象**: 所有用户
**内容摘要**:
- 功能概述和核心价值
- 知识图谱、好奇心指纹、思维盲区详细说明
- 设计理念和视觉风格
- 快速开始和最佳实践
- 常见问题解答
- 技术原理简介

**推荐阅读顺序**: 第一份文档,了解功能用途

---

### 2. 开发文档

#### [技术设计文档 (Technical Design)](./personal-cognitive-dashboard.md)
**适用对象**: 技术负责人、架构师
**内容摘要**:
- 项目背景和需求分析
- 系统架构和技术选型
- 核心模块设计
- 数据库 ER 图和表结构
- API 接口设计
- 前端组件架构
- 实施路线图
- 风险评估和应对策略

**推荐阅读顺序**: 设计阶段必读,实施前参考

---

#### [实施总结 (Implementation Summary)](./dashboard-implementation-summary.md)
**适用对象**: 开发者、技术审查人员
**内容摘要**:
- 完整的实施过程记录
- 后端服务层详解 (analytics_service, knowledge_graph_service)
- 前端组件实现细节 (D3.js 集成、Vue Composition API)
- 数据库模型和关系
- 核心算法实现 (共现分析、DFS 孤岛检测、领域识别)
- 性能优化策略
- 测试建议
- 部署注意事项
- 未来增强方向

**推荐阅读顺序**: 实施完成后阅读,代码审查时参考

---

#### [API 参考 (API Reference)](./dashboard-api-reference.md)
**适用对象**: 前端开发者、API 集成人员
**内容摘要**:
- 完整的 API 端点说明
- 请求/响应格式和示例
- 参数类型和数据结构
- 错误码和错误处理
- 前端使用示例 (useDashboard composable)
- 性能建议和数据更新时机

**API 端点列表**:
- `GET /api/v1/dashboard/` - 获取仪表盘总览
- `GET /api/v1/dashboard/knowledge-graph` - 获取知识图谱
- `GET /api/v1/dashboard/curiosity-fingerprint` - 获取好奇心指纹
- `GET /api/v1/dashboard/blind-spots` - 获取思维盲区
- `POST /api/v1/dashboard/rebuild` - 重建知识图谱
- `POST /api/v1/analytics/spark-click` - 记录火花点击

**推荐阅读顺序**: 前端开发时随时查阅

---

#### [实施清单 (Implementation Checklist)](./dashboard-checklist.md)
**适用对象**: 项目经理、QA 测试人员、开发者
**内容摘要**:
- 后端实现完成度检查
- 前端实现完成度检查
- 测试清单 (API、功能、用户体验)
- 部署前检查清单
- 下一步工作建议
- 已知限制和常见问题排查

**推荐阅读顺序**: 实施过程中持续对照,测试和部署前必读

---

## 🗂️ 文档关系图

```
用户视角                       开发视角
   ↓                              ↓
用户指南  ←───────────→  技术设计文档
   ↓                              ↓
(使用功能)                    实施总结
                                  ↓
                           API 参考 + 实施清单
                                  ↓
                            (编码、测试、部署)
```

## 📋 快速导航

### 按角色导航

**产品经理 / 项目负责人**
1. [用户指南](./dashboard-user-guide.md) - 了解功能价值
2. [技术设计文档](./personal-cognitive-dashboard.md) - 理解技术架构
3. [实施清单](./dashboard-checklist.md) - 跟踪开发进度

**后端开发者**
1. [技术设计文档](./personal-cognitive-dashboard.md) - 数据库和 API 设计
2. [实施总结](./dashboard-implementation-summary.md) - 服务层实现细节
3. [API 参考](./dashboard-api-reference.md) - 接口规范
4. [实施清单](./dashboard-checklist.md) - 对照完成度

**前端开发者**
1. [API 参考](./dashboard-api-reference.md) - 接口调用
2. [实施总结](./dashboard-implementation-summary.md) - 组件实现和 D3.js 集成
3. [用户指南](./dashboard-user-guide.md) - 理解功能逻辑
4. [实施清单](./dashboard-checklist.md) - 功能测试

**QA 测试人员**
1. [用户指南](./dashboard-user-guide.md) - 了解功能和预期行为
2. [实施清单](./dashboard-checklist.md) - 测试用例参考
3. [API 参考](./dashboard-api-reference.md) - API 测试

**运维 / DevOps**
1. [实施总结](./dashboard-implementation-summary.md) - 部署注意事项
2. [实施清单](./dashboard-checklist.md) - 部署前检查
3. [API 参考](./dashboard-api-reference.md) - 监控端点

---

## 🔍 按任务导航

### 了解功能价值
→ [用户指南](./dashboard-user-guide.md)

### 设计阶段
→ [技术设计文档](./personal-cognitive-dashboard.md)

### 开发阶段
- 后端: [技术设计文档](./personal-cognitive-dashboard.md) + [实施总结](./dashboard-implementation-summary.md)
- 前端: [API 参考](./dashboard-api-reference.md) + [实施总结](./dashboard-implementation-summary.md)

### 测试阶段
→ [实施清单](./dashboard-checklist.md) + [API 参考](./dashboard-api-reference.md)

### 部署阶段
→ [实施总结 - 部署章节](./dashboard-implementation-summary.md#-部署注意事项) + [实施清单](./dashboard-checklist.md)

### 维护阶段
→ [API 参考](./dashboard-api-reference.md) + [实施清单 - 问题排查](./dashboard-checklist.md#-常见问题排查)

### 功能增强
→ [实施总结 - 未来方向](./dashboard-implementation-summary.md#-未来增强方向)

---

## 📊 文档统计

| 文档 | 字数 | 主要内容 | 更新频率 |
|------|------|----------|----------|
| 用户指南 | ~6000 | 功能说明、使用指南 | 功能变更时 |
| 技术设计文档 | ~12000 | 架构设计、需求分析 | 设计阶段 |
| 实施总结 | ~9000 | 实现细节、算法说明 | 实施完成后 |
| API 参考 | ~7000 | 接口规范、示例 | API 变更时 |
| 实施清单 | ~5000 | 检查清单、测试用例 | 实施过程中 |

---

## 🔄 文档维护

### 版本控制
所有文档遵循语义化版本号 (Semantic Versioning):
- **主版本号**: 重大功能变更或架构调整
- **次版本号**: 新增功能或重要改进
- **修订号**: 文档修正或小幅更新

**当前版本**: 1.0.0 (首次发布)

### 更新原则
1. **同步更新**: 代码变更后立即更新相关文档
2. **向后兼容**: 新版文档需说明与旧版的差异
3. **变更日志**: 重要更新需在文档末尾记录

### 维护责任
- **技术负责人**: 审核所有文档变更
- **开发者**: 更新实施总结和 API 参考
- **产品经理**: 更新用户指南
- **QA**: 更新测试清单

---

## 🛠️ 使用建议

### 新成员入职
**Day 1**: 阅读[用户指南](./dashboard-user-guide.md),理解产品价值
**Day 2**: 阅读[技术设计文档](./personal-cognitive-dashboard.md),理解架构
**Day 3**: 阅读[实施总结](./dashboard-implementation-summary.md),熟悉代码

### 开发新功能
**步骤 1**: 更新[技术设计文档](./personal-cognitive-dashboard.md),记录设计决策
**步骤 2**: 编写代码,参考[实施总结](./dashboard-implementation-summary.md)的实现模式
**步骤 3**: 更新[API 参考](./dashboard-api-reference.md),记录新接口
**步骤 4**: 更新[实施清单](./dashboard-checklist.md),添加测试用例
**步骤 5**: 更新[用户指南](./dashboard-user-guide.md),说明新功能

### 排查问题
**步骤 1**: 查阅[实施清单 - 问题排查](./dashboard-checklist.md#-常见问题排查)
**步骤 2**: 检查[API 参考](./dashboard-api-reference.md)的错误响应
**步骤 3**: 阅读[实施总结](./dashboard-implementation-summary.md)的相关算法

### 性能优化
→ [实施总结 - 性能优化](./dashboard-implementation-summary.md#-性能优化)
→ [API 参考 - 性能建议](./dashboard-api-reference.md#-性能建议)

---

## 📞 联系方式

**文档问题反馈**: docs@insightreader.com
**技术支持**: support@insightreader.com
**GitHub Issues**: https://github.com/insightreader/issues

---

## 📜 许可证

本文档集遵循 MIT License,与 InsightReader 项目保持一致。

---

**索引版本**: 1.0.0
**最后更新**: 2025-10-20
**维护者**: InsightReader Documentation Team
