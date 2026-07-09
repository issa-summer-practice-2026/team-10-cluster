FROM node:lts as frontend-build

WORKDIR /frontend

COPY frontend/package*.json ./

RUN npm ci

COPY frontend/ .

RUN npm run build

FROM python:3.11-slim as backend-build

WORKDIR /backend

COPY backend/dev-requirements.txt .
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r dev-requirements.txt

COPY backend/ .

COPY --from=frontend-build /frontend/dist /frontend/dist

EXPOSE 8000

ENV HOST=0.0.0.0

CMD ["python", "-m" ,"app"]