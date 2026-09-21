# Cloud-Based Satellite Image Analysis and Land Use/Land Cover Classification System

## 1. Project Overview
This application provides a cloud-based platform for satellite imagery analysis. It enables users to upload satellite images, process them through a custom machine learning pipeline to classify land-use/land-cover categories, and persistently view the results in a web-based dashboard. The system is designed with a fully decoupled React frontend and FastAPI backend, utilizing a production-ready containerized architecture.

## 2. Key Features
- **Authentication**: JWT authentication and secure bcrypt password hashing.
- **Image Management**: Image upload, ownership/access control, and strict MIME/content validation.
- **Storage Abstraction**: Local storage and S3-compatible cloud storage support.
- **Machine Learning Analysis**: Real MobileNetV3 inference providing class probabilities, predicted class, and confidence scoring.
- **Persistent Analysis History**: PostgreSQL database for storing user images and analysis results.
- **Production Configuration**: Docker-based deployment with health and readiness endpoints, strict CORS configuration, and environment-driven secrets.
- **Quality Assurance**: Automated test suite and CI/CD workflow configuration.

## 3. System Architecture

```text
       User
         |
         v
  React Frontend
 (Vite/TypeScript)
         |
         | REST API
         v
  FastAPI Backend
         |
         +---- Authentication (JWT/bcrypt)
         |
         +---- Image Management
         |
         +---- Analysis Service
         |        |
         |        v
         |    MobileNetV3 (PyTorch)
         |
         +---- Storage Service
         |       |
         |       +---- Local
         |       +---- S3
         |
         +---- PostgreSQL
```

## 4. Machine Learning Pipeline
The ML pipeline is based on the EuroSAT RGB dataset.

- **Dataset**: EuroSAT RGB
- **Dataset Size**: 27,000 images
- **Classes**: 10
  - AnnualCrop
  - Forest
  - HerbaceousVegetation
  - Highway
  - Industrial
  - Pasture
  - PermanentCrop
  - Residential
  - River
  - SeaLake
- **Split**: 70% training, 15% validation, 15% testing
- **Seed**: 42
- **Model**: MobileNetV3 Small
- **Input**: 64x64 RGB
- **Training**: 10 epochs
- **Optimizer**: Adam
- **Learning Rate**: 0.001
- **Loss**: CrossEntropyLoss
- **Batch Size**: 32

**Actual Evaluation Metrics (Phase 5 Experiment)**
These are the evaluation results from the completed Phase 5 experiment on the isolated 15% test split.
- **Test Accuracy**: 94.5679%
- **Macro Precision**: 94.4510%
- **Macro Recall**: 94.3289%
- **Macro F1**: 94.3681%
- **Weighted F1**: 94.5542%

## 5. ML Inference Pipeline
The inference pipeline executes seamlessly at runtime:
Image upload -> validation -> preprocessing -> MobileNetV3 model -> class probabilities -> predicted class -> confidence -> database persistence -> frontend result display.

Inference uses the pre-trained CPU-optimized checkpoint:
`ml/models/land_cover/v1/best_model.pt`

## 6. Dataset Provenance
The model was trained exclusively on the **EuroSAT** dataset (RGB version).
- Helber, P., Bischke, B., Dengel, A., & Borth, D. (2019). *EuroSAT: A Novel Dataset and Deep Learning Benchmark for Land Use and Land Cover Classification*. IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing.
- Helber, P., Bischke, B., Dengel, A., & Borth, D. (2018). *Introducing EuroSAT: A Novel Dataset and Deep Learning Benchmark for Land Use and Land Cover Classification*. IGARSS 2018.

## 7. API Documentation

- **Health Endpoints**
  - `GET /api/health`: Unauthenticated. Basic liveness check.
  - `GET /api/ready`: Unauthenticated. Verifies PostgreSQL connectivity and ML model availability.
- **Authentication Endpoints**
  - `POST /api/auth/register`: Unauthenticated. Registers a new user.
  - `POST /api/auth/login`: Unauthenticated. Returns a JWT access token.
- **Image Endpoints**
  - `POST /api/images/`: Authenticated. Uploads a satellite image.
  - `GET /api/images/`: Authenticated. Lists the user's images.
  - `GET /api/images/{id}`: Authenticated. Retrieves specific image metadata.
  - `GET /api/images/{id}/content`: Authenticated. Retrieves the raw image file.
- **Analysis Endpoints**
  - `POST /api/analyses/`: Authenticated. Triggers the ML pipeline for an uploaded image.
  - `GET /api/analyses/`: Authenticated. Lists the user's analysis history.
  - `GET /api/analyses/{id}`: Authenticated. Retrieves specific analysis results and probability scores.

## 8. Environment Configuration
The backend strictly relies on environment variables for production. An example configuration is provided in `.env.example`.
- **Database**: `DATABASE_URL` (Required in production)
- **JWT**: `JWT_SECRET_KEY` (Must be >= 32 chars in production), `ACCESS_TOKEN_EXPIRE_MINUTES`, `JWT_ALGORITHM`
- **CORS**: `CORS_ORIGINS` (e.g., `["https://your-domain.com"]`)
- **Storage**: `STORAGE_PROVIDER` (`local` or `s3`)
- **S3 (If used)**: `S3_ENDPOINT_URL`, `S3_REGION`, `S3_BUCKET_NAME`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`
- **ML**: `ML_MODEL_PATH`, `ML_MODEL_VERSION`, `ML_DEVICE`

> **Note**: `.env` files must NEVER be committed to version control. Real secrets should be securely injected via your deployment environment.

## 9. Local Development
To run the full stack locally:
```bash
docker compose build
docker compose up -d
docker compose exec backend alembic upgrade head
```
This mirrors the production Docker configuration. The frontend is accessible at `http://localhost:5173` and the backend API at `http://localhost:8000`.

To run backend tests locally:
```bash
docker compose exec backend sh -c "PYTHONPATH=. pytest -q"
```

## 10. Testing
The application features a comprehensive automated test suite.
**Current Test Result:** 38 passed

Test coverage includes:
- Health and readiness endpoints
- Authentication and authorization
- Image management and file validation
- Storage (local and S3 abstraction)
- Analysis/ML inference
- CORS headers

## 11. Security
- JWT authentication and bcrypt password hashing.
- Ownership checks on all user-data endpoints.
- Strict input, MIME type, and file size validation.
- Environment-based secrets with production validation (rejecting weak secrets).
- Explicit CORS configuration.
- Non-root Docker backend container execution.
- Protected API routes preventing unauthenticated access.

## 12. Docker / Deployment
The repository features a deployment-ready Docker architecture containing:
- **Frontend Container**: Multi-stage build resulting in a static Nginx server.
- **Backend Container**: Multi-stage build running a FastAPI server as a non-root `appuser`. The ML model is baked directly into the image.
- **PostgreSQL Container**: Application database.
- **Healthchecks**: Built-in Docker healthchecks for robust orchestration.
- **Environment-Driven Configuration**: No hardcoded credentials.

## 13. Project Structure
```text
satellite-image-analysis/
├── backend/
│   ├── alembic/
│   ├── app/
│   ├── storage/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   ├── Dockerfile
│   └── package.json
├── ml/
│   ├── artifacts/
│   ├── evaluation/
│   ├── inference/
│   ├── models/
│   ├── preprocessing/
│   ├── training/
│   └── config.py
├── .github/
│   └── workflows/
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## 14. Screenshots / Demo Readiness
The frontend provides a fully responsive UI with the following demonstrable screens:
- **Login/Register**: Secure user authentication flow.
- **Dashboard**: Overview of user activity and recent analyses.
- **Image Upload**: Interface for uploading and validating satellite imagery.
- **Image History**: Gallery of previously uploaded images.
- **Analysis Details**: Detailed view of ML inference results, including probability bars for all 10 land-cover classes.

## 15. Github Quality
- The repository `.gitignore` strictly excludes `.env` files, node modules, Python caches, temporary databases, and runtime uploads.
- No model checkpoints are ignored if they are required for production inference.

## 16. CI/CD Review
- `.github/workflows/main.yml`: Triggered on push to `main` and PRs. Contains automated CI jobs for backend tests and frontend builds to ensure integration health.

## 17. License / Provenance Check
- The ML dataset uses the EuroSAT RGB dataset (Open access / Academic usage).
- The repository does not currently contain a dedicated `LICENSE` file.
