# 生产环境部署文档 (Docker)

本文档描述如何使用 Docker 在局域网中部署前后端服务，支持 HTTPS 访问。

## 网络架构

```
局域网用户
    ↓ https://192.168.31.xxx:443
Docker Nginx (前端容器)
    ↓ SSL 终结
    ├── 静态文件 → /usr/share/nginx/html
    └── /api/* → http://backend:8000
```

---

## 1. 前置准备

### 1.1 目录结构

```
funasr/
├── docker-compose.yml
├── Dockerfile              # 后端 Dockerfile
├── Dockerfile.frontend     # 前端 Dockerfile
├── frontend/
│   ├── nginx.conf          # Nginx 配置
│   └── ...
├── certs/                  # SSL 证书目录
│   ├── cmcc_ca.crt         # CA 根证书（客户端安装）
│   ├── cmcc_ca.key         # CA 私钥（保密）
│   ├── lan_server.crt      # 服务器证书
│   └── lan_server.key      # 服务器私钥
└── ...
```

### 1.2 系统要求

- Docker 20.10+
- Docker Compose 2.0+ (或 docker-compose 1.29+)
- 开放端口：80, 443

---

## 2. SSL 证书生成

### 2.1 生成 CA 根证书

```bash
cd certs/

openssl req -x509 -new -nodes -days 3650 -newkey rsa:2048 \
  -keyout cmcc_ca.key \
  -out cmcc_ca.crt \
  -subj "/CN=MorphK CA/O=MorphK/C=CN" \
  -addext "basicConstraints=critical,CA:TRUE" \
  -addext "keyUsage=critical,keyCertSign,cRLSign"
```

### 2.2 创建扩展配置

创建 `lan_ext.cnf`：

```ini
basicConstraints=CA:FALSE
keyUsage=digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=DNS:local.morphk.icu,DNS:localhost,IP:192.168.31.100,IP:127.0.0.1
```

> [!TIP]
> 修改 `IP:192.168.31.100` 为你的服务器实际 IP 地址

### 2.3 生成服务器证书

```bash
# 生成 CSR
openssl req -new -nodes -newkey rsa:2048 \
  -keyout lan_server.key \
  -out lan_server.csr \
  -subj "/CN=local.morphk.icu"

# 用 CA 签发
openssl x509 -req -in lan_server.csr \
  -CA cmcc_ca.crt -CAkey cmcc_ca.key -CAcreateserial \
  -out lan_server.crt -days 3650 \
  -extfile lan_ext.cnf
```

---

## 3. Docker 配置

### 3.1 docker-compose.yml

```yaml
version: '2.1'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: cmcc-backend
    restart: always
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./config:/app/config
      - ./logs:/app/logs
      - ./chroma_db:/app/chroma_db
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - cmcc-network

  frontend:
    build:
      context: ./frontend
      dockerfile: ../Dockerfile.frontend
    container_name: cmcc-frontend
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./certs/lan_server.crt:/etc/nginx/certs/server.crt:ro
      - ./certs/lan_server.key:/etc/nginx/certs/server.key:ro
      - ./logs/nginx:/var/log/nginx
    depends_on:
      backend:
        condition: service_healthy
    networks:
      - cmcc-network

networks:
  cmcc-network:
    driver: bridge
```

### 3.2 nginx.conf

```nginx
server {
    listen 80;
    server_name localhost;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name localhost;

    # SSL 证书
    ssl_certificate /etc/nginx/certs/server.crt;
    ssl_certificate_key /etc/nginx/certs/server.key;

    # SSL 优化
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;

    # 静态文件
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket 代理
    location /audio/ws {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }
}
```

---

## 4. 部署步骤

### 4.1 构建并启动

```bash
# 构建镜像并启动
docker-compose up -d --build

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 4.2 验证服务

```bash
# 检查容器状态
docker ps

# 测试后端健康检查
curl http://localhost:8000/api/health

# 测试前端 HTTPS
curl -k https://localhost
```

---

## 5. 客户端证书安装

客户端需要安装 `cmcc_ca.crt` 才能信任自签名证书。

### 5.1 iPhone / iPad

1. 发送 `cmcc_ca.crt` 到设备
2. **设置** → **通用** → **VPN与设备管理** → 安装描述文件
3. **设置** → **通用** → **关于本机** → **证书信任设置** → 启用 **MorphK CA**

### 5.2 Android

1. 发送 `cmcc_ca.crt` 到设备
2. **设置** → **安全** → **加密与凭据** → **安装证书** → **CA 证书**

### 5.3 Windows

```powershell
# 以管理员身份运行
certutil -addstore -f "Root" cmcc_ca.crt
```

### 5.4 macOS

```bash
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain cmcc_ca.crt
```

---

## 6. 访问服务

| 访问方式 | URL |
|---------|-----|
| HTTP (自动跳转) | `http://192.168.31.xxx` |
| HTTPS | `https://192.168.31.xxx` |
| 使用域名 | `https://local.morphk.icu` (需配置 hosts) |

### 6.1 配置 hosts（可选）

在客户端 hosts 文件添加：

```
192.168.31.xxx  local.morphk.icu
```

---

## 7. 常用命令

| 操作 | 命令 |
|-----|-----|
| 启动服务 | `docker-compose up -d` |
| 停止服务 | `docker-compose down` |
| 重新构建 | `docker-compose up -d --build` |
| 查看日志 | `docker-compose logs -f` |
| 进入容器 | `docker exec -it cmcc-frontend sh` |
| 重启前端 | `docker-compose restart frontend` |

---

## 8. 故障排查

### 8.1 证书错误

```bash
# 检查证书是否正确挂载
docker exec cmcc-frontend ls -la /etc/nginx/certs/

# 检查 Nginx 配置
docker exec cmcc-frontend nginx -t
```

### 8.2 后端连接失败

```bash
# 检查后端健康状态
docker-compose ps

# 检查网络连通性
docker exec cmcc-frontend ping backend
```

### 8.3 查看详细日志

```bash
# Nginx 错误日志
docker exec cmcc-frontend cat /var/log/nginx/error.log

# 后端日志
docker-compose logs backend
```

---

## 9. 安全提醒

> [!CAUTION]
> - `cmcc_ca.key` 是 CA 私钥，**绝对不能泄露**
> - 自签名证书仅用于内网部署
> - 公网环境应使用 Let's Encrypt 证书
