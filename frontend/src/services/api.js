/**
 * API service helper to query backend FastAPI endpoints.
 * Includes automatic fallback to simulated mock data if the backend is offline.
 */
import { mockComplianceSummary, mockViolations } from './mockData';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const defaultScanPayload = [
  {
    provider: "AWS",
    resource_type: "storage",
    resource_id: "demo-aws-s3-compliant",
    resource_name: "aws-prod-data-bucket",
    configuration: { encryption_enabled: true, logging_enabled: true, public_access: false }
  },
  {
    provider: "AWS",
    resource_type: "storage",
    resource_id: "demo-aws-s3-non-compliant",
    resource_name: "aws-public-unencrypted-bucket",
    configuration: { encryption_enabled: false, logging_enabled: false, public_access: true }
  },
  {
    provider: "AWS",
    resource_type: "database",
    resource_id: "demo-aws-rds-db",
    resource_name: "aws-legacy-db-instance",
    configuration: { encryption_enabled: false, logging_enabled: false, public_access: true }
  },
  {
    provider: "GCP",
    resource_type: "storage",
    resource_id: "demo-gcp-storage-compliant",
    resource_name: "gcp-secured-bucket",
    configuration: { encryption_enabled: true, logging_enabled: true, public_access: false }
  },
  {
    provider: "GCP",
    resource_type: "storage",
    resource_id: "demo-gcp-storage-non-compliant",
    resource_name: "gcp-public-storage-bucket",
    configuration: { encryption_enabled: true, logging_enabled: false, public_access: true }
  },
  {
    provider: "GCP",
    resource_type: "database",
    resource_id: "demo-gcp-cloudsql-db",
    resource_name: "gcp-dev-sql-instance",
    configuration: { encryption_enabled: false, logging_enabled: true, public_access: false }
  }
];

/**
 * Handle API response parsing and fallback logic.
 */
async function apiFetch(endpoint, options = {}) {
  const forceMock = import.meta.env.VITE_USE_MOCK_DATA === 'true';
  
  if (forceMock) {
    console.warn(`[Sentinel API] Force mock enabled. Returning mock data for: ${endpoint}`);
    return { data: getFallbackData(endpoint), isMock: true };
  }

  // Set up a 3-second timeout abort signal
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 3000);

  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      signal: controller.signal,
      ...options,
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      throw new Error(`API response error: status ${response.status}`);
    }
    
    const json = await response.json();
    return { data: json, isMock: false };
  } catch (error) {
    clearTimeout(timeoutId);
    console.warn(`[Sentinel API] Connection failed or timed out for ${BASE_URL}${endpoint}. Falling back to simulated mock data. Details: ${error.message}`);
    return { data: getFallbackData(endpoint), isMock: true };
  }
}

function getFallbackData(endpoint) {
  if (endpoint.includes('/compliance/summary')) {
    return mockComplianceSummary;
  }
  if (endpoint.includes('/violations')) {
    return mockViolations;
  }
  if (endpoint.includes('/reports/json') || endpoint.includes('/compliance/report')) {
    return {
      report_title: "CloudCompliance Sentinel Audit Report (Simulation)",
      generated_at: new Date().toISOString(),
      summary: mockComplianceSummary,
      violations: mockViolations
    };
  }
  // Default fallback for triggers/evaluate
  return { status: "evaluation_triggered", evaluations: mockViolations };
}

export async function getComplianceSummary() {
  return apiFetch('/api/compliance/summary');
}

export async function getViolations() {
  return apiFetch('/api/violations');
}

export async function triggerResourceEvaluation(resources = null) {
  const payload = resources || defaultScanPayload;
  return apiFetch('/api/resources/evaluate', {
    method: 'POST',
    body: JSON.stringify(payload)
  });
}

export async function getComplianceReport() {
  return apiFetch('/api/reports/json');
}
