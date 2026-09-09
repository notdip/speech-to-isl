import { motion } from "motion/react";
import { useRef, useEffect } from "react";

const API_BASE = `http://${window.location.hostname}:8000`;
const CARD_WIDTH = 160;
const CARD_HEIGHT = 220;
const MEDIA_HEIGHT = 140;

function WordVideo({ src }) {
  const videoRef = useRef(null);

  useEffect(() => {
    const v = videoRef.current;
    if (!v) return;
    v.load();
    const playPromise = v.play();
    if (playPromise !== undefined) {
      playPromise.catch(() => {
        // Autoplay blocked — harmless, video will still show its first frame once loaded
      });
    }
  }, [src]);

  return (
    <video
      ref={videoRef}
      src={src}
      loop
      muted
      playsInline
      preload="auto"
      style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }}
    />
  );
}

export default function GlossTimeline({ wordBreakdown }) {
  if (!wordBreakdown || wordBreakdown.length === 0) return null;

  return (
    <div style={{ display: "flex", alignItems: "flex-start", gap: "1rem", overflowX: "auto", overflowY: "hidden", padding: "1rem 0" }}>
      {wordBreakdown.map((w, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.06 }}
          style={{
            width: `${CARD_WIDTH}px`,
            height: `${CARD_HEIGHT}px`,
            flexShrink: 0,
            background: "var(--panel)",
            borderRadius: "10px",
            padding: "0.75rem",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <div style={{ fontFamily: "var(--font-mono)", fontSize: "0.7rem", color: "var(--marigold)", marginBottom: "0.5rem", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
            {w.token}
          </div>

          <div style={{ width: "100%", height: `${MEDIA_HEIGHT}px`, borderRadius: "6px", overflow: "hidden", background: "var(--ink)" }}>
            {w.is_fingerspell ? (
              <div style={{ display: "flex", flexWrap: "wrap", gap: "2px", height: "100%", alignContent: "flex-start" }}>
                {w.letters.map((l, j) => (
                  <img key={j} src={`${API_BASE}${l.image_url}`} alt={l.letter} style={{ width: "30px", height: "30px", objectFit: "cover", borderRadius: "3px" }} />
                ))}
              </div>
            ) : (
              <WordVideo src={`${API_BASE}${w.video_url}`} />
            )}
          </div>
        </motion.div>
      ))}
    </div>
  );
}