import { useRef, useState } from "react";
import { motion } from "motion/react";

const API_BASE = `http://${window.location.hostname}:8000`;

export default function ResultVideo({ videoUrl }) {
  const videoRef = useRef(null);
  const [speed, setSpeed] = useState(1);

  if (!videoUrl) return null;
  const fullUrl = `${API_BASE}${videoUrl}`;

  const setPlaybackRate = (rate) => {
    setSpeed(rate);
    if (videoRef.current) videoRef.current.playbackRate = rate;
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ background: "var(--panel)", borderRadius: "12px", padding: "1.25rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <div style={{ fontFamily: "var(--font-mono)", fontSize: "0.7rem", color: "var(--teal)", textTransform: "uppercase" }}>
          Sign Language Video
        </div>
        <a href={fullUrl} download style={{ color: "var(--marigold)", fontFamily: "var(--font-mono)", fontSize: "0.75rem", textDecoration: "none" }}>
          ↓ Download
        </a>
      </div>

      <video ref={videoRef} src={fullUrl} controls autoPlay style={{ width: "100%", borderRadius: "8px" }} />

      <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.75rem" }}>
        {[0.5, 1, 1.5, 2].map((rate) => (
          <button
            key={rate}
            onClick={() => setPlaybackRate(rate)}
            style={{
              padding: "0.3rem 0.7rem",
              borderRadius: "6px",
              border: "none",
              background: speed === rate ? "var(--marigold)" : "var(--ink)",
              color: speed === rate ? "var(--ink)" : "var(--muted)",
              fontFamily: "var(--font-mono)",
              fontSize: "0.75rem",
              cursor: "pointer",
            }}
          >
            {rate}x
          </button>
        ))}
      </div>
    </motion.div>
  );
}