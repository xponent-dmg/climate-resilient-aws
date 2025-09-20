# Climate-Resilient Healthcare System MVP

## Complete System Overview

The Climate-Resilient Healthcare System MVP is an AI-driven, cloud-native platform that predicts and responds to climate-related health risks across India. It integrates climate, air quality, and health data to forecast multiple risks (heat stress, floods, respiratory issues, vector-borne diseases), send alerts, and optimize healthcare resources.

### Key Features

- **Multi-risk Prediction**: Monitors heat stress, floods, respiratory issues, vector-borne diseases
- **ML-Powered Capacity Planning**: Predicts hospital bed and staff needs based on air quality and climate data
- **Role-Based Access**: Admin, Clinician, and Analyst views
- **Interactive Dashboard**: Risk scores, charts, maps, capacity management, and health tips
- **Real-time Alerts**: Notifications when risk thresholds are exceeded
- **Resource Optimization**: Suggests hospital capacity adjustments based on predicted risks

## Tech Stack

- **Backend**: Python (pandas, sqlalchemy, xgboost, scikit-learn, FastAPI)
- **ML**: XGBoost models for risk classification and capacity prediction
- **Frontend**: React/Next.js (TypeScript), Chart.js, Leaflet maps
- **Database**: SQLite (local), RDS PostgreSQL (AWS)
- **AWS Services**: EC2, S3, RDS, API Gateway, Lambda, SageMaker, IAM, Secrets Manager, SNS, Glue

## Local Development

### Frontend (Day 1 – Sept 17, 2025)

- Stack: Next.js (TypeScript, App Router, `src/`), Tailwind CSS, Chart.js via `react-chartjs-2`, axios
- Location: `frontend/`
- Features:
  - Login with mock credentials and RBAC (Admin, Clinician)
  - Dashboard shows region (Delhi, India), risk score, and temperature trend line chart
  - Admin additionally sees resource suggestion card
  - Mobile-responsive, vibe-driven UI with Tailwind
  - Commented axios snippet prepared for AWS API Gateway `/predict`

#### Run locally

```bash
cd frontend
npm install
npm run dev
# open http://localhost:3000
```

#### Demo credentials

- Admin: `admin` / `admin123`
- Clinician: `clinician` / `clin123`
- Analyst: `analyst` / `anal123`

#### File highlights

- `frontend/src/pages/login.tsx`: login form and session init
- `frontend/src/pages/index.tsx`: protected dashboard route
- `frontend/src/context/AuthContext.tsx`: localStorage-backed mock session and RBAC
- `frontend/src/components/Dashboard.tsx`: header, risk, chart, suggestion (admin only)
- `frontend/src/components/TemperatureChart.tsx`: Chart.js line chart
- `frontend/src/data/mockUsers.ts`, `frontend/src/data/mockData.ts`: mock users and climate data

#### AWS prep (Day 5)

- Swap mock auth for IAM-backed requests to API Gateway using axios with SigV4 (e.g., interceptor or presigned)
- Endpoint: `/predict` (POST). Request: `{ region: "Delhi, India" }`
- Secrets: move creds/config to AWS Secrets Manager or environment variables

#### MCP prompt used

Generate mobile-responsive React/Next.js dashboard with mock authentication (login page, RBAC for Admin/Clinician) and Chart.js for climate trends, compliant with AWS best practices.

#### Day 5 plan (IAM integration)

- Add AWS SigV4 axios interceptor or use presigned requests with temporary creds
- Store secrets in AWS Secrets Manager; load via backend or environment
- Replace mock call with POST `/predict` to API Gateway (IAM auth)
- Handle 401/403 with sign-out and re-auth flow

### Backend (Day 2 – Local Ingestion, ETL, API, Alerts)

- Location: `backend/`
- Tech: Python (pandas, sqlalchemy, requests), SQLite (mock RDS)
- Flow: ingest CSV → ETL (clean + mock health) → API handler (risk + alert)

Run locally:
```bash
cd backend
# create venv and install deps (already done if you ran the task)
python -m venv .venv
./.venv/Scripts/pip install -U pip pandas sqlalchemy requests scikit-learn xgboost
# run pipeline
./.venv/Scripts/python ingest.py
./.venv/Scripts/python trigger_etl.py
./.venv/Scripts/python api.py
```

Expected API output (example):
```json
{"statusCode":200,"body":"{\"risk\":0.67,\"temps\":[{\"label\":\"Day 1\",\"value\":35.0},{\"label\":\"Day 2\",\"value\":34.0}],\"region\":\"Delhi\"}"}
```

Files:
- `backend/ingest.py`: copy CSV from `data/` to `raw/`
- `backend/etl.py`: clean, feature engineer, mock health, write `local.db`
- `backend/trigger_etl.py`: simple trigger wrapper
- `backend/api.py`: mock Lambda-style handler with risk and alert print

MCP prompt used:
Generate Python scripts for local data ingestion, ETL with mock health generation, mock API with alerts, using pandas/sqlalchemy for SQLite, compliant with AWS best practices for future Lambda/Glue deployment.

### End-to-End (Local Integration)

- Backend: `cd backend && ./.venv/Scripts/python server.py` (serves on http://localhost:8000)
- Frontend: `cd frontend && npm run dev` (open http://localhost:3000)
- Config: `NEXT_PUBLIC_API_BASE` defaults to `http://localhost:8000`. Create `frontend/.env.local` to override.
- In the dashboard Overview: use the Mock Predict and Mock Report buttons to call the backend.

### Frontend Enhancements (Connected to Local Backend)

- Live risk fetch from backend `/predict` and CSV reports from `/reports`
- Admin: Capacity manager (beds/staff) with readiness bar and suggestions
- Tips & Badges: dynamic health tips and fun badges based on risk
- Family & Community: guidance for households and community actions
- Risk Calendar: next 7 days colored blocks
- Team Notes: chat-like notes for alerts
- Readiness & Share: checklist and share button
- Feedback & Help: quick feedback form and simple guide

Test results: Risk predicted and capacity updated—vibes are high!

MCP Knowledge Server prompt used:
Generate ways to connect React frontend to local Python backend with fun features like risk prediction and hospital capacity updates, plus more ideas for health tips and community help, all in a clean white professional style.

### Multi-Risk ML System

- **Data Sources**: 
  - Air quality data (`backend/data/airquality.csv`) - SO2, NO2, PM10, PM2.5 across Indian cities
  - Temperature data (`backend/data/Mean_Seasonal_Temp_IMD-1901_to_2019_0.csv`) - Seasonal temperature trends
  - Dengue data (`backend/data/dengue.csv`) - Vector-borne disease cases by state

- **ML Models**:
  - **Risk Classification**: XGBoost models for predicting high-risk conditions (heat, flood, respiratory, vector-borne, drought, storm, air pollution)
  - **Capacity Prediction**: XGBoost regression models for hospital beds and staff needs based on air quality and seasonal factors

- **API Endpoints**:
  - `/predict`: Returns multi-risk scores and ML predictions
  - `/capacity`: Gets/sets current capacity values
  - `/capacity/predict`: Predicts capacity needs based on environmental factors
  - `/capacity/train`: Trains capacity models using air quality data
  - `/reports`: Generates CSV reports of risk data

- **Frontend Integration**:
  - Multi-risk cards showing heat, flood, respiratory, vector-borne risks
  - ML Outlook showing probability of high-risk conditions
  - Capacity Predictor for estimating resource needs
  - Dynamic tips and guidance based on risk levels

## Running the Complete System

1. Start the backend server:
```bash
cd backend
./.venv/Scripts/python server.py
```

2. Start the frontend:
```bash
cd frontend
npm run dev
```

3. Open http://localhost:3000 and log in with demo credentials
4. Train the capacity model:
   - Go to Capacity (Admin only)
   - Click "Train Model" in the Capacity Predictor
   - Use the predictor to estimate needs based on air quality and season

5. Explore the dashboard:
   - Click "Refresh Data" to fetch latest risks and ML predictions
   - Try different sections in the sidebar
   - Test role-specific features by logging in as different users

## AWS Deployment (Day 4-5)

Prepared for deployment to AWS with:
- S3 for raw data storage
- RDS PostgreSQL for processed data
- Lambda for API handlers
- API Gateway for endpoints
- SageMaker for ML model hosting
- SNS for alerts
- IAM and Secrets Manager for security

## Built with 💪 by [Your Name] in one week, September 2025. Vibe on!