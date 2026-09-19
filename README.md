# Satellite Image Analysis and Land Use/Land Cover Classification System

## 1. Project Overview
This application provides a cloud-based platform for satellite imagery analysis. It aims to allow authenticated users to upload satellite imagery, process it through an ML pipeline to classify land-use/land-cover categories, and visualize the results.

## 2. Current Scope
This repository currently implements **Phase 5**: the complete Machine Learning Pipeline.
It establishes the backend API (FastAPI), frontend application (React + Vite), database configuration (PostgreSQL), Docker setup, Authentication, Local/Cloud Storage Abstraction, and the EuroSAT Land Cover Classification ML pipeline.

## 3. Architecture
```text
                    "O"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?
                    ",        User          ",
                    """?"?"?"?"?"?"?"?"?"?""?"?"?"?"?"?"?"?"?"?"?"~
                               ",
                               -
                    "O"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?
                    ", React + TypeScript   ",
                    ", Frontend             ",
                    """?"?"?"?"?"?"?"?"?"?""?"?"?"?"?"?"?"?"?"?"?"~
                               ", REST API
                               -
                    "O"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?
                    ", FastAPI Backend      ",
                    ", Python               ",
                    """?"?"?"?"?"?"?""?"?"?"?"?"?"?""?"?"?"?"?"?"~
                            ",       ",
                  "O"?"?"?"?"?"?"?"?"?"~       """?"?"?"?"?"?"?"?"?"?"?
                  -                            -
        "O"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?          "O"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?
        ", PostgreSQL       ",          ", ML Pipeline      ",
        ", Application Data ",          ", PyTorch / EuroSAT",
        """?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"~          """?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"?"~
```

## 4. Machine Learning & Dataset Provenance
**Dataset Used**: [EuroSAT RGB](https://github.com/phelber/EuroSAT) via Hugging Face (`timm/eurosat-rgb`).
- **Description**: 27,000 labeled RGB images of 10 land cover classes (AnnualCrop, Forest, HerbaceousVegetation, Highway, Industrial, Pasture, PermanentCrop, Residential, River, SeaLake).
- **Authors**: Patrick Helber, Benjamin Bischke, Andreas Dengel, Damian Borth.
- **License**: MIT License. The underlying imagery data is provided by the European Space Agency (ESA) Sentinel-2 satellite under the Copernicus program open access terms.
- **Citation**: 
  > Helber, P., Bischke, B., Dengel, A., & Borth, D. (2019). "Eurosat: A novel dataset and deep learning benchmark for land use and land cover classification." *IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing*.
- **Splits**: The project uses a custom, deterministic, stratified 70/15/15 split derived explicitly from the 27,000 local image set.

## 5. Technology Stack
- **Frontend:** React, TypeScript, Vite, React Router, Tailwind CSS, Axios, Lucide React
- **Backend:** Python, FastAPI, Uvicorn, Pydantic, SQLAlchemy 2.x
- **ML/AI**: PyTorch, torchvision, Pillow, scikit-learn
- **Database:** PostgreSQL, Alembic
- **Infrastructure:** Docker, Docker Compose

## 6. Repository Structure
- `/frontend`: React application using Vite.
- `/backend`: FastAPI backend application, tests, and database migrations.
- `/ml`: Machine Learning subsystem including dataset downloaders, training scripts, testing, and fully trained models.
- `/.github`: GitHub actions and workflows.
- `docker-compose.yml`: Multi-container orchestration.

## 7. Local Development
**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Backend:**
```bash
cd backend
python -m venv venv
# activate venv
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 8. Environment Variables
Copy `.env.example` to `.env` in the root directory. It contains necessary placeholders for database URL, secrets, and API keys required for development.

## 9. Docker
To run the full stack (Frontend, Backend, PostgreSQL) via Docker Compose:
```bash
docker compose up --build
```
This will start the UI on port 5173, the API on port 8000, and PostgreSQL on port 5432.

## 10. Testing
**Backend & ML Tests:**
```bash
cd backend
pytest tests/
```

## 11. Roadmap Status
- **Phase 1-4**: Architecture, Auth, Database, Storage (Complete)
- **Phase 5**: ML Dataset + Training Pipeline (Complete)
- **Phase 6**: Prediction / Inference API (Next)
