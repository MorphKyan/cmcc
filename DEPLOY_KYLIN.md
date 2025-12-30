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

### 配置 Docker 镜像加速（推荐）

国内网络环境下，建议配置镜像加速以提升拉取速度：

```bash
# 创建或编辑 Docker daemon 配置文件
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://dockerhub.icu",
    "https://docker.1panel.live"
  ]
}
EOF

# 重新加载配置并重启 Docker
sudo systemctl daemon-reload
sudo systemctl restart docker
```

> **说明**：项目的 Dockerfile 已内置以下国内镜像配置：
> - **apt 源**：阿里云镜像 (`mirrors.aliyun.com`)
> - **pip 源**：清华镜像 (`pypi.tuna.tsinghua.edu.cn`)
> - **npm 源**：淘宝镜像 (`registry.npmmirror.com`)

## 项目结构

确保以下文件已上传到服务器（可通过 `scp`、`git clone` 或 USB 传输）：

```
cmcc/
├── Dockerfile                # 后端 Docker 镜像配置
├── Dockerfile.frontend       # 前端 Docker 镜像配置
├── docker-compose.yml        # Docker Compose 编排配置
├── requirements/             # Python 依赖（分层）
│   ├── base.txt              # 核心依赖
│   ├── mic.txt               # 麦克风输入依赖（可选）
│   └── ollama.txt            # Ollama 支持依赖（可选）
├── requirements.txt          # Python 依赖（汇总）
├── src/                      # 后端源码
├── frontend/                 # 前端源码
│   ├── nginx.conf            # Nginx 配置
│   ├── local_morphk_icu.pem  # SSL 证书
│   └── local_morphk_icu.key  # SSL 私钥
├── config/                   # 配置文件
├── data/                     # 数据目录
├── chroma_db/                # 向量数据库存储
└── logs/                     # 日志目录
```

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
```

## 部署步骤

### 1. 进入项目目录

```bash
cd /path/to/cmcc
```

### 2. 创建必要的目录

```bash
mkdir -p logs/nginx chroma_db
```

### 3. 配置功能开关（可选）

项目支持通过 Docker 构建参数和环境变量控制可选功能：

| 功能 | 构建参数 | 环境变量 | 默认值 |
|------|----------|----------|--------|
| 本地麦克风输入 | `ENABLE_MIC_INPUT` | `ENABLE_MIC_INPUT` | `false` |
| Ollama 本地服务 | `ENABLE_OLLAMA` | `ENABLE_OLLAMA` | `false` |

如需启用 Ollama 支持，修改 `docker-compose.yml`：

```yaml
services:
  backend:
    build:
      args:
        ENABLE_OLLAMA: "true"    # 构建时安装 langchain-ollama
    environment:
      - ENABLE_OLLAMA=true       # 运行时启用功能
```

> **注意**：如果 `config/config.toml` 中 `rag.provider` 或 `llm.provider` 设置为 `"ollama"`，
> 必须启用 `ENABLE_OLLAMA`，否则应用启动时会报错。

### 4. 配置服务端口（可选）

默认情况下，前端使用端口 80/443，后端使用端口 8000。如需修改，请创建 `.env` 文件：

```bash
# 复制示例配置
cp .env.example .env

# 编辑配置
vim .env
```

`.env` 文件内容示例：
```env
# 前端 HTTP 端口
FRONTEND_PORT=8380

# 前端 HTTPS 端口
FRONTEND_SSL_PORT=8443

# 后端 API 端口
BACKEND_PORT=23306
```

### 5. 构建并启动服务

```bash
# 默认构建（不含 Ollama 和麦克风输入）
docker compose up -d --build

# 或手动指定构建参数
docker compose build --build-arg ENABLE_OLLAMA=true
docker compose up -d
```

此命令将：
- 构建后端和前端 Docker 镜像
- 创建并启动容器
- 后端启动后，前端才会启动（通过健康检查确保）

### 6. 验证部署

检查容器运行状态：
```bash
docker compose ps
```

应看到两个服务都处于 `running` 状态：
```
NAME            STATUS                   PORTS
cmcc-backend    Up (healthy)             0.0.0.0:8000->8000/tcp
cmcc-frontend   Up                       0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
```

### 7. 访问应用

- **前端页面**: `https://<服务器IP>`（HTTP 自动跳转 HTTPS）
- **后端 API**: `https://<服务器IP>/api`（通过 Nginx 代理）
- **WebSocket**: `wss://<服务器IP>/ws`（通过 Nginx 代理）

## 日常维护

### 查看日志

```bash
# 查看所有容器日志
docker compose logs -f

# 仅查看后端日志
docker compose logs -f backend

# 仅查看前端日志
docker compose logs -f frontend
```

### 停止服务

```bash
docker compose down
```

### 重启服务

```bash
docker compose restart
```

### 更新应用

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker compose up -d --build
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

### 权限问题

```bash
# 将当前用户添加到 docker 组
sudo usermod -aG docker $USER
# 重新登录后生效
```

### 端口冲突

如果默认端口被占用，请新建或修改 `.env` 文件（参考 [配置服务端口](#4-配置服务端口可选)）：

```env
FRONTEND_PORT=8080
FRONTEND_SSL_PORT=8443
BACKEND_PORT=8080
```

### 容器无法启动

```bash
# 查看详细错误信息
docker compose logs backend
docker compose logs frontend

# 检查镜像构建是否成功
docker compose build --no-cache
```

### 健康检查失败

如果后端健康检查失败，检查：
1. 后端服务是否正常启动
2. `/api/health` 接口是否正常响应

```bash
# 进入后端容器调试
docker compose exec backend bash

# 手动测试健康检查
curl http://localhost:8000/api/health
```

### SSL 证书问题

确保证书文件存在且路径正确：
```bash
ls -la frontend/local_morphk_icu.pem
ls -la frontend/local_morphk_icu.key
```
