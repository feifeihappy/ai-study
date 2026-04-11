# 使用官方 Python 运行时作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制当前目录下的所有文件到容器的 /app 目录
COPY . .

# 暴露 Streamlit 默认端口
EXPOSE 8501

# 运行应用
# 注意：这里不需要设置 API KEY，运行时通过 -e 传入
CMD ["streamlit", "run", "web_app.py", "--server.port=8501", "--server.address=0.0.0.0"]