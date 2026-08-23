# Installation & Setup Guide

This guide describes how to run CloudCompliance Sentinel locally.

## Prerequisites
* **Python 3.8+**
* **Node.js 16+** & **npm**

## Setup Steps

### 1. Database & Backend API
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and active a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   ```
3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the environment variables example file:
   ```bash
   cp .env.example .env
   ```
5. Launch the FastAPI application:
   ```bash
   uvicorn app.main:app --reload
   ```
6. Verify the server is running by opening: `http://127.0.0.1:8000/health`

### 2. React UI Dashboard
1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Copy environment configuration:
   ```bash
   cp .env.example .env
   ```
4. Start the Vite server:
   ```bash
   npm run dev
   ```
5. Launch the dashboard app at the address specified in the CLI (usually `http://localhost:5173`).
