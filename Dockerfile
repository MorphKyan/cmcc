# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

# 构建参数 - 控制可选功能
ARG ENABLE_MIC_INPUT=false
ARG ENABLE_OLLAMA=false

WORKDIR /app

# 配置 apt 使用阿里云镜像（加速国内构建）
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# 配置 pip 使用清华镜像
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装系统依赖（av 需要 ffmpeg）
# 使用 cache mount 加速 apt 安装
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
  rm -f /etc/apt/apt.conf.d/docker-clean \
  && apt-get update && apt-get install -y --no-install-recommends \
  curl \
  ffmpeg \
  git

# 复制依赖文件
COPY requirements/ /tmp/requirements/

# 安装核心依赖
# 使用 cache mount 加速 pip 安装
RUN --mount=type=cache,target=/root/.cache/pip \
  pip install --no-cache-dir \
  --extra-index-url https://download.pytorch.org/whl/cpu \
  -r /tmp/requirements/base.txt

# 条件安装可选依赖 - 本地麦克风输入
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
  --mount=type=cache,target=/root/.cache/pip \
  if [ "$ENABLE_MIC_INPUT" = "true" ]; then \
  rm -f /etc/apt/apt.conf.d/docker-clean \
  && apt-get update && apt-get install -y --no-install-recommends \
  portaudio19-dev && \
  pip install --no-cache-dir -r /tmp/requirements/mic.txt; \
  fi

# 条件安装可选依赖 - Ollama 支持
RUN --mount=type=cache,target=/root/.cache/pip \
  if [ "$ENABLE_OLLAMA" = "true" ]; then \
  pip install --no-cache-dir -r /tmp/requirements/ollama.txt; \
  fi

# 清理临时文件
RUN rm -rf /tmp/requirements

# 设置运行时环境变量
ENV ENABLE_MIC_INPUT=$ENABLE_MIC_INPUT
ENV ENABLE_OLLAMA=$ENABLE_OLLAMA

# 复制应用代码
COPY src/ ./src/
COPY config/ ./config/
COPY data/ ./data/
COPY main.py .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
