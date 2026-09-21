# Satellite Image Analysis and Land Use/Land Cover Classification System

## 1. Project Overview
This application provides a cloud-based platform for satellite imagery analysis. It aims to allow authenticated users to upload satellite imagery, process it through an ML pipeline to classify land-use/land-cover categories, and visualize the results.

## 2. Architecture
```text
                    +-----------------------+
                    |        User           |
                    +-----------+-----------+
                                |
                                v
                    +-----------------------+
                    | React + TypeScript    |
                    | Frontend (Static)     |
                    +-----------+-----------+
                                | REST API
                                v
                    +-----------------------+
                    | FastAPI Backend       |
                    | Python                |
                    +-----+-----------+-----+
                          |           |
                  +-------v---+   +---v-------+
                  |           |   |           |
        +---------+---------+ |   | +---------+---------+
        | PostgreSQL        | |   | | ML Pipeline       |
        | Application Data  | |   | | PyTorch / EuroSAT |
        +-------------------+ |   | +-------------------+
```

## 3. Required Services
For a production deployment, the application requires the following services:
- **Frontend Hosting**: A static file host to serve the built React application (e.g., Vercel, Netlify, AWS S3+CloudFront, or Nginx).
- **Backend Container Engine**: A Docker-compatible runtime capable of running the FastAPI server (e.g., Render, Railway, AWS ECS, Fly.io).
- **Database**: A managed PostgreSQL 15+ database instance (e.g., Supabase, Neon, AWS RDS).
- **Object Storage**: (Optional but recommended) S3-compatible object storage for storing uploaded images persistently across container restarts (e.g., AWS S3, Cloudflare R2, MinIO).

## 4. Environment Variables
In production, configuring the backend strictly through environment variables is required. Do not use `.env` files in source control.

**Required Backend Variables:**
- `DATABASE_URL`: Connection string for PostgreSQL (e.g., `postgresql://user:password@host:5432/dbname`)
- `JWT_SECRET_KEY`: A secure random string (minimum 32 chars) used to sign JSON Web Tokens.
- `JWT_ALGORITHM`: Typically `HS256`.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Expiration time for authentication tokens (e.g., `1440`).
- `CORS_ORIGINS`: Comma-separated list of allowed origins or JSON array (e.g., `https://your-frontend-domain.example`).
- `ENVIRONMENT`: Set to `production` to enable strict error handling and startup validation.
- `LOG_LEVEL`: Typically `INFO` or `WARNING`.

**Storage Configuration:**
- `STORAGE_PROVIDER`: `local` or `s3`.
- `STORAGE_LOCAL_ROOT`: Directory for uploads when using `local` storage.
- `S3_ENDPOINT_URL`, `S3_REGION`, `S3_BUCKET_NAME`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`: Required if `STORAGE_PROVIDER=s3`.

**Frontend Variable (Build Time):**
- `VITE_API_BASE_URL`: Base URL of the backend API (e.g., `https://api.your-domain.example`).

## 5. Local Docker Startup
To run the full stack locally using Docker Compose, which mirrors the production configuration:
1. Ensure Docker and Docker Compose are installed.
2. Run the application:
```bash
docker compose up -d --build
```
3. The UI will be available on `http://localhost:5173`, the API on `http://localhost:8000`, and PostgreSQL on `5432`.

## 6. Database Migration
Migrations are managed via Alembic. In a local Docker setup, they can be run securely:
```bash
docker compose exec backend alembic upgrade head
```
For cloud deployments, run `alembic upgrade head` either via a release command (e.g., Render's Release Command) or manually on the container.

## 7. Production Configuration & Deployment

### Recommended Deployment Architecture
**Frontend (Vercel / Netlify):**
1. Connect your repository to the hosting platform.
2. Set the build command to `npm run build` and publish directory to `dist/`.
3. Configure the environment variable `VITE_API_BASE_URL` to point to your live backend domain.

**Backend (Render / Railway / Fly.io):**
1. Deploy the `backend/Dockerfile`. The backend image is a multi-stage Docker build optimized for production.
2. Configure all environment variables listed in Section 4.
3. Configure a Release Command (or pre-deploy script) to run `alembic upgrade head`.
4. Ensure the port exposed matches your platform (e.g., `8000`).

**PostgreSQL Requirements:**
The database must be accessible to the backend container over the network. Using managed databases (like Neon or AWS RDS) is highly recommended.

**S3-Compatible Storage Configuration:**
Configure `STORAGE_PROVIDER=s3` and pass valid S3 credentials to allow images to survive container restarts and scale horizontally.

## 8. ML Model Architecture & Pipeline
The underlying ML inference pipeline is powered by a PyTorch **MobileNetV3 Small** architecture.
- **Image Size**: 64x64 RGB
- **Classes**: 10 land-cover classes (Annual Crop, Forest, Herbaceous Vegetation, Highway, Industrial, Pasture, Permanent Crop, Residential, River, SeaLake).
- **Execution**: The model is configured to run inference exclusively on the **CPU** for scalable server-side inference without requiring expensive GPU container instances.

The production ML model checkpoint (`ml/models/land_cover/v1/best_model.pt`) is baked directly into the backend Docker image during the build process.

## 9. Evaluation Metrics
The Phase 5 ML model was evaluated on an isolated held-out test split of the EuroSAT dataset, achieving the following real metrics:
- **Test Accuracy**: 94.57%
- **Macro Precision**: 94.45%
- **Macro Recall**: 94.33%
- **Macro F1 Score**: 94.37%
- **Weighted F1 Score**: 94.55%

## 10. Dataset Provenance and Citation
The model was trained exclusively on the **EuroSAT** dataset (RGB version).
- **Dataset Size**: 27,000 labeled and geo-referenced Sentinel-2 satellite images.
- **License**: The EuroSAT dataset is publicly available and permitted for academic/research purposes.
- **Reference**:
  - Helber, P., Bischke, B., Dengel, A., & Borth, D. (2019). *EuroSAT: A Novel Dataset and Deep Learning Benchmark for Land Use and Land Cover Classification*. IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing.
  - Helber, P., Bischke, B., Dengel, A., & Borth, D. (2018). *Introducing EuroSAT: A Novel Dataset and Deep Learning Benchmark for Land Use and Land Cover Classification*. IGARSS 2018.

## 11. Health & Readiness Endpoints
The application exposes the following endpoints for orchestration and monitoring:
- `GET /api/health`: Provides a basic liveness check (HTTP 200) indicating the FastAPI server is running.
- `GET /api/ready`: Provides a readiness check. It verifies PostgreSQL database connectivity and ensures the ML model is successfully loaded in memory. If any dependency fails, it returns HTTP 503 without leaking details.

## 12. Production Security Considerations
- **Environment Driven Secrets**: The repository contains no real credentials. Never commit real keys. `config.py` explicitly rejects default passwords in `production`.
- **CORS Hardening**: `CORS_ORIGINS` precisely matches your frontend deployment domain to prevent Cross-Site Request Forgery and unauthorized API usage.
- **Non-Root Containers**: The provided `backend/Dockerfile` creates a non-root `appuser` user to execute the application, minimizing security risks inside the container footprint.
- **Protected Endpoints**: Real ML inference is strictly authenticated and validated by image ownership.
- **Error Handling**: Stack traces are caught in production mode, masking internal infrastructure, database architectures, and paths.

## 13. Troubleshooting
- **Database Connection Failed**: Ensure `DATABASE_URL` is correctly formatted. If connecting to a managed host, verify IP whitelisting or VPC peering.
- **Model Fails to Load**: Verify `ML_MODEL_PATH` points correctly to the checkpoint embedded in the Docker image. If missing, startup will intentionally fail in `production` environment.
- **Frontend Fails to Connect**: Verify `VITE_API_BASE_URL` was injected at **build time**, and ensure `CORS_ORIGINS` includes the exact URL with protocol/scheme intact.
