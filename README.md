# RazorPay Recovery Brain

A robust, agentic payment recovery orchestration system.

## Project Architecture

This project is built using:
- **Backend**: FastAPI, LangGraph, Python 3.10+
- **Persistence**: SQLite (via SQLAlchemy)
- **Frontend**: React (Vite) + Custom CSS Glassmorphism
- **Integration**: Razorpay Python SDK

The system intelligently categorizes failed payments, predicts recovery probability using ML, diagnoses the issue with agentic reasoning, checks plans against policy rules, executes the recovery action, and tracks everything in a persistent audit log.

## Getting Started

### 1. Backend Setup

1. Copy `.env.example` to `.env` and fill in your Razorpay Test API keys.
```bash
cp .env.example .env
```
2. Install dependencies (if not already done):
```bash
pip install -r requirements.txt
```
3. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```
The API will run on `http://127.0.0.1:8000`. 
Swagger Documentation: `http://127.0.0.1:8000/docs`

### 2. Frontend Setup

1. Navigate to the `frontend` folder:
```bash
cd frontend
```
2. Start the Vite development server:
```bash
npm run dev
```
3. Open your browser to the local URL provided by Vite (usually `http://localhost:5173`).

### 3. Usage

1. In the React Dashboard, enter a payment ID and failure details.
2. Click **"Trigger Recovery Agent"**.
3. Watch the live tracker update via polling as the LangGraph workflow analyzes, diagnoses, and ultimately attempts to recover the payment.
