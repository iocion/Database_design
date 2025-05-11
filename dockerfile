# 使用官方 Python 镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 创建非 root 用户
RUN useradd -m myuser

# 复制 requirements.txt 并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码到工作目录
COPY . .

# 切换到非 root 用户
USER myuser

# 暴露端口
EXPOSE 5000

# 运行 Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "run:app", "--workers", "4", "--timeout", "120", "--worker-class", "sync"]