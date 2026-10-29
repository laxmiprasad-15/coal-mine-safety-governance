# REST API Documentation

**Base URL:** `http://localhost:8000/api/v1`  
**Interactive Swagger Docs:** `http://localhost:8000/docs`  
**ReDoc Specification:** `http://localhost:8000/redoc`  

---

## 1. Authentication (`/auth`)

### `POST /auth/login`
Authenticates a user and issues a Bearer JWT token.
- **Request Body (JSON):**
  ```json
  {
    "email": "safety@coalmine.gov",
    "password": "Safety@123"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": 2,
      "email": "safety@coalmine.gov",
      "full_name": "Vikram Rathore",
      "role": "Safety Officer",
      "department": "Safety Operations"
    }
  }
  ```

### `GET /auth/me`
Fetches current authenticated profile.
- **Headers:** `Authorization: Bearer <token>`
- **Response (200 OK):** User object.

---

## 2. Dashboard (`/dashboard`)

### `GET /dashboard/summary`
Returns top-level KPIs, risk distribution counts, recent detections, and sensor anomalies.
- **Headers:** `Authorization: Bearer <token>`
- **Response (200 OK):**
  ```json
  {
    "kpis": {
      "open_cases": 19,
      "total_cases": 32,
      "completion_rate": 37.5,
      "critical_alerts_today": 32,
      "ppe_violations_today": 29,
      "high_risk_zones": 3,
      "overdue_actions": 1,
      "equipment_alerts": 1,
      "worker_health_alerts": 1
    },
    "risk_distribution": { "Low": 3, "Medium": 2, "High": 2, "Critical": 1 },
    "recent_detections": [...],
    "recent_anomalies": [...],
    "zones_mini": [...]
  }
  ```

---

## 3. Digital Twin (`/digital-twin`)

### `GET /digital-twin/overview?replay_offset_minutes=0`
Provides real-time topological mine zone data, hazard color codes, active worker counts, and sensor summaries.
- **Response (200 OK):** Array of zones with coordinates and live hazard levels.

### `GET /digital-twin/zone-panel/{zone_id}`
Returns granular telemetry, camera streams, recent violations, and active compliance cases for a selected zone.

---

## 4. Computer Vision & PPE (`/ppe`)

### `POST /ppe/detect`
Uploads an image or webcam capture for YOLOv8 PPE analysis.
- **Request:** `multipart/form-data` with `file` (image) and `zone_id` (integer).
- **Response (200 OK):**
  ```json
  {
    "detection_id": 56,
    "annotated_image_url": "/uploads/ppe/detected_173000.jpg",
    "detected_classes": ["person", "gloves"],
    "violations": ["Missing Hardhat / Helmet", "Missing Safety Vest"],
    "confidence": 0.93,
    "case_created": true,
    "case_id": 33
  }
  ```

### `GET /ppe/detections`
Lists historical detection events with status filters (`Pending Confirmation`, `Case Created`, `Dismissed`).

### `PATCH /ppe/detections/{id}/status`
Allows safety personnel to manually confirm or dismiss an AI PPE detection.

---

## 5. IoT Sensors & Environmental Telemetry (`/sensors`)

### `GET /sensors/`
Lists all deployed environmental sensors across zones with current readings and DGMS thresholds.

### `POST /sensors/csv-upload`
Uploads a batch CSV sensor reading file for ingestion and historical analysis.

### `POST /sensors/simulate-pulse`
Triggers an immediate live synthetic sensor broadcast across all mine zones to simulate real-time operations.

---

## 6. Predictive Risk & Forecasting (`/risk`)

### `GET /risk/predict?zone_id=1`
Calculates instant Random Forest risk score (0-100) and classification (`Low`, `Medium`, `High`, `Critical`) for a given zone.

### `GET /risk/forecast`
Generates **Next Shift Risk Forecast** across all mine districts with Explainable AI (XAI) feature attribution.

---

## 7. Compliance Cases (`/compliance`)

### `GET /compliance/cases`
Query compliance cases with filters: `status`, `risk_level`, `category`, `zone_id`.

### `POST /compliance/cases`
Creates a manual or automated compliance case.

### `PUT /compliance/cases/{id}`
Updates case status, assignee, or closure notes.

---

## 8. Corrective Action Tracking (`/actions`)

### `GET /actions/`
Lists assigned remedial tasks with deadline countdowns and progress badges.

### `PUT /actions/{id}`
Transitions action states: `Assigned` $\rightarrow$ `In Progress` $\rightarrow$ `Submitted for Verification` $\rightarrow$ `Verified` $\rightarrow$ `Closed`.

---

## 9. Reports (`/reports`)

### `POST /reports/generate`
Generates a downloadable PDF or Excel report:
- `report_type`: `Daily Safety Report`, `Weekly Compliance Report`, `PPE Violations Report`, `DGMS Statutory Audit Report`.
- `format`: `pdf` or `excel`.

### `GET /reports/download/{filename}`
Streams the compiled document file to client.

---

## 10. Audit Trail (`/audit`)

### `GET /audit/logs`
Returns chronological, immutable event logs with SHA-256 integrity tokens.
