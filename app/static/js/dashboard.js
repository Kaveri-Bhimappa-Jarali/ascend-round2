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

function appendText(parent, tagName, text) {
  const element = document.createElement(tagName);
  element.textContent = text;
  parent.appendChild(element);
  return element;
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
  container.replaceChildren();

  Object.entries(providers).forEach(([name, details]) => {
    const panel = document.createElement("article");
    appendText(panel, "span", name.toUpperCase());
    appendText(panel, "strong", details.status);
    appendText(panel, "p", `Resources: ${details.resources}`);
    appendText(panel, "p", `Violations: ${details.violations}`);
    container.appendChild(panel);
  });
}

async function loadViolations() {
  const violations = await fetchJson("/api/violations");
  const table = document.getElementById("violation-table");
  table.replaceChildren();

  if (violations.length === 0) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 7;
    cell.textContent = "No violations found.";
    row.appendChild(cell);
    table.appendChild(row);
    return;
  }

  violations.forEach((violation) => {
    const row = document.createElement("tr");
    [
      violation.provider,
      violation.resource_type,
      violation.resource_id,
      violation.rule_id,
      violation.severity,
      violation.status,
      violation.detected_at,
    ].forEach((value) => {
      appendText(row, "td", value ?? "-");
    });
    table.appendChild(row);
  });
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
