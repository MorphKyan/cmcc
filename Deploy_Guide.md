# 麒麟 V10 Docker 部署指南

本指南描述如何在麒麟 V10 服务器上使用 Docker 部署应用。

## 前置条件

### 安装 Docker

麒麟 V10 基于 Linux，可以使用标准安装脚本或包管理器安装 Docker：

```bash
# 使用官方安装脚本
curl -fsSL https://get.docker.com | bash

# 或使用包管理器（以 apt 为例）
sudo apt update
sudo apt install docker.io docker-compose-plugin
```

验证安装：
```bash
docker --version
docker compose version
```

### 启用 Docker 服务

```bash
sudo systemctl enable docker
sudo systemctl start docker
```

## 项目结构

对于直接拉取镜像部署，确保以下文件和目录结构已上传或在服务器上部署：

```
cmcc/
├── docker-compose-deploy.yaml  # Docker Compose 部署配置文件
├── certs/                      # SSL 证书挂载目录
│   ├── lan_server.crt          # SSL 证书文件
│   └── lan_server.key          # SSL 私钥文件
├── config/                     # 后端配置文件目录
├── data/                       # 后端数据存储目录
├── models/                     # 模型存储目录（如有需要）
├── chroma_db/                  # 向量数据库存储目录
└── logs/                       # 日志持久化目录
```
<!-- 
## SSL 证书配置

应用使用 HTTPS 访问，需要配置 SSL 证书。

### 使用现有证书

将证书文件放置到 `frontend/` 目录：
- `local_morphk_icu.pem` - 证书文件
- `local_morphk_icu.key` - 私钥文件

### 生成自签名证书（测试用）

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout frontend/local_morphk_icu.key \
  -out frontend/local_morphk_icu.pem \
  -subj "/CN=localhost"
``` -->

## 部署步骤

### 1. 克隆项目并进入目录

```bash
git clone https://github.com/MorphKyan/cmcc.git
cd cmcc
```

### 2. 下载模型文件

应用运行需要预选下载音频处理模型。请确保服务器已安装 Python 并在项目根目录下执行：

```bash
python download_models.py
```

该脚本会自动从 HuggingFace 和 GitHub 下载并验证模型文件（包含 VAD、SenseVoiceSmall 等），并存放在 `./models` 目录。

### 3. 配置服务端口（可选）

默认情况下，前端使用端口 80/443，后端使用端口 8000。如需修改，请创建 `.env` 文件：

```bash
# 复制示例配置
cp .env.example .env

# 编辑配置
vim .env
```

`.env` 文件内容示例：
```env
# 前端 HTTPS 端口（默认 443）
FRONTEND_SSL_PORT=8443

# 后端 API 端口（仅做 HTTP 暴露供特殊情况访问时修改这部分，默认 8000）
BACKEND_PORT=23306
```

### 4. 配置业务参数

项目使用 TOML 格式文件管理后端核心业务参数（如 LLM 提供商、检索库、AEP 中控接口等）。

请根据您的部署环境选择对应的模版并进行配置：

- **生产环境 (Production)**:
  ```bash
  cp config/config.prod.example.toml config/config.toml
  ```
- **开发环境 (Development)**:
  ```bash
  cp config/config.dev.example.toml config/config.toml
  ```

> [!TIP]
> 如果您需要针对特定场景进行微调，可以参考通用示例 `config/config.example.toml`。

复制后，请务必使用编辑器（如 `vim`）修改 `config/config.toml` 中的关键敏感信息，例如 `api_key` 和 `base_url`。

### 5. 启动服务

需先登录阿里云镜像仓库（只需一次）：
用户名：MorphKyan
密码：cmcc1425

```bash
# 登录阿里云镜像仓库（输入你的阿里云账号和 registry 密码）
docker login crpi-levx0ydbtxzjpzw9.cn-beijing.personal.cr.aliyuncs.com

# 拉取最新镜像并启动
docker compose -f docker-compose-deploy.yaml pull
docker compose -f docker-compose-deploy.yaml up -d
```

### 6. 验证部署

检查容器运行状态：
```bash
docker compose -f docker-compose-deploy.yaml ps
```

应看到两个服务都处于正常运行状态：
```
NAME            STATUS                   PORTS
cmcc-backend    Up (healthy)             0.0.0.0:8000->8000/tcp
cmcc-frontend   Up                       0.0.0.0:443->443/tcp
```

### 7. 访问应用

- **前端页面**: `https://<服务器IP>:<FRONTEND_SSL_PORT>` (当前环境只支持 HTTPS，默认 443 端口可省略)
- **后端 API**: 
  - 通过 Nginx (HTTPS): `https://<服务器IP>:<FRONTEND_SSL_PORT>/api/`
  - 直接后端访问 (HTTP): `http://<服务器IP>:<BACKEND_PORT>/api/`
- **WebSocket**: `wss://<服务器IP>:<FRONTEND_SSL_PORT>/api/audio/ws`（通过 Nginx 代理）

## 日常维护

### 查看日志

```bash
# 查看所有容器日志
docker compose -f docker-compose-deploy.yaml logs -f

# 仅查看后端日志
docker compose -f docker-compose-deploy.yaml logs -f backend

# 仅查看前端日志
docker compose -f docker-compose-deploy.yaml logs -f frontend
```

### 停止服务

```bash
docker compose -f docker-compose-deploy.yaml down
```

### 重启服务

```bash
docker compose -f docker-compose-deploy.yaml restart
```

### 更新应用

```bash
# 重拉镜像并重启
docker compose -f docker-compose-deploy.yaml pull
docker compose -f docker-compose-deploy.yaml up -d
```

## 日志管理

### 应用日志

日志持久化到宿主机文件系统：

| 日志类型 | 路径 | 说明 |
|---------|------|------|
| 主日志 | `./logs/app_YYYY-MM-DD.log` | 每日轮转 |
| 错误日志 | `./logs/error_YYYY-MM-DD.log` | ERROR 级别以上 |
| Nginx 访问日志 | `./logs/nginx/access.log` | HTTP 请求记录 |
| Nginx 错误日志 | `./logs/nginx/error.log` | Nginx 错误 |

查看实时日志：
```bash
# 应用主日志
tail -f logs/app_$(date +%Y-%m-%d).log

# Nginx 访问日志
tail -f logs/nginx/access.log
```

### 日志保留策略

- 主日志：30 天
- 错误日志：60 天
- 过期日志自动压缩为 `.zip` 文件

## 故障排查

### 端口冲突

如果默认端口被占用，请新建或修改 `.env` 文件（参考 [配置服务端口](#3-配置服务端口可选)）：

```env
FRONTEND_SSL_PORT=8443
BACKEND_PORT=23306
```

### 容器无法启动

```bash
# 查看详细错误信息
docker compose -f docker-compose-deploy.yaml logs backend
docker compose -f docker-compose-deploy.yaml logs frontend
```

### 健康检查失败

如果后端健康检查失败，检查：
1. 后端服务是否正常启动
2. `/api/` 接口是否正常响应 (可在内部访问 `http://localhost:8000/api/`)

```bash
# 进入后端容器调试
docker compose -f docker-compose-deploy.yaml exec backend bash

# 手动测试健康检查
curl http://localhost:8000/api/
```