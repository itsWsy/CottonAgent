# CottonPilot API

统一响应：

```json
{ "code": 0, "message": "success", "data": {} }
```

错误返回使用 HTTP 状态码，`message` 或 `detail` 描述错误。

## Auth

- `POST /api/auth/login`：用户名密码登录，返回 `token` 和 `userInfo`。
- `GET /api/auth/profile`：获取当前用户信息。

## 棉田 CRUD

- `GET /api/fields?name=&growthStage=`
- `POST /api/fields`
- `GET /api/fields/{field_id}`
- `PUT /api/fields/{field_id}`
- `DELETE /api/fields/{field_id}`

## 农事记录

- `GET /api/fields/{field_id}/records`
- `POST /api/fields/{field_id}/records`
- `DELETE /api/records/{record_id}`

## Agent

- `POST /api/agent/tasks`：创建任务，立即返回 `{ taskId, status }`。
- `GET /api/agent/tasks`：历史任务列表。
- `GET /api/agent/tasks/{task_id}`：任务详情。
- `GET /api/agent/tasks/{task_id}/events`：SSE 事件流，需携带 `Authorization: Bearer <token>`。
- `POST /api/agent/tasks/{task_id}/accept`
- `POST /api/agent/tasks/{task_id}/reject`

SSE 事件类型：

- `task_snapshot`
- `step_start`
- `step_success`
- `step_failed`
- `recommendations`
- `farm_plan`
- `evidences`
- `answer`
- `completed`
- `failed`
- `heartbeat`

事件格式：

```json
{
  "type": "step_start",
  "taskId": "uuid",
  "timestamp": 1782180000000,
  "data": { "stepId": "load_field_context", "stepName": "读取棉田档案" }
}
```

## Dashboard

- `GET /api/dashboard/summary`
- `GET /api/dashboard/task-trend`
- `GET /api/dashboard/action-distribution`
- `GET /api/dashboard/recent-tasks`
