FROM python:3.11-slim AS builder

WORKDIR /app
# 安装依赖
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

#生产阶段
FROM python:3.11-slim
WORKDIR /app
# 复制依赖
COPY --from=builder /root/.local /root/.local
# 复制应用代码
COPY . .
# 设置环境变量
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app
# 暴露端口
EXPOSE 8000

#健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
