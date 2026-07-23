# AI Government Exam Platform

A production-ready MVP for an AI-powered government exam preparation platform.

## Architecture

This platform follows Clean Architecture and SOLID principles, utilizing a Microservice-oriented Monorepo structure.

- **Frontend:** React + TypeScript + Vite
- **Backend:** FastAPI (Python)
- **AI Services:** Dedicated Python services
- **Database:** PostgreSQL
- **Cache:** Redis
- **Infrastructure:** Docker Compose (local dev)

## Development Setup

1. Copy `.env.example` to `.env` and fill in the values.
2. Run `docker-compose up --build` to start all services.
3. Access the frontend at `http://localhost:3000`.
4. Access the backend API docs at `http://localhost:8000/docs`.

## Milestones

- [x] Milestone 1: Foundation Setup
- [ ] Milestone 2: Authentication
- [ ] Milestone 3: Taxonomy & Content Management
