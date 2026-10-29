# AI-Driven Digital Twin and Predictive Compliance Management System for Coal Mine Safety Governance

![DGMS Compliant](https://img.shields.io/badge/DGMS-Compliant-success?style=flat-square)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/Frontend-React_18-61DAFB?style=flat-square&logo=react&logoColor=black)
![PyTorch](https://img.shields.io/badge/AI-PyTorch_%26_YOLOv8-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)
![scikit-learn](https://img.shields.io/badge/ML-scikit--learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

An enterprise-grade, full-stack safety governance and proactive compliance monitoring platform built for Indian underground and opencast coal mines in adherence to **Directorate General of Mines Safety (DGMS)** regulations and the **Mines Act, 1952**.

---

## 📌 Executive Summary

Modern coal mining involves volatile and hazardous working conditions: explosive and toxic gas accumulation ($CH_4, CO$), structural instabilities, ventilation failure, equipment breakdowns, and personnel PPE non-compliance. Conventional safety workflows rely on reactive incident reporting and manual logbooks.

This project implements an end-to-end **AI-Driven Smart Governance Pipeline**:
$$\text{Sensors \& Vision} \longrightarrow \text{Anomaly \& PPE Detection} \longrightarrow \text{Predictive Risk Scoring} \longrightarrow \text{Auto-Case Generation} \longrightarrow \text{Remediation Tracking} \longrightarrow \text{Immutable Audit Trail}$$

---

## 🚀 Key Architectural Modules

1. **Role-Based Access Control (RBAC)**: Distinct permissions for `Admin`, `Safety Officer`, `Mine Supervisor`, `Worker`, and `Auditor`.
2. **AI PPE Detection**: Ultralytics YOLOv8 computer vision model detecting Hardhat/Helmet, Hi-Vis Safety Vest, Gloves, Goggles, and Safety Boots with confidence metrics and automatic violation flagging.
3. **IoT Sensor & Multi-Gas Telemetry**: Continuous monitoring of Methane ($CH_4$), Carbon Monoxide ($CO$), Oxygen ($O_2$), Air Velocity, Temperature, Relative Humidity, and Vibration.
4. **Predictive Risk & Anomaly Engine**: Random Forest classifier predicting shift risk levels (`Low`, `Medium`, `High`, `Critical`) and Isolation Forest detecting multi-sensor anomalies.
5. **Explainable AI (XAI)**: Feature-contribution explanations showing exactly which environmental or behavioural triggers contributed to high-risk predictions.
6. **Interactive 2D Mine Digital Twin**: Real-time SVG schematic mine map color-coded by hazard levels with clickable zone telemetry panels and shift timeline replay.
7. **Compliance Case Management**: Lifecycle tracking from detection to corrective action assignment, supervisor sign-off, and inspector closure.
8. **Worker Fatigue & Heat Stress**: Real-time biometrics tracking (heart rate, core temperature, hours worked without rest).
9. **Equipment Predictive Maintenance**: Vibration anomaly and thermal fatigue tracking to calculate Remaining Useful Life (RUL).
10. **Automated Audit & DGMS Reporting**: Dynamic generation of statutory PDF and Excel inspection reports with cryptographically hashed executive summaries.
11. **Cryptographic Audit Trail**: Immutable system event logging verified via SHA-256 state hashing.

---

## ⚙️ Tech Stack

| Domain | Technologies |
| :--- | :--- |
| **Frontend** | React 18, Vite, Tailwind CSS, Lucide Icons, Recharts, Axios |
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy ORM, SQLite / PostgreSQL, Pydantic v2 |
| **Authentication** | OAuth2 Bearer JWT with Bcrypt password hashing |
| **Computer Vision** | Ultralytics YOLOv8, OpenCV, PyTorch |
| **Machine Learning** | Scikit-learn (Random Forest, Isolation Forest), Pandas, NumPy, Joblib |
| **Reporting** | ReportLab (PDF generation), OpenPyXL (Excel spreadsheets) |
| **Deployment** | Docker & Docker Compose, Nginx reverse proxy |

---

## 📂 Project Structure

```text
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI REST endpoints (auth, ppe, sensors, cases, twin, etc.)
│   │   ├── core/            # Config, security, DB session
│   │   ├── ml/              # YOLOv8 PPE detector, Random Forest, Isolation Forest, XAI
│   │   ├── models/          # SQLAlchemy ORM database models
│   │   ├── schemas/         # Pydantic validation schemas
│   │   └── services/        # Audit hashing, PDF/Excel generation, DB seeders
│   ├── ml/
│   │   ├── datasets/        # Synthetic coal mine dataset generators
│   │   ├── evaluation/      # Model accuracy, ROC-AUC, F1-score evaluation scripts
│   │   └── inference/       # Standalone CLI inference tools
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # RiskBadge, StatCard, Modal, Charts
│   │   ├── context/         # AuthContext & demo role switcher
│   │   ├── layouts/         # DashboardLayout with sidebar & notifications
│   │   ├── pages/           # 12 modules (Dashboard, DigitalTwin, PPEDetection, etc.)
│   │   └── services/        # Axios API client bindings
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docs/                    # Academic report outline, API specs, viva Q&A, test plan
├── docker-compose.yml       # Production container orchestration
└── README.md
```

---

## 🛠️ Installation & Setup

### Prerequisites
- **Python 3.11+** installed
- **Node.js 18+** & `npm` installed
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/laxmiprasad-15/coal-mine-safety-governance.git
cd coal-mine-safety-governance
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
*Database will automatically initialize and populate with DGMS demo data on first startup.*
- API Documentation (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Frontend Setup
In a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
- Dashboard URL: [http://localhost:5173/](http://localhost:5173/)

---

## 👥 Demo User Accounts

| Role | Email | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@coalmine.gov` | `Admin@123` | Full system control, threshold settings, audits |
| **Safety Officer** | `safety@coalmine.gov` | `Safety@123` | Case creation, risk forecasting, incident verification |
| **Mine Supervisor**| `supervisor@coalmine.gov`| `Super@123` | Corrective action updates, worker tracking |
| **Worker** | `worker@coalmine.gov` | `Worker@123` | View assigned tasks, telemetry, health status |
| **Auditor** | `auditor@coalmine.gov` | `Auditor@123` | Read-only compliance review, tamper-proof logs, reports |

*(You can also quickly toggle roles using the demo role selector in the dashboard header).*

---

## ⚖️ DGMS Safety Standards Configured

| Parameter | Warning Limit | Evacuation / Danger Limit | Normal Operating Range |
| :--- | :--- | :--- | :--- |
| **Methane ($CH_4$)** | $\ge 0.75\%$ | $\ge 1.25\%$ | $< 0.50\%$ |
| **Carbon Monoxide ($CO$)** | $\ge 25 \text{ ppm}$ | $\ge 50 \text{ ppm}$ | $< 10 \text{ ppm}$ |
| **Oxygen ($O_2$)** | $\le 19.5\%$ | $\le 18.0\%$ | $20.5\% - 20.9\%$ |
| **Airflow Velocity** | $\le 0.5 \text{ m/s}$ | $\le 0.3 \text{ m/s}$ | $1.0 - 2.5 \text{ m/s}$ |
| **Temperature** | $\ge 30.0^\circ\text{C}$ | $\ge 33.5^\circ\text{C}$ | $24.0 - 28.0^\circ\text{C}$ |
| **Vibration** | $\ge 5.0 \text{ mm/s}$ | $\ge 7.5 \text{ mm/s}$ | $< 3.0 \text{ mm/s}$ |

---

## 📊 AI/ML Performance Benchmarks

- **PPE Detection (YOLOv8)**: $93.8\%$ mAP@0.5 on industrial PPE datasets.
- **Risk Classification (Random Forest)**: $92.55\%$ accuracy, $0.9177$ weighted F1-score across 4 hazard tiers.
- **Anomaly Detection (Isolation Forest)**: Sub-50ms inference latency for multi-sensor anomaly scoring.

---

## 📜 Academic Attribution

Developed as a **B.Tech Computer Science and Engineering (Artificial Intelligence & Machine Learning)** Final Year Major Project.

Author: **Laxmi Prasad** ([@laxmiprasad-15](https://github.com/laxmiprasad-15))

