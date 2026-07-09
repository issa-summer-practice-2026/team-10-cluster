FROM node as frondend-build

WORKDIR /frondend

COPY frontend/package*.json ./

RUN npm ci

COPY frontend/ .

RUN npm run build


FROM python:3:11-slim as backend-build

WORKDIR /backend

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend

COPY --from=frontend-build /app/frontend/dist ./backend/dist

EXPOSE 8000

ENV HOST=0.0.0.0

CMD ["python", "backend/app.py"]