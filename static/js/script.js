/**
 * SepsisGuard — Client-Side Logic
 *
 * Responsibilities:
 *  1. Load sample patient presets into the form fields.
 *  2. POST form values to /predict and handle the response.
 *  3. Animate the risk-gauge ring and update result labels.
 *  4. Display server-side error messages in a styled banner.
 */

"use strict";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const PRESETS = {
  healthy:  { HR: 72,  O2Sat: 99, Temp: 36.8, SBP: 118, MAP: 88, Resp: 14,
              BUN: 12.0, Creatinine: 0.9, Glucose: 95.0,  WBC: 6.5,  Age: 35, Gender: 0 },
  warning:  { HR: 105, O2Sat: 94, Temp: 38.4, SBP: 100, MAP: 70, Resp: 24,
              BUN: 22.0, Creatinine: 1.4, Glucose: 140.0, WBC: 13.0, Age: 62, Gender: 1 },
  critical: { HR: 130, O2Sat: 88, Temp: 39.5, SBP: 80,  MAP: 55, Resp: 32,
              BUN: 45.0, Creatinine: 2.8, Glucose: 180.0, WBC: 19.0, Age: 74, Gender: 1 },
};

const FIELD_LABELS = {
  HR:         "Heart Rate",
  O2Sat:      "O₂ Saturation",
  Temp:       "Temperature",
  SBP:        "Systolic BP",
  MAP:        "Mean Arterial Pressure",
  Resp:       "Respiratory Rate",
  BUN:        "BUN",
  Creatinine: "Creatinine",
  Glucose:    "Glucose",
  WBC:        "WBC",
  Age:        "Age",
  Gender:     "Gender",
};

const RING_CIRCUMFERENCE = 2 * Math.PI * 52; // r = 52, matches SVG

// ---------------------------------------------------------------------------
// Preset buttons
// ---------------------------------------------------------------------------

document.querySelectorAll(".preset-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const preset = PRESETS[btn.dataset.preset];
    if (!preset) return;
    Object.entries(preset).forEach(([key, value]) => {
      const el = document.getElementById(key);
      if (el) el.value = value;
    });
    // Clear any previous results when loading a new preset
    resetResults();
  });
});

// ---------------------------------------------------------------------------
// Assess button
// ---------------------------------------------------------------------------

const assessBtn  = document.getElementById("assess-btn");
const errorBanner = document.getElementById("error-banner");

assessBtn.addEventListener("click", async () => {
  clearError();

  const payload = {};
  for (const field of Object.keys(FIELD_LABELS)) {
    const el = document.getElementById(field);
    if (!el) continue;
    payload[field] = el.value;
  }

  setLoading(true);

  try {
    const res = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (!res.ok) {
      showError(data.error || "An unexpected error occurred. Please try again.");
      return;
    }

    renderResult(data, payload);
  } catch (_err) {
    showError("Could not reach the server. Make sure app.py is running.");
  } finally {
    setLoading(false);
  }
});

// ---------------------------------------------------------------------------
// Result rendering
// ---------------------------------------------------------------------------

function renderResult(data, payload) {
  document.getElementById("result-empty").hidden = true;

  const content = document.getElementById("result-content");
  content.hidden = false;

  const prob   = data.probability;
  const isHigh = data.prediction === 1;

  // -- Percentage text --
  document.getElementById("risk-value").textContent = prob + "%";

  // -- Ring animation --
  const ring   = document.getElementById("ring-fill");
  const offset = RING_CIRCUMFERENCE - (prob / 100) * RING_CIRCUMFERENCE;
  ring.style.strokeDashoffset = offset;
  ring.style.stroke = isHigh ? "#C6323A" : "#1E8E5A";

  // -- Labels --
  const label = document.getElementById("risk-label");
  const note  = document.getElementById("risk-note");
  label.className = "risk-label " + (isHigh ? "high" : "low");

  if (isHigh) {
    label.textContent = "⚠ High Risk of Sepsis";
    note.textContent  = "Recommend immediate clinical review and sepsis protocol consideration.";
  } else {
    label.textContent = "✓ Low Risk of Sepsis";
    note.textContent  = "Continue routine monitoring per standard care protocol.";
  }

  // -- Badge --
  let badge = document.getElementById("risk-badge");
  if (!badge) {
    badge = document.createElement("p");
    badge.id = "risk-badge";
    label.after(badge);
  }
  badge.className   = "risk-badge " + (isHigh ? "high" : "low");
  badge.textContent = isHigh ? "HIGH RISK" : "LOW RISK";

  // -- Summary table --
  const table = document.getElementById("summary-table");
  table.innerHTML = Object.entries(payload)
    .map(([key, value]) => {
      const displayVal = key === "Gender"
        ? (String(value) === "1" ? "Male" : "Female")
        : value;
      return `<tr><td>${FIELD_LABELS[key] ?? key}</td><td>${displayVal}</td></tr>`;
    })
    .join("");
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function setLoading(loading) {
  const btn = document.getElementById("assess-btn");
  btn.disabled = loading;
  btn.innerHTML = loading
    ? `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><circle cx="12" cy="12" r="10" opacity=".25"/><path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"><animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="0.75s" repeatCount="indefinite"/></path></svg> Analyzing&hellip;`
    : `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg> Run Risk Assessment`;
}

function showError(message) {
  errorBanner.textContent = message;
  errorBanner.hidden = false;
}

function clearError() {
  errorBanner.textContent = "";
  errorBanner.hidden = true;
}

function resetResults() {
  clearError();
  document.getElementById("result-empty").hidden   = false;
  document.getElementById("result-content").hidden = true;
}
