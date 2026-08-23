# CloudCompliance Sentinel Frontend

This is a Vite + React application providing a web compliance dashboard.

## Setup Instructions

1. **Install Node dependencies**:
   Make sure you have Node.js installed, then run:
   ```bash
   cd frontend
   npm install
   ```

2. **Configure Settings**:
   Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

3. **Start Development Server**:
   ```bash
   npm run dev
   ```

## Folder Structure

- **`src/components/`**: Reusable UI elements (cards, compliance progress rings, charts).
- **`src/pages/`**: Page views (Dashboard overview, detailed Resource List, Reports page).
- **`src/services/`**: API integration wrapper to query the backend endpoints.
- **`src/hooks/`**: Custom react hooks (e.g. data fetching state).
- **`src/utils/`**: Helper methods and formatting functions.
- **`public/`**: Public assets (logos, images).
