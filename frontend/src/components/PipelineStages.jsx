import { motion } from "motion/react";

export function TranscriptBox({ transcript, language }) {
  if (!transcript) return null;
  return (
    <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="card">
      <div className="card-label">Input · {language || "—"}</div>
      <div style={{ fontFamily: "var(--font-body)" }}>{transcript}</div>
    </motion.div>
  );
}

export function CleaningStatsBox({ transcript }) {
  if (!transcript) return null;
  const words = transcript.trim().split(/\s+/).filter(Boolean);
  return (
    <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="card">
      <div className="card-label">Preprocessing</div>
      <div style={{ display: "flex", gap: "1.5rem", fontFamily: "var(--font-mono)", fontSize: "0.85rem", color: "var(--muted)" }}>
        <span>{words.length} words</span>
        <span>{transcript.length} chars</span>
        <span>{new Set(words.map(w => w.toLowerCase())).size} unique</span>
      </div>
    </motion.div>
  );
}

export function GlossBox({ gloss }) {
  if (!gloss) return null;
  return (
    <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="card">
      <div className="card-label">Gloss Translation</div>
      <div style={{ fontFamily: "var(--font-mono)", color: "var(--marigold)", fontSize: "0.95rem" }}>{gloss}</div>
    </motion.div>
  );
}

const STAGES = ["Speech Captured", "Speech to Text", "Gloss Generation", "Sign Synthesis"];

export function StatusStepper({ currentStage }) {
  return (
    <div className="card">
      <div className="stepper">
        {STAGES.map((s, i) => {
          const done = i < currentStage;
          const active = i === currentStage;
          return (
            <div key={s} className="stepper-item">
              <motion.div
                className={`stepper-dot ${done ? "done" : ""} ${active ? "active" : ""}`}
                animate={active ? { scale: [1, 1.15, 1] } : {}}
                transition={active ? { duration: 1, repeat: Infinity } : {}}
              />
              <div className={`stepper-label ${done || active ? "active" : ""}`}>{s}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}