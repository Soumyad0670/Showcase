# Showcase Backend Infrastructure Documentation

## Overview

The **app** folder is the orchestration engine and command center of the Showcase platform. While the `agents` folder handles the "thinking," the backend manages the **lifecycle**—handling file ingestion, database persistence, asynchronous task scheduling, and secure cloud deployment.

Built with **FastAPI**, it follows a strict **Layered Architecture** to ensure that our "no-compromise" technical standards are met through clean separation of concerns.

## What This System Does

### Input (What Comes In)

* **Resume Files**: PDF or Image uploads via Multipart/form-data.
* **User Metadata**: Preferences for themes, custom links, and professional tone.
* **Auth Tokens**: Secure JWTs for user session management.

### Output (What Goes Out)

* **Structured JSON**: Validated portfolio data ready for the frontend generator.
* **Live Portfolio URL**: The endpoint where the user's site is deployed (e.g., via Vercel).
* **Job Status**: Real-time updates on the AI generation progress.

---

## Architecture

### The Execution Pipeline

```
HTTP Request (PDF Upload)
      ↓
[1. API Layer] ← Validates request & returns Job ID
      ↓
[2. Tasks Layer] ← Offloads work to Background Worker
      ↓
[3. Service Layer] ← Orchestrates OCR -> Agents -> Deploy
      ↓
[4. Adapter Layer] ← Communicates with DB & Gemini
      ↓
[5. Persistence] ← Saves final portfolio to PostgreSQL

```

### Backend Hierarchy

```
app/
├── main.py                 #  Entry Point - Initializes FastAPI & Routers
├── tasks.py                #  Background Jobs - Orchestrates the AI lifecycle
├── api/                    #  HTTP Layer - Routes and Controller logic
│   └── v1/                 # Versioned Endpoints (resume, portfolio)
├── services/               #  Business Logic - The "Brain" of the backend
│   ├── ai_service.py       # Bridge to agents/integration.py
│   └── ocr_service.py      # Text extraction orchestration
├── schemas/                #  Data Contracts - Pydantic validation models
├── models/                 #  Persistence - SQLAlchemy database definitions
├── adapters/               #  Infrastructure - External system wrappers
└── core/                   #  Settings - Security, Config, and Env vars

```

---

##  File-by-File Breakdown

### 1️⃣ `api/v1/resume.py` & `portfolio.py`

**Purpose**: These are the "front doors" for the frontend.

* **`resume.py`**: Handles the initial PDF upload. It triggers the background task and returns a `job_id`.
* **`portfolio.py`**: Allows users to fetch their generated data or request a "regeneration" of specific sections.

### 2️⃣ `services/ai_service.py` - The Agentic Bridge

**Purpose**: This is the dedicated service that communicates with your Agentic Team's folder.

* **Role**: It maps the internal backend data into the format expected by `agents/integration.py`.
* **Standard**: It ensures that if the Agentic logic changes, we only need to update this one file in the backend.

### 3️⃣ `schemas/portfolio.py` - The Validator

**Purpose**: To ensure the AI output is 100% accurate before it hits our database.

* **Strictness**: Uses Pydantic to verify that the JSON returned by the agents contains all required fields (Hero, Projects, Skills) in the correct format.

### 4️⃣ `tasks.py` - The Background Orchestrator

**Purpose**: Handles long-running AI processes (4-10 seconds) so the user doesn't experience a lag.

* **Logic**:
1. Trigger `ocr_service` to get text.
2. Call `ai_service` to generate content.
3. Save result to `models/portfolio.py`.
4. Update job status to `COMPLETED`.



---

##  Complete Data Flow Example

### Step-by-Step Processing

#### 🔹 Step 1: Request & Validation (`api/` + `schemas/`)

User sends a PDF. The backend uses `schemas/resume.py` to ensure the file is valid.

```python
# API returns immediately
{ "job_id": "7aff-...", "status": "processing" }

```

#### 🔹 Step 2: Extraction & Intelligence (`services/`)

The `tasks.py` worker picks up the job.

1. **OCR**: `ocr_service` extracts raw text.
2. **AI**: `ai_service` calls `agents.integration.generate_portfolio(text)`.

#### 🔹 Step 3: Persistence (`models/` + `adapters/`)

The generated JSON is validated against `schemas/portfolio.py` and saved into PostgreSQL using the session managed in `adapters/database.py`.

---

##  Design Principles

1. **Stateless API**: The backend can scale horizontally because all session data is in the DB/JWT.
2. **Thin Controllers**: API routes should contain no logic—only calls to the `services` layer.
3. **Dependency Injection**: Uses `api/dependencies.py` to manage database connections and authentication cleanly.
4. **Fail-Safe Backgrounding**: If the AI Agent fails, `tasks.py` catches the error and updates the DB status so the frontend can show a "Retry" button.

---

##  Configuration & Security

### Environment Variables (`core/config.py`)

```bash
# Security & DB
DATABASE_URL="postgresql+psycopg2://..."
SECRET_KEY="your-jwt-secret"

# AI Integration
GEMINI_API_KEY="your-google-api-key"

```

### Security (`core/security.py`)

* **JWT Authentication**: Ensures only the owner can edit their portfolio.
* **CORS Middleware**: Configured in `main.py` to only allow requests from our trusted frontend.

---

##  Quality Metrics

### Backend Efficiency Score

We measure performance based on:

* **Response Time**: Time taken to return a `job_id` (< 200ms).
* **OCR Accuracy**: Success rate of text extraction.
* **DB Integrity**: Zero "orphan" records—every portfolio must link to a user.

---

##  Key Roles Summary

| Layer | Responsibility | Primary Tool |
| --- | --- | --- |
| **API** | Handle Requests | FastAPI Routers |
| **Services** | Logic Orchestration | Python Class Methods |
| **Schemas** | Data Contracts | Pydantic Models |
| **Adapters** | External I/O | SQLAlchemy / Gemini SDK |
| **Tasks** | Performance | Asyncio / BackgroundTasks |


**END OF BACKEND DOCUMENTATION**