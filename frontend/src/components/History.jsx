export function loadHistory() {
  try {
    return JSON.parse(localStorage.getItem("isl_history") || "[]");
  } catch {
    return [];
  }
}

export function saveToHistory(entry) {
  const history = loadHistory();
  const updated = [entry, ...history].slice(0, 15);
  localStorage.setItem("isl_history", JSON.stringify(updated));
  return updated;
}

export default function History({ items, onSelect }) {
  if (items.length === 0) return null;
  return (
    <div style={{ marginTop: "2rem" }}>
      <div style={{ fontFamily: "var(--font-mono)", fontSize: "0.7rem", color: "var(--teal)", textTransform: "uppercase", marginBottom: "0.5rem" }}>
        Recent
      </div>
      {items.map((item, i) => (
        <div
          key={i}
          onClick={() => onSelect(item)}
          style={{ padding: "0.5rem 0", borderBottom: "1px solid var(--panel)", cursor: "pointer", fontSize: "0.85rem", color: "var(--muted)" }}
        >
          {item.transcript}
        </div>
      ))}
    </div>
  );
}