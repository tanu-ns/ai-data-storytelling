# Contributing

## Development Setup

1. **Infrastructure**:
   Run the stack using Docker Compose:
   ```bash
   cd infra
   docker-compose up -d
   ```

2. **Backend**:
   ```bash
   cd api
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

3. **Frontend**:
   ```bash
   cd web
   npm install
   npm run dev
   ```

## Workflow
- Create a branch for your feature.
- Write tests.
- Submit a PR.
