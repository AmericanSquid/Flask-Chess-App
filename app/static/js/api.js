export function getCsrfToken() {
  return document.querySelector('meta[name="csrf-token"]')?.content || "";
}

async function parseResponse(response) {
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(data.message || data.error || `HTTP ${response.status}`);
    error.status = response.status;
    error.data = data;
    throw error;
  }
  return data;
}

export async function getJSON(url) {
  const response = await fetch(url, {
    headers: { Accept: "application/json" },
    credentials: "same-origin",
  });
  return parseResponse(response);
}

export async function postJSON(url, payload = {}) {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
      Accept: "application/json",
    },
    credentials: "same-origin",
    body: JSON.stringify({ ...payload, csrf_token: getCsrfToken() }),
  });
  return parseResponse(response);
}
