FROM node:20-alpine AS frontend-build
WORKDIR /app/car-sales-web
COPY car-sales-web/package*.json ./
RUN npm ci
COPY car-sales-web/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 FRONTEND_DIR=/app/frontend-dist
COPY car-sales-backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY car-sales-backend/ ./car-sales-backend/
COPY --from=frontend-build /app/car-sales-web/dist ./frontend-dist
WORKDIR /app/car-sales-backend
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]