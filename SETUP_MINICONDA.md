# Windows Miniconda 环境配置指南（CMD）

本文档说明如何在 Windows 系统下使用 Miniconda 和 CMD 配置项目环境。

## 前置要求

- 已安装 Miniconda3
- 安装路径：`C:\Users\MorphKyan\miniconda3`

## 配置步骤

### 1. 打开 CMD

按下 `Win + R`，输入 `cmd`，按回车打开命令提示符。

### 2. 导航到项目目录

```cmd
cd C:\Users\MorphKyan\cmcc
```

### 3. 删除已存在的失败环境（如果有）

```cmd
conda env remove -n cmcc_env
```

### 4. 创建新的 Conda 环境

```cmd
conda env create -f environment.yml
```

此命令将：
- 创建名为 `cmcc_env` 的环境
- 安装 Python 3.12
- 安装所有项目依赖（包括 modelscope、langchain、fastapi 等）

**注意**：此过程可能需要几分钟，请耐心等待。

### 5. 激活环境

```cmd
conda activate cmcc_env
```

激活成功后，命令提示符前会显示 `(cmcc_env)`。

### 6. 验证安装

检查 Python 版本：
```cmd
python --version
```

应显示：`Python 3.12.x`

检查已安装的包：
```cmd
pip list
```

## 常用命令

### 激活环境
```cmd
conda activate cmcc_env
```

### 退出环境
```cmd
conda deactivate
```

### 查看所有环境
```cmd
conda env list
```

### 删除环境
```cmd
conda env remove -n cmcc_env
```

### 更新依赖（如果 requirements.txt 有变化）
```cmd
conda activate cmcc_env
pip install -r requirements.txt --upgrade
```

### 更新环境配置（如果 environment.yml 有变化）
```cmd
conda env update --file environment.yml --prune
```
此命令会根据 `environment.yml` 更新当前环境的依赖，`--prune` 选项会移除不再需要的包。

## 故障排除

### 问题：`conda` 命令不可用

**解决方案**：初始化 Miniconda
```cmd
C:\Users\MorphKyan\miniconda3\Scripts\activate.bat
conda init cmd.exe
```

然后关闭并重新打开 CMD。

### 问题：环境创建失败

1. 确保使用的是 CMD（不是 PowerShell）
2. 检查网络连接
3. 尝试使用国内镜像源：
```cmd
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --set show_channel_urls yes
```

## 环境说明

- **环境名称**：`cmcc_env`
- **Python 版本**：3.12
- **主要依赖**：
  - FastAPI：Web 框架
  - LangChain：LLM 应用框架
  - ModelScope：模型服务
  - Ollama：本地 LLM
  - FunASR：语音识别
  - ChromaDB：向量数据库
  - Torch：深度学习框架

## 下一步

环境配置完成后，您可以：

1. 启动应用：
```cmd
conda activate cmcc_env
python main.py
```

2. 运行测试：
```cmd
conda activate cmcc_env
python test_rag_llm_pipeline.py
```
