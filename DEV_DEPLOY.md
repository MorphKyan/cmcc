# 开发测试环境部署文档

本文档描述如何在家庭网络环境中部署前后端服务，使其可通过公网访问。

## 网络架构

```
用户浏览器
    ↓ https://web.cmcc.morphk.icu:8443
Cloudflare DNS (灰云, DNS Only)
    ↓ 解析到 IPv6
2409:8a00:3270:e80::742:8443
    ↓ IPv6 直连
NPM Docker (192.168.31.200:8443 → 容器:443)
    ↓ SSL 终结 + 反向代理
Vite 前端 (192.168.31.100:5173)
```

---

## 1. Cloudflare DNS 配置

### 1.1 添加 DNS 记录

| 类型 | 名称 | 内容 | 代理状态 |
|-----|-----|------|---------|
| AAAA | web.cmcc | `2409:8a00:3270:e80::742` | **DNS Only（灰云）** |

> [!IMPORTANT]
> 必须使用 **DNS Only（灰云）** 模式，不能开启 Cloudflare 代理（橙云）。
> 原因：WebSocket 实时语音流需要直连，Cloudflare 代理会影响长连接稳定性。

### 1.2 获取 IPv6 地址

在 NPM 服务器上运行：

```bash
ip -6 addr show | grep "scope global"
```

使用输出中的公网 IPv6 地址（通常是 `2409:` 开头的地址）。

---

## 2. SSL 证书生成

由于运营商封锁 443 端口，我们使用自签名证书 + 非标准端口方案。

### 2.1 生成 CA 根证书

```bash
openssl req -x509 -new -nodes -days 3650 -newkey rsa:2048 \
  -keyout cmcc_ca.key \
  -out cmcc_ca.crt \
  -subj "/CN=MorphK CA/O=MorphK/C=CN" \
  -addext "basicConstraints=critical,CA:TRUE" \
  -addext "keyUsage=critical,keyCertSign,cRLSign"
```

### 2.2 生成服务器证书签名请求 (CSR)

```bash
openssl req -new -nodes -newkey rsa:2048 \
  -keyout cmcc_server.key \
  -out cmcc_server.csr \
  -subj "/CN=web.cmcc.morphk.icu"
```

### 2.3 创建扩展配置文件

创建 `server_ext.cnf`：

```ini
basicConstraints=CA:FALSE
keyUsage=digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=DNS:web.cmcc.morphk.icu
```

### 2.4 使用 CA 签发服务器证书

```bash
openssl x509 -req -in cmcc_server.csr \
  -CA cmcc_ca.crt -CAkey cmcc_ca.key -CAcreateserial \
  -out cmcc_server.crt -days 3650 \
  -extfile server_ext.cnf
```

### 2.5 证书文件说明

| 文件 | 用途 | 安装位置 |
|-----|------|---------|
| `cmcc_ca.crt` | CA 根证书 | iPhone/Android 设备 |
| `cmcc_server.crt` | 服务器证书 | NPM |
| `cmcc_server.key` | 服务器私钥 | NPM |

---

## 3. Nginx Proxy Manager 配置

### 3.1 Docker 端口映射

```yaml
ports:
  - "8443:443"    # HTTPS（使用非标准端口绑开运营商限制）
  - "8880:81"     # NPM 管理界面
  - "3000:3000"   # 其他服务（可选）
```

### 3.2 上传 SSL 证书

1. 登录 NPM 管理界面：`http://192.168.31.200:8880`
2. 进入 **SSL Certificates** → **Add SSL Certificate** → **Custom**
3. 上传：
   - **Certificate**: `cmcc_server.crt`
   - **Certificate Key**: `cmcc_server.key`
   - **Intermediate Certificate**: 留空
4. 保存

### 3.3 配置 Proxy Host

| 配置项 | 值 |
|-------|---|
| Domain Names | `web.cmcc.morphk.icu` |
| Scheme | `http` |
| Forward Hostname/IP | `192.168.31.100` |
| Forward Port | `5173` |
| SSL Certificate | 选择上传的证书 |
| Force SSL | ✅ |
| Websockets Support | ✅ |

### 3.4 高级配置 (Advanced)

在 Advanced 标签页添加：

```nginx
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_read_timeout 86400;
proxy_send_timeout 86400;
```

### 3.5 完整 JSON 配置参考

```json
{
  "domainNames": ["web.cmcc.morphk.icu"],
  "forwardHost": "192.168.31.100",
  "forwardPort": 5173,
  "forwardScheme": "http",
  "certificateId": "1",
  "sslForced": true,
  "allowWebsocketUpgrade": true,
  "advancedConfig": "proxy_set_header Upgrade $http_upgrade;\nproxy_set_header Connection \"upgrade\";\nproxy_read_timeout 86400;\nproxy_send_timeout 86400;",
  "enabled": true
}
```

---

## 4. 路由器配置

### 4.1 IPv6 防火墙规则

由于 IPv6 没有 NAT，需要在路由器开放入站端口：

| 协议 | 端口 | 目标 IP | 说明 |
|-----|-----|--------|------|
| TCP | 8443 | NPM 机器的 IPv6 地址 | HTTPS 访问 |

### 4.2 IPv4 端口转发（可选）

如果需要 IPv4 访问：

| 外部端口 | 内部 IP | 内部端口 |
|---------|---------|---------|
| 8443 | 192.168.31.200 | 8443 |

---

## 5. Vite 前端配置

### 5.1 vite.config.js 关键配置

```javascript
server: {
  host: '0.0.0.0',
  port: 5173,
  cors: true,
  open: false,
  allowedHosts: ['web.cmcc.morphk.icu', 'localhost'],
  hmr: {
    protocol: 'wss',
    host: 'web.cmcc.morphk.icu',
    clientPort: 8443,
  },
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      secure: false,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

### 5.2 启动前端服务

```bash
cd frontend
npm run dev
```

---

## 6. 后端服务配置

### 6.1 启动后端

```bash
python main.py --host 0.0.0.0 --port 8000
```

### 6.2 如需公网访问后端 API

在 NPM 中添加另一个 Proxy Host：

| 配置项 | 值 |
|-------|---|
| Domain Names | `api.cmcc.morphk.icu` |
| Forward Hostname/IP | `192.168.31.100` |
| Forward Port | `8000` |

---

## 7. 客户端证书安装

### 7.1 iPhone / iPad

1. 将 `cmcc_ca.crt` 发送到设备（AirDrop/邮件/网盘）
2. 点击文件 → 安装描述文件
3. **设置** → **通用** → **VPN与设备管理** → 安装描述文件
4. **设置** → **通用** → **关于本机** → 滚到底部 → **证书信任设置**
5. 找到 **MorphK CA**，**打开开关**启用完全信任

### 7.2 Android

1. 将 `cmcc_ca.crt` 发送到设备
2. **设置** → **安全** → **加密与凭据** → **安装证书**
3. 选择 **CA 证书**
4. 选择文件并安装

### 7.3 Windows

1. 双击 `cmcc_ca.crt`
2. 点击 **安装证书**
3. 选择 **本地计算机** → **将所有证书放入下列存储** → **受信任的根证书颁发机构**
4. 完成安装

### 7.4 macOS

1. 双击 `cmcc_ca.crt` 打开钥匙串访问
2. 添加到 **登录** 钥匙串
3. 找到 **MorphK CA** → 右键 → **显示简介**
4. 展开 **信任** → **使用此证书时** 改为 **始终信任**

---

## 8. 验证测试

### 8.1 内网连通性测试

```powershell
# 测试 NPM HTTPS 端口
Test-NetConnection -ComputerName 192.168.31.200 -Port 8443

# 测试 Vite 服务
Test-NetConnection -ComputerName 192.168.31.100 -Port 5173

# 测试 NPM 能否访问 Vite
curl http://192.168.31.100:5173
```

### 8.2 DNS 解析测试

```powershell
nslookup web.cmcc.morphk.icu
```

应只返回 IPv6 地址，不应有 Cloudflare IP（104.x.x.x 或 172.67.x.x）。

### 8.3 公网访问测试

使用手机 **关闭 WiFi，用 4G/5G 流量**访问：

```
https://web.cmcc.morphk.icu:8443
```

---

## 9. 故障排查

| 问题 | 可能原因 | 解决方案 |
|-----|---------|---------|
| 连接超时 | 防火墙阻止 / 端口未开放 | 检查路由器 IPv6 防火墙 |
| 连接被拒绝 | 服务未运行 | 检查 NPM / Vite 是否启动 |
| 证书错误 | 证书未安装或未信任 | 按照第 7 节安装证书 |
| DNS 返回 Cloudflare IP | 代理已开启 | 改为 DNS Only（灰云） |
| WebSocket 断连 | Cloudflare 代理干扰 | 确保使用 DNS Only |

### 9.1 查看 NPM 日志

```bash
docker logs nginx-proxy-manager
docker logs -f nginx-proxy-manager  # 实时查看
```

---

## 10. 文件清单

```
certs/
├── cmcc_ca.crt          # CA 根证书（安装到设备）
├── cmcc_ca.key          # CA 私钥（妥善保管，不要泄露）
├── cmcc_server.crt      # 服务器证书（上传到 NPM）
├── cmcc_server.key      # 服务器私钥（上传到 NPM）
└── server_ext.cnf       # OpenSSL 扩展配置
```

---

## 11. 安全提醒

> [!CAUTION]
> - **CA 私钥 (`cmcc_ca.key`)** 必须妥善保管，泄露后可签发任意证书
> - 自签名证书仅用于开发测试环境
> - 生产环境应使用 Let's Encrypt 或商业 CA 签发的证书
