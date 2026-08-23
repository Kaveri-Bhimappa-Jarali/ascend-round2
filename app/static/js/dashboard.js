async function fetchJson(path, options) {
  const response = await fetch(path, options);
  if (!response.ok) {
    throw new Error(`${path} returned ${response.status}`);
  }
  return response.json();
}

function setText(id, value) {
  document.getElementById(id).textContent = value;
}

async function loadSummary() {
  const summary = await fetchJson("/api/summary");
  setText("total-resources", summary.total_resources);
  setText("compliant-resources", summary.compliant_resources);
  setText("violations", summary.violations);
  setText("compliance-score", `${summary.compliance_score}%`);
  setText("score-label", summary.score_label);
}

async function loadProviders() {
  const providers = await fetchJson("/api/providers");
  const container = document.getElementById("providers");
  container.innerHTML = "";

  Object.entries(providers).forEach(([name, details]) => {
    const panel = document.createElement("article");
    panel.innerHTML = `
      <span>${name.toUpperCase()}</span>
      <strong>${details.status}</strong>
      <p>Resources: ${details.resources}</p>
      <p>Violations: ${details.violations}</p>
    `;
    container.appendChild(panel);
  });
}

async function loadViolations() {
  const violations = await fetchJson("/api/violations");
  const table = document.getElementById("violation-table");

  if (violations.length === 0) {
    table.innerHTML = '<tr><td colspan="6">No violations found.</td></tr>';
    return;
  }

  table.innerHTML = violations
    .map(
      (violation) => `
        <tr>
          <td>-</td>
          <td>${violation.resource_id}</td>
          <td>${violation.rule_id}</td>
          <td>${violation.severity}</td>
          <td>${violation.status}</td>
          <td>${violation.detected_at}</td>
        </tr>
      `,
    )
    .join("");
}

async function loadResources() {
  const resources = await fetchJson("/api/resources");
  document.getElementById("resources").textContent = JSON.stringify(resources, null, 2);
}

async function refreshDashboard() {
  await Promise.all([loadSummary(), loadProviders(), loadViolations(), loadResources()]);
}

document.getElementById("run-scan").addEventListener("click", async () => {
  await fetchJson("/api/scan", { method: "POST" });
  await refreshDashboard();
});

refreshDashboard().catch((error) => {
  console.error(error);
});
