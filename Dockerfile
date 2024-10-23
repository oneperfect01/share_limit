# 使用 Python 3.11 Alpine 版本作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 将当前目录下的所有文件复制到容器
COPY . .
# 将当前目录下的配置文件复制到容器的 /app 目录
COPY config.json /app

# 安装依赖，添加 `--no-cache` 避免缓存
RUN pip install --no-cache-dir -r requirements.txt

# 暴露应用运行时的端口
EXPOSE 41758


# 设置容器启动时执行的命令
CMD ["python", "./app.py"]
