# Major Project Report Outline

**Title:** AI-Driven Digital Twin and Predictive Compliance Management System for Coal Mine Safety Governance  
**Degree:** Bachelor of Technology in Computer Science and Engineering (Artificial Intelligence & Machine Learning)  
**Author:** Laxmi Prasad  

---

## Preliminary Pages
1. **Title Page** (Institute Name, Logo, Project Title, Student Details, Department)
2. **Certificate of Approval** (Signatures of Guide, Head of Department, External Examiner)
3. **Candidate's Declaration**
4. **Acknowledgement**
5. **Abstract**
6. **Table of Contents**
7. **List of Figures and Tables**
8. **List of Abbreviations** (DGMS, PPE, IoT, YOLO, XAI, RF, RUL, RBAC)

---

## Chapter 1: Introduction
### 1.1 Background & Motivation
- Indian Coal Mining sector overview and economic significance.
- Inherent hazards in underground and opencast mines: explosive gases, roof collapses, heavy equipment accidents, occupational health degradation.
- Statutory regulatory framework: Mines Act 1952, Coal Mines Regulations (CMR) 2017, and DGMS circulars.
### 1.2 Problem Statement
- Limitations of legacy safety monitoring: retrospective logbooks, fragmented sensors, delayed human inspection, lack of traceability.
### 1.3 Project Aim and Objectives
- Integrated vision-telemetry governance pipeline.
- Real-time PPE compliance tracking with edge AI.
- Multi-sensor IoT telemetry ingestion with Isolation Forest anomaly detection.
- Machine learning-driven shift risk forecasting with Explainable AI.
- Interactive 2D schematic Digital Twin for mine situational awareness.
- Closed-loop compliance case management with cryptographic audit logging.
### 1.4 Scope and Limitations
### 1.5 Organization of the Report

---

## Chapter 2: Literature Review
### 2.1 Occupational Safety in Subterranean Mining
- Review of major Indian mine disaster investigations (e.g., Chasnala, Chinakuri) and common failure points.
### 2.2 Computer Vision in Industrial Safety
- Evolution from Haar Cascades to YOLO architectures (YOLOv5 to YOLOv8) for industrial PPE monitoring.
### 2.3 IIoT and Sensor Analytics for Underground Atmospheres
- Gas sensing technologies ($CH_4, CO, O_2$), ventilation telemetry, and wireless sensor network constraints.
### 2.4 Digital Twin Paradigms in Mining
- State of the art in digital twin representation: 3D CAD vs. responsive 2D schematic diagrams for control rooms.
### 2.5 Explainable AI (XAI) in Mission-Critical Systems
- Importance of feature attribution (SHAP, tree feature importance) in safety decision support systems.
### 2.6 Comparative Analysis of Existing Solutions
- Summary table highlighting the research gap addressed by this project.

---

## Chapter 3: System Architecture and Methodology
### 3.1 Architectural Overview
- Three-tier decoupled architecture: Presentation Layer (React), Application Layer (FastAPI), Data/Inference Layer (PyTorch & Scikit-learn).
### 3.2 Data Flow Diagram (DFD Level 0, 1, 2)
### 3.3 Database Design & Entity Relationship Diagram (ERD)
- Relational schema: Users, Roles, Zones, Sensors, SensorReadings, PPEDetections, ComplianceCases, CorrectiveActions, WorkerBiometrics, EquipmentTelemetry, AuditLogs.
### 3.4 Computer Vision Subsystem (YOLOv8)
- Transfer learning on industrial safety equipment dataset.
- Classes: Hardhat, Safety Vest, Goggles, Gloves, Boots.
- Fallback heuristic computer vision engine.
### 3.5 Predictive Analytics Subsystem
- Anomaly Detection: Isolation Forest trained on multi-sensor features.
- Risk Classification: Random Forest Classifier with probability calibration.
- XAI Engine: Dynamic natural language explanation generation.
### 3.6 2D Digital Twin Design
- SVG vector rendering with dynamic color status binding and historical replay.
### 3.7 Governance & Cryptographic Auditing
- State hashing via SHA-256 for non-repudiation and auditor transparency.

---

## Chapter 4: Implementation Details
### 4.1 Development Environment & Tooling
- Hardware specs, software versions, and library choices.
### 4.2 Backend Implementation
- RESTful API design using FastAPI and Pydantic v2.
- JWT-based authentication and role-based route guards.
### 4.3 Frontend Implementation
- Component-driven architecture using Vite, React 18, and Tailwind CSS.
- Real-time updates and interactive charts using Recharts.
### 4.4 Automated Report Generation Engine
- Headless PDF compilation via ReportLab with corporate DGMS compliance branding.
- Excel generation via OpenPyXL for raw auditor verification.

---

## Chapter 5: Results and Discussion
### 5.1 AI/ML Experimental Evaluation
- YOLOv8 precision, recall, and mAP@0.5 curve.
- Random Forest Confusion Matrix, ROC-AUC, Precision-Recall metrics (92.55% accuracy).
- Isolation Forest anomaly detection latency (<50ms).
### 5.2 User Interface Walkthrough & Demonstrations
- Screenshots of Dashboard, Digital Twin, PPE Detection, Risk Forecast, Compliance Cases, Reports.
### 5.3 System Stress Testing and Scalability Analysis

---

## Chapter 6: Conclusion and Future Scope
### 6.1 Summary of Contributions
### 6.2 Future Enhancements
- Integration with LoRaWAN underground telemetry transceivers.
- 3D point-cloud LiDAR scan integration into the digital twin.
- Edge TPU / Jetson deployment directly on miner cap lamps and locomotives.

---

## References
1. DGMS (Directorate General of Mines Safety), *Coal Mines Regulations (CMR)*, Ministry of Labour & Employment, Govt. of India, 2017.
2. Jocher, G., et al., *Ultralytics YOLOv8 Architecture*, 2023.
3. Breiman, L., "Random Forests", *Machine Learning*, vol. 45, no. 1, pp. 5–32, 2001.
4. Liu, F. T., Ting, K. M., & Zhou, Z. H., "Isolation Forest", *IEEE ICDM*, 2008.
5. Lundberg, S. M., & Lee, S. I., "A Unified Approach to Interpreting Model Predictions", *NeurIPS*, 2017.
