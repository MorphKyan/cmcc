# API 接入文档

本文档描述了如何接入数据服务 API，包括设备、区域、媒体、门数据的批量上传、查询和清空，用户位置的更新，以及 RAG 服务的管理与查询。

## 基础信息

- **基础 URL**: 
  - 数据管理: `/data`
  - RAG 服务: `/rag`
- **数据格式**: JSON

---

## 1. 设备管理 (Devices)

### 1.1 批量上传设备
上传一批设备数据到系统中。

- **接口**: `POST /data/devices/batch`
- **Content-Type**: `application/json`

**请求参数 (JSON Body)**:
接受一个设备对象列表。

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `name` | string | 是 | 设备名称 |
| `type` | string | 是 | 设备类型 |
| `area` | string | 是 | 所属区域名称 |
| `aliases` | string | 否 | 设备别名 |
| `description` | string | 否 | 设备描述 |

**请求示例**:
```json
[
  {
    "name": "Camera-01",
    "type": "camera",
    "area": "Lobby",
    "aliases": "大堂摄像头",
    "description": "位于大堂入口处"
  },
  {
    "name": "Sensor-01",
    "type": "sensor",
    "area": "ServerRoom"
  }
]
```

**响应示例**:
```json
{
  "status": "success",
  "message": "设备数据批量上传成功"
}
```

### 1.2 获取所有设备
获取当前系统中的所有设备数据。

- **接口**: `GET /data/devices`

**响应示例**:
```json
[
  {
    "name": "Camera-01",
    "type": "camera",
    "area": "Lobby",
    "aliases": "大堂摄像头",
    "description": "位于大堂入口处"
  }
]
```

### 1.3 清空设备数据
清空系统中所有的设备数据。

- **接口**: `DELETE /data/devices`

**响应示例**:
```json
{
  "status": "success",
  "message": "设备数据已清空"
}
```

---

## 2. 区域管理 (Areas)

### 2.1 批量上传区域
上传一批区域数据。

- **接口**: `POST /data/areas/batch`
- **Content-Type**: `application/json`

**请求参数 (JSON Body)**:
接受一个区域对象列表。

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `name` | string | 是 | 区域名称 |
| `aliases` | string | 否 | 区域别名 |
| `description` | string | 否 | 区域描述 |

**请求示例**:
```json
[
  {
    "name": "Lobby",
    "aliases": "一楼大堂",
    "description": "主入口区域"
  }
]
```

**响应示例**:
```json
{
  "status": "success",
  "message": "区域数据批量上传成功"
}
```

### 2.2 获取所有区域
- **接口**: `GET /data/areas`

**响应示例**:
```json
[
  {
    "name": "Lobby",
    "aliases": "一楼大堂",
    "description": "主入口区域"
  }
]
```

### 2.3 清空区域数据
- **接口**: `DELETE /data/areas`

**响应示例**:
```json
{
  "status": "success",
  "message": "区域数据已清空"
}
```

---

## 3. 媒体资源管理 (Media)

### 3.1 批量上传媒体数据
上传一批媒体资源数据（如视频、音频等）。

- **接口**: `POST /data/media/batch`
- **Content-Type**: `application/json`

**请求参数 (JSON Body)**:
接受一个媒体对象列表。

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `name` | string | 是 | 媒体名称 |
| `type` | string | 是 | 媒体类型 (如 video, audio 等) |
| `aliases` | string | 否 | 媒体别名 |
| `description` | string | 否 | 媒体描述 |

**请求示例**:
```json
[
  {
    "name": "intro_video_01",
    "type": "video",
    "aliases": "公司介绍视频",
    "description": "公司简介宣传片"
  },
  {
    "name": "safety_guide",
    "type": "video",
    "aliases": "安全指南",
    "description": "员工安全培训视频"
  }
]
```

**响应示例**:
```json
{
  "status": "success",
  "message": "媒体数据批量上传成功"
}
```

### 3.2 获取所有媒体数据
- **接口**: `GET /data/media`

**响应示例**:
```json
[
  {
    "name": "intro_video_01",
    "type": "video",
    "aliases": "公司介绍视频",
    "description": "公司简介宣传片"
  }
]
```

### 3.3 清空媒体数据
- **接口**: `DELETE /data/media`

**响应示例**:
```json
{
  "status": "success",
  "message": "媒体数据已清空"
}
```

---

## 4. 门禁资源管理 (Doors)

### 4.1 批量上传门数据
- **接口**: `POST /data/doors/batch`
- **Content-Type**: `application/json`

**请求参数 (JSON Body)**:

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `name` | string | 是 | 门名称 |
| `type` | string | 是 | 类型 (passage 或 standalone) |
| `area1` | string | 是 | 连接区域1 |
| `area2` | string | 是 | 连接区域2 |
| `location` | string | 是 | 具体位置描述 |

**请求示例**:
```json
[
  {
    "name": "Door_101",
    "type": "passage",
    "area1": "Lobby",
    "area2": "Corridor",
    "location": "大堂东侧"
  }
]
```

**响应示例**:
```json
{
  "status": "success",
  "message": "门数据批量上传成功"
}
```

### 4.2 获取所有门数据
- **接口**: `GET /data/doors`

**响应示例**:
```json
[
  {
    "name": "Door_101",
    "type": "passage",
    "area1": "Lobby",
    "area2": "Corridor",
    "location": "大堂东侧"
  }
]
```

### 4.3 清空门数据
- **接口**: `DELETE /data/doors`

**响应示例**:
```json
{
  "status": "success",
  "message": "门数据已清空"
}
```

---

## 5. 用户位置 (Location)

### 5.1 更新用户位置
更新指定客户端的当前位置信息。这通常用于上下文感知的 RAG 功能。

> [!NOTE]
> 需要客户端先建立 WebSocket 连接后才能更新位置，否则会返回 404 错误。

- **接口**: `POST /data/location`
- **Content-Type**: `application/json`

**请求参数 (JSON Body)**:

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `client_id` | string | 是 | 客户端唯一标识 |
| `location` | string | 是 | 当前位置描述 (如 "Lobby") |

**请求示例**:
```json
{
  "client_id": "user_12345",
  "location": "ServerRoom"
}
```

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "client_id": "user_12345",
    "location": "ServerRoom"
  },
  "message": "用户位置已更新为: ServerRoom"
}
```

**错误响应** (客户端未连接):
```json
{
  "detail": "未找到客户端连接: user_12345"
}
```

---

## 6. RAG 管理 (RAG)

### 6.1 获取 RAG 状态
获取 RAG 处理器的当前状态。

- **接口**: `GET /rag/status`

**状态说明**:

| 状态 | 说明 |
| :--- | :--- |
| `UNINITIALIZED` | 服务刚启动，尚未开始初始化 |
| `INITIALIZING` | 正在初始化中 |
| `READY` | 服务正常，可以接受请求 |
| `ERROR` | 初始化失败，附带错误信息 |

**响应示例** (正常):
```json
{
  "status": "success",
  "data": {
    "initialized": true,
    "database_exists": true,
    "database_path": "/path/to/chroma_db"
  }
}
```

**响应示例** (错误):
```json
{
  "detail": {
    "status": "error",
    "message": "连接 Ollama 服务失败"
  }
}
```

### 6.2 刷新 RAG 数据库
刷新 RAG 数据库端点。主要用于在更新了底层数据文件后，手动触发 RAG 向量数据库的刷新。

- **接口**: `POST /rag/refresh`
- **Content-Type**: `application/json`

**响应示例**:
```json
{
  "status": "success",
  "message": "刷新RAG数据库成功"
}
```

### 6.3 重新初始化 RAG
异步触发 RAG 处理器的重新初始化。适用于解决外部依赖（如 Ollama 服务或数据文件）问题后需要重新启动 RAG 服务的场景。

- **接口**: `POST /rag/reinitialize`
- **状态码**: `202 Accepted` (任务已接受，后台执行中)

> [!IMPORTANT]
> 此接口是异步的，调用后立即返回，初始化在后台进行。如果已有初始化任务正在进行，会返回 409 冲突状态。

**响应示例**:
```json
{
  "message": "RAG reinitialization process has been started in the background."
}
```

**冲突响应** (重复初始化):
```json
{
  "detail": "Reinitialization is already in progress."
}
```

### 6.4 查询 RAG 数据库
直接查询 RAG 向量数据库，获取与输入相关的上下文信息。

- **接口**: `POST /rag/query`
- **Content-Type**: `application/json`

**请求参数 (JSON Body)**:

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `query` | string | 是 | 查询文本 |

**请求示例**:
```json
{
  "query": "大堂有哪些摄像头？"
}
```

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "query": "大堂有哪些摄像头？",
    "results": [
      {
        "content": "Camera-01: 位于大堂入口处的摄像头",
        "metadata": {
          "source": "devices",
          "area": "Lobby"
        }
      }
    ],
    "count": 1
  }
}
```