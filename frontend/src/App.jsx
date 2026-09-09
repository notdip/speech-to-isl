import { useState } from "react";
import { motion } from "motion/react";
import SigningHand from "./components/SigningHand";
import AudioRecorder from "./components/AudioRecorder";
import { TranscriptBox, CleaningStatsBox, GlossBox, StatusStepper } from "./components/PipelineStages";
import ResultVideo from "./components/ResultVideo";
import GlossTimeline from "./components/GlossTimeline";
import History, { loadHistory, saveToHistory } from "./components/History";
import "./styles/tokens.css";

const API_BASE = `http://${window.location.hostname}:8000`;

export default function App() {
  const [textInput, setTextInput] = useState("");
  const [transcript, setTranscript] = useState("");
  const [language, setLanguage] = useState("");
  const [gloss, setGloss] = useState("");
  const [videoUrl, setVideoUrl] = useState(null);
  const [wordBreakdown, setWordBreakdown] = useState([]);
  const [stage, setStage] = useState(0);
  const [history, setHistory] = useState(loadHistory());

  const runFromTranscript = async (text) => {
    setTranscript(text);
    setStage(1);
    const form = new FormData();
    form.append("text", text);
    const translateRes = await fetch(`${API_BASE}/api/translate`, { method: "POST", body: form });
    const translateData = await translateRes.json();
    setGloss(translateData.gloss);
    setStage(2);

    const videoForm = new FormData();
    videoForm.append("gloss", translateData.gloss);
    const videoRes = await fetch(`${API_BASE}/api/generate-video`, { method: "POST", body: videoForm });
    const videoData = await videoRes.json();
    setVideoUrl(videoData.video_url);
    setWordBreakdown(videoData.word_breakdown);
    setStage(4);
    setHistory(saveToHistory({ transcript: text, gloss: translateData.gloss, videoUrl: videoData.video_url }));
  };

  const handleTranscribed = (data) => {
    setLanguage(data.language);
    runFromTranscript(data.text);
  };

  const handleTextSubmit = () => {
    if (!textInput.trim()) return;
    setLanguage("en (typed)");
    runFromTranscript(textInput);
  };

  const handleHistorySelect = (item) => {
    setTranscript(item.transcript);
    setGloss(item.gloss);
    setVideoUrl(item.videoUrl);
    setStage(4);
  };

  return (
    <div className="app-shell">
      <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "2rem" }}>
        <div style={{ width: "40px", height: "40px" }}><SigningHand /></div>
        <h1 style={{ fontFamily: "var(--font-display)", fontSize: "1.75rem", margin: 0 }}>Speak. See it signed.</h1>
      </div>

      <div className="two-col">
        <div>
          <div className="card" style={{ textAlign: "center" }}>
            <AudioRecorder onTranscribed={handleTranscribed} disabled={stage > 0 && stage < 4} />
            <div style={{ margin: "1rem 0", color: "var(--muted)", fontFamily: "var(--font-mono)", fontSize: "0.75rem" }}>— or type —</div>
            <textarea
              className="textarea"
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              rows={2}
              placeholder="Type a sentence..."
            />
            <motion.button whileTap={{ scale: 0.97 }} onClick={handleTextSubmit} className="btn btn-primary" style={{ marginTop: "0.75rem" }}>
              Translate
            </motion.button>
          </div>

          <StatusStepper currentStage={stage} />
          <TranscriptBox transcript={transcript} language={language} />
          <CleaningStatsBox transcript={transcript} />
          <GlossBox gloss={gloss} />
          <History items={history} onSelect={handleHistorySelect} />
        </div>

        <div>
          <ResultVideo videoUrl={videoUrl} />
          <GlossTimeline wordBreakdown={wordBreakdown} />
        </div>
      </div>
    </div>
  );
}