<<<<<<< HEAD
# CottonAgent
=======
# 棉智策 CottonPilot

面向棉花种植场景的农事推荐智能体平台 V1。项目包含 Vue3 前端、FastAPI 后端、SQLite 持久化、SSE 实时任务状态和无大模型 Key 的模板降级能力。

## 功能截图

当前仓库不包含截图文件，可运行后截取登录页、Dashboard、棉田详情和 Agent 工作台作为简历展示素材。

## 技术栈

前端：Vue 3、JavaScript、Vite、Vue Router、Pinia、Element Plus、SCSS、Axios、ECharts、fetch-event-source、Vitest、ESLint。

后端：Python 3.11+、FastAPI、Uvicorn、SQLAlchemy 2.x、SQLite、Pydantic 2.x、PyJWT、httpx、pytest。V1 使用独立 WorkflowService 保留 LangGraph 风格的节点、状态和执行语义，以避免不同 LangGraph API 版本带来的演示不稳定。

## 项目结构

- `frontend/`：Vue 前端工程
- `backend/`：FastAPI 后端工程
- `backend/app/data/`：本地棉花知识库与农事序列数据
- `docs/api.md`：接口说明

## Windows PowerShell 启动

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python run.py
```

如果使用已有环境 `D:\conda\.conda\CottonAgent`：

```powershell
cd backend
D:\conda\.conda\CottonAgent\python.exe -m pip install -r requirements.txt
D:\conda\.conda\CottonAgent\python.exe run.py
```

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

## macOS/Linux 启动

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

测试账号：`admin / 123456`

Swagger 地址：`http://localhost:8000/docs`

无 `LLM_API_KEY` 时，后端会自动使用模板生成最终说明，不影响完整演示。

## 测试与构建

```bash
cd backend && pytest
cd frontend && npm run lint && npm run test && npm run build
```

## V1 已实现

登录鉴权、棉田 CRUD、农事记录、Dashboard 统计、Agent 任务、8 步工作流、SSE snapshot/实时事件、Top-3 推荐、7 天计划、推荐依据、历史任务、接受/拒绝方案。

## 当前迭代增强

- Agent 工作台增加表单校验、执行进度、当前运行步骤和 SSE 连接状态提示。
- SSE 断线后自动重试，并在任务完成或失败后主动关闭连接。
- Agent 步骤输出增加中文摘要，步骤详情保留输入/输出 JSON。
- Agent 每个节点现在都会记录工具调用，包括工具名、输入、观测结果和调用时间。
- Agent 工作台新增工具轨迹区，可实时查看咨询校验、档案读取、历史记录读取、知识检索、多因子推荐、计划生成、最终说明和结果持久化过程。
- 任务详情快照包含 `agentTrace` 和 `safetyConstraints`，页面刷新后仍可恢复完整执行轨迹。
- 推荐结果增加得分拆解：历史序列、生育阶段、知识匹配和最终分。
- 推荐结果增加结构化推荐理由，任务详情刷新后可恢复。
- 结果区增加风险判定依据，继续保留人工确认免责声明。

## 推荐器 V1.1

当前推荐器已升级为可解释多因子评分器，候选操作来自历史转移、知识库、当前阶段高频、天气规则和症状规则。Top-3 主推荐会排除固定复盘类操作 `UPDATE_RECORD`，该操作只会追加到 7 天计划。

评分因子：

- 历史转移 `transitionScore`
- 知识匹配 `knowledgeScore`
- 阶段适配 `growthStageScore`
- 天气影响 `weatherSuitabilityScore`
- 症状紧急度 `symptomUrgencyScore`
- 近期重复惩罚 `recencyPenaltyScore`

前端推荐卡片会展示候选来源、得分拆解和结构化推荐理由。推荐结果仍只覆盖监测、采样、记录、巡查、复查和评估类操作，不输出具体农药名称、剂量或自动执行建议。

## 后续方向

后续可扩展图片识别、向量数据库、Redis 消息队列、LangGraph 原生持久化、多 Agent 协作和更细粒度的权限系统。这些能力未在 V1 中实现。
>>>>>>> 7072fe8 (first commit)
