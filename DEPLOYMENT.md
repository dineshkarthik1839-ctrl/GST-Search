# CompanyLens - Live Production Deployment Guide

CompanyLens is configured as an **All-in-One, Single-Port Web Application & API Gateway**.

- **Frontend Web UI**: `http://<your-domain>/` (Served directly by FastAPI from compiled Vite React build)
- **Backend API Gateway**: `http://<your-domain>/api/v1`
- **Interactive Swagger Docs**: `http://<your-domain>/docs`
- **Health Check Endpoint**: `http://<your-domain>/api/v1/health`

---

## Option 1: One-Click Deploy on Render (Recommended - Free Tier Available)

1. **Push your repository** to GitHub (already linked to `https://github.com/dineshkarthik1839-ctrl/GST-Search.git`).
2. Log into [Render.com](https://render.com/).
3. Click **New +** -> **Blueprints**.
4. Connect your GitHub repository `GST-Search`.
5. Render will automatically detect `render.yaml` and launch:
   - **PostgreSQL Database** (`companylens-db`)
   - **Unified Web Service** (`companylens-app`) running on port `8000`.
6. Once deployed, Render will generate a live URL (e.g., `https://companylens-app.onrender.com`).

---

## Option 2: Deploy on Railway.app

1. Log into [Railway.app](https://railway.app/).
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select `dineshkarthik1839-ctrl/GST-Search`.
4. Add a **PostgreSQL Database** service inside the project.
5. In your Railway service variables, set:
   ```env
   DATABASE_URL=${{ Postgres.DATABASE_URL }}
   ENVIRONMENT=production
   ```
6. Click **Deploy**. Railway will automatically detect the `Dockerfile` and `railway.json`.

---

## Option 3: Local or VPS Production (Docker Compose)

To run CompanyLens in production mode on any VPS (AWS EC2, DigitalOcean droplet, Linode, Ubuntu server, or locally):

```bash
# 1. Clone the repository
git clone https://github.com/dineshkarthik1839-ctrl/GST-Search.git
cd GST-Search

# 2. Build and start containers in detached mode
docker-compose up -d --build

# 3. Access your live instance
# Web Application & API Gateway: http://localhost:8000
# Swagger API Docs: http://localhost:8000/docs
```

---

## Option 4: Deploying on Docker Hub & Cloud VPS (Portainer/K8s)

```bash
# Build production multi-stage image
docker build -t yourusername/companylens:latest .

# Push to Docker Hub
docker push yourusername/companylens:latest

# Run anywhere
docker run -d -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:password@host:5432/companylens_db" \
  yourusername/companylens:latest
```

---

## Environment Variables Reference

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `DATABASE_URL` | PostgreSQL Connection URI | `postgresql://postgres:root@localhost:5433/companylens_db` |
| `ENVIRONMENT` | Deployment Environment (`development` / `production`) | `production` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |
| `PORT` | Single server port exposed | `8000` |
