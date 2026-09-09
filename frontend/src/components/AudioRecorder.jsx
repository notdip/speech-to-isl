import { useState, useRef } from "react";
import { motion } from "motion/react";

export default function AudioRecorder({ onTranscribed, disabled }) {
  const [recording, setRecording] = useState(false);
  const mediaRecorder = useRef(null);
  const chunks = useRef([]);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder.current = new MediaRecorder(stream);
    chunks.current = [];

    mediaRecorder.current.ondataavailable = (e) => chunks.current.push(e.data);
    mediaRecorder.current.onstop = async () => {
      const blob = new Blob(chunks.current, { type: "audio/webm" });
      const form = new FormData();
      form.append("file", blob, "recording.webm");

      const res = await fetch(`http://${window.location.hostname}:8000/api/transcribe`, { method: "POST", body: form });
      const data = await res.json();
      onTranscribed(data);
    };

    mediaRecorder.current.start();
    setRecording(true);
  };

  const stopRecording = () => {
    mediaRecorder.current?.stop();
    mediaRecorder.current?.stream.getTracks().forEach((t) => t.stop());
    setRecording(false);
  };

  return (
    <motion.button
      whileTap={{ scale: 0.92 }}
      onClick={recording ? stopRecording : startRecording}
      disabled={disabled}
      style={{
        width: "72px",
        height: "72px",
        borderRadius: "50%",
        border: `2px solid ${recording ? "var(--marigold)" : "var(--muted)"}`,
        background: recording ? "var(--marigold)" : "transparent",
        color: recording ? "var(--ink)" : "var(--paper)",
        fontSize: "1.5rem",
        cursor: "pointer",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        margin: "0 auto",
      }}
      animate={recording ? { boxShadow: ["0 0 0 0px rgba(232,163,61,0.4)", "0 0 0 16px rgba(232,163,61,0)"] } : {}}
      transition={recording ? { duration: 1.2, repeat: Infinity } : {}}
    >
      🎙
    </motion.button>
  );
}