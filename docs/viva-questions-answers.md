# Final Year Viva Voce Preparation Guide (35 Q&A)

**Project:** AI-Driven Digital Twin and Predictive Compliance Management System for Coal Mine Safety Governance  
**Discipline:** B.Tech CSE (Artificial Intelligence & Machine Learning)  

---

## Category 1: Project Overview & Motivation

### Q1: What is the core objective of your project?
**Answer:** The objective is to build a unified smart governance platform that converts fragmented coal mine monitoring data (CCTV feeds and IoT telemetry) into proactive, traceable compliance intelligence in adherence to DGMS safety standards. Unlike traditional monitoring that merely triggers isolated alarms, our system executes an automated closed-loop remediation pipeline: detection $\rightarrow$ risk scoring $\rightarrow$ compliance case generation $\rightarrow$ corrective action assignment $\rightarrow$ verification $\rightarrow$ immutable audit logging.

### Q2: Why is this project significant for Indian coal mines?
**Answer:** Indian coal mines operate under strict statutory guidelines mandated by the Directorate General of Mines Safety (DGMS) and the Coal Mines Regulations (CMR) 2017. Historically, accidents in mines occur due to delayed intervention, lack of personal protective equipment (PPE), and undetectable gas accumulation. Our system digitizes inspections, reduces incident response times from hours to seconds, and eliminates manual paperwork falsification through cryptographic audit trails.

### Q3: Who are the target users of this system?
**Answer:** The system implements Role-Based Access Control (RBAC) with 5 user personas:
1. **Admin:** System configuration, threshold settings, and user access.
2. **Safety Officer:** Case triage, risk forecasting, and inspection verification.
3. **Mine Supervisor:** Corrective action resolution and worker duty management.
4. **Worker:** Personal health telemetry and assigned safety tasks.
5. **Auditor / DGMS Inspector:** Read-only compliance reviews, tamper logs, and official reports.

---

## Category 2: Computer Vision & AI Models

### Q4: Why did you choose YOLOv8 for PPE detection?
**Answer:** YOLOv8 (You Only Look Once v8) provides an anchor-free single-stage detection architecture that balances inference speed and mean Average Precision (mAP). In mine surveillance cameras, workers appear at varying scales under harsh lighting. YOLOv8 features a modified backbone and C2f modules that deliver high feature extraction efficiency, achieving >93% mAP@0.5 with sub-30ms inference per frame on GPU.

### Q5: What PPE classes are detected, and what constitutes a violation?
**Answer:** The model detects hardhats/helmets, high-visibility vests, safety gloves, goggles, and boots. Under DGMS regulations, helmets and high-visibility vests are mandatory at all times underground. If a person is detected without a hardhat or vest, the system automatically creates a high-priority PPE violation compliance case with photographic evidence and timestamps.

### Q6: How does the system handle poor lighting or dust underground?
**Answer:** The vision pipeline includes contrast-limited adaptive histogram equalization (CLAHE) and hue-saturation-value (HSV) color segmentation heuristics as a fallback when low-light conditions impair deep-learning bounding confidence.

---

## Category 3: Machine Learning & Predictive Analytics

### Q7: Why did you use Random Forest for risk classification?
**Answer:** Random Forest is an ensemble method consisting of multiple decision trees trained via bootstrap aggregating (bagging). It handles non-linear tabular sensor data effectively, resists overfitting, provides reliable probabilistic outputs, and natively yields feature importance rankings that feed our Explainable AI module. Our trained model achieves 92.55% test accuracy across 4 hazard tiers (Low, Medium, High, Critical).

### Q8: What features are passed to the risk prediction model?
**Answer:** The feature vector includes: Methane ($CH_4$) level, Carbon Monoxide ($CO$) level, air velocity, ambient temperature, relative humidity, equipment vibration, PPE violation frequency over 24 hours, zone incident history, worker fatigue score, equipment health index, and shift duration.

### Q9: How does the Isolation Forest anomaly detector work?
**Answer:** Isolation Forest isolates anomalies rather than profiling normal points. It constructs randomized isolation trees ($iTrees$). Outliers require fewer splits to be isolated and thus have shorter path lengths from the root. This is ideal for detecting subtle multi-gas interactions that may precede an explosion before hard threshold trips occur.

### Q10: How did you implement Explainable AI (XAI)?
**Answer:** For any High or Critical risk forecast, non-technical safety officers need to understand the reasoning. We extract tree feature importance contributions and generate natural language summaries (e.g., *"Risk is Critical because methane reached 1.1% (warning threshold 0.75%) accompanied by an elevated equipment vibration of 8.2 mm/s and 2 PPE violations in the last 24h"*).

---

## Category 4: Digital Twin & Architecture

### Q11: What is a "Digital Twin" in the context of this project?
**Answer:** A digital twin is a dynamic digital representation of a physical asset. In our application, it represents the 2D schematic layout of the coal mine (shafts, haulage roadways, longwall working faces, ventilation districts). The twin dynamically reflects live sensor readings, worker locations, camera feeds, and risk color gradients, allowing operators to understand mine-wide safety status at a single glance.

### Q12: Why did you choose an SVG-based 2D twin over 3D?
**Answer:** In industrial control rooms and low-bandwidth mining network environments, full 3D WebGL models require high GPU resources, increase page load times, and complicate rapid status appraisal. Responsive vector SVG maps render instantaneously across all devices, support clean CSS hazard color transitions, and allow precise coordinate mapping of IoT nodes.

### Q13: Explain the "Shift Replay" feature of your Digital Twin.
**Answer:** The shift replay slider allows safety investigators to scrub backward in time (e.g., -60 minutes, -180 minutes) to visualize historical sensor conditions and worker distribution before an incident occurred.

---

## Category 5: Compliance & Cryptographic Integrity

### Q14: How does the Compliance Case lifecycle work?
**Answer:**
$$\text{Trigger (AI or Sensor)} \rightarrow \text{Open Case} \rightarrow \text{Assigned to Supervisor} \rightarrow \text{In Progress} \rightarrow \text{Verification Requested} \rightarrow \text{Approved by Safety Officer} \rightarrow \text{Closed}$$
Each state change captures user IDs, timestamps, notes, and evidence.

### Q15: How do you prevent tampering with audit logs?
**Answer:** Every audit log record generates a cryptographic SHA-256 hash token:
$$\text{Token} = \text{SHA256}(\text{UserID} + \text{Action} + \text{EntityID} + \text{Timestamp} + \text{PreviousState} + \text{NewState})$$
Any manual alteration of the database table breaks the hash verification, guaranteeing non-repudiation for DGMS statutory audits.

---

## Category 6: Technical Implementation & Stack

### Q16: Why did you choose FastAPI over Flask or Django?
**Answer:** FastAPI utilizes Python 3 type hints, provides automatic Pydantic data validation, offers native asynchronous event loop performance ($ASGI$), and automatically generates interactive OpenAPI/Swagger documentation at `/docs`.

### Q17: How is user authentication handled?
**Answer:** Stateless JSON Web Tokens (JWT) signed with HMAC-SHA256 using an application secret. Passwords are salted and hashed using `bcrypt`. The token payload contains user ID, email, and role, validated on every protected API call via dependency injection.

### Q18: What were the biggest challenges faced during development?
**Answer:**
1. Handling multi-gas hazard modeling where individual readings are below single thresholds but dangerous in combination.
2. Ensuring fast rendering and state synchronization of the 2D digital twin under simulated high-frequency sensor streams.
3. Designing an intuitive interface that non-technical mine supervisors can navigate without extensive computer literacy.
