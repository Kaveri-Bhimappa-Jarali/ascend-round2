# Compliance Policies and Rules

Below is the list of compliance rules implemented in the CloudCompliance Sentinel Engine and how they map to standards.

## Active Rules

### 1. Encryption Required (`ENCRYPTION_REQUIRED`)
* **Standard**: GDPR Article 32 (Security of processing), HIPAA Security Rule §164.312(a)(2)(iv)
* **Target Resources**: `storage`, `database`
* **Condition**: `encryption_enabled == false`
* **Violation Severity**: `HIGH`
* **Default Description**: Storage buckets or database instances must have encryption-at-rest enabled to prevent data exposure.

### 2. Audit Logging Required (`LOGGING_REQUIRED`)
* **Standard**: GDPR Article 30 (Records of processing activities), HIPAA Security Rule §164.312(b)
* **Target Resources**: `storage`, `database`, `compute`
* **Condition**: `logging_enabled == false`
* **Violation Severity**: `MEDIUM`
* **Default Description**: Enable resource change logging and access tracking logs to support forensic audit checks.

### 3. Public Exposure Forbidden (`PUBLIC_EXPOSURE_FORBIDDEN`)
* **Standard**: GDPR Article 25 (Data protection by design and by default)
* **Target Resources**: `storage`, `database`, `vpc`
* **Condition**: `public_access == true` or firewall rule allowing `0.0.0.0/0` access to databases
* **Violation Severity**: `HIGH`
* **Default Description**: Private databases or buckets must not be accessible via the public internet.
