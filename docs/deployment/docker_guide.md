# SmartMES - Docker & Local Deployment Guide

## 1. Overview
SmartMES uses Docker Compose to run all services locally without requiring cloud subscriptions or complex host configuration.

---

## 2. Containerized Services

| Service Name | Container Name | Image | Port Mapping | Internal Host |
| :--- | :--- | :--- | :--- | :--- |
| **postgres** | `smartmes_postgres` | `postgres:16-alpine` | `5432:5432` | `postgres` |
| **redis** | `smartmes_redis` | `redis:7-alpine` | `6379:6379` | `redis` |
| **backend** | `smartmes_backend` | Python 3.11 FastAPI | `8000:8000` | `backend` |
| **frontend** | `smartmes_frontend` | Next.js 14 Standalone | `3000:3000` | `frontend` |

---

## 3. Useful Commands

```bash
# Start all containers in background
docker-compose up -d

# Check status of running containers
docker-compose ps

# View backend logs
docker-compose logs -f backend

# Rebuild containers after code changes
docker-compose up --build -d

# Stop and remove containers and networks
docker-compose down
```
