const API_BASE = `http://${window.location.hostname}:8000`;

export async function processText(text, model = "llama3.1:8b") {
  const form = new FormData();
  form.append("text", text);
  form.append("model", model);
  const res = await fetch(`${API_BASE}/api/process-text`, { method: "POST", body: form });
  return res.json();
}

export async function processAudio(audioFile, model = "llama3.1:8b") {
  const form = new FormData();
  form.append("file", audioFile);
  form.append("model", model);
  const res = await fetch(`${API_BASE}/api/process-audio`, { method: "POST", body: form });
  return res.json();
}

export function videoUrl(path) {
  return `${API_BASE}${path}`;
}