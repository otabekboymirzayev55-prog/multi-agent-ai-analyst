import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Loader2, Activity } from "lucide-react";

const API = "http://localhost:8000";

export default function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "👋 Hi! I'm your Multi-Agent AI Analyst. Ask me anything about your customers, revenue, or business data!",
      steps: [],
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage() {
    const question = input.trim();
    if (!question || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setLoading(true);

    try {
      const res = await fetch(`${API}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.answer, steps: data.steps },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "❌ Error connecting to the API. Is the server running?", steps: [] },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleKey(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  return (
    <div style={styles.page}>
      {/* Header */}
      <div style={styles.header}>
        <Bot size={24} color="#fff" />
        <span style={styles.headerTitle}>Multi-Agent AI Analyst</span>
        <span style={styles.headerBadge}>● Live</span>
      </div>

      {/* Messages */}
      <div style={styles.messages}>
        {messages.map((msg, i) => (
          <div key={i} style={msg.role === "user" ? styles.userRow : styles.botRow}>
            {/* Avatar */}
            <div style={msg.role === "user" ? styles.userAvatar : styles.botAvatar}>
              {msg.role === "user" ? <User size={16} /> : <Bot size={16} />}
            </div>

            {/* Bubble */}
            <div style={msg.role === "user" ? styles.userBubble : styles.botBubble}>
              <p style={styles.bubbleText}>{msg.content}</p>

              {/* Agent path */}
              {msg.steps && msg.steps.length > 0 && (
                <div style={styles.steps}>
                  <Activity size={11} style={{ marginRight: 4 }} />
                  {msg.steps.join(" → ")}
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Loading bubble */}
        {loading && (
          <div style={styles.botRow}>
            <div style={styles.botAvatar}><Bot size={16} /></div>
            <div style={styles.botBubble}>
              <Loader2 size={18} style={{ animation: "spin 1s linear infinite" }} />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <div style={styles.inputBar}>
        <textarea
          style={styles.textarea}
          rows={1}
          placeholder="Ask about customers, revenue, churn..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          disabled={loading}
        />
        <button style={styles.sendBtn} onClick={sendMessage} disabled={loading}>
          <Send size={18} />
        </button>
      </div>

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #0f0f0f; }
        textarea:focus { outline: none; }
        textarea { resize: none; font-family: inherit; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
      `}</style>
    </div>
  );
}

const styles = {
  page: {
    display: "flex", flexDirection: "column", height: "100vh",
    background: "#0f0f0f", color: "#e5e5e5", fontFamily: "'Segoe UI', sans-serif",
  },
  header: {
    display: "flex", alignItems: "center", gap: 10,
    padding: "14px 20px", background: "#1a1a2e",
    borderBottom: "1px solid #2a2a3e",
  },
  headerTitle: { fontSize: 17, fontWeight: 600, color: "#fff", flex: 1 },
  headerBadge: { fontSize: 12, color: "#4ade80" },
  messages: { flex: 1, overflowY: "auto", padding: "20px 16px", display: "flex", flexDirection: "column", gap: 16 },
  userRow: { display: "flex", justifyContent: "flex-end", alignItems: "flex-start", gap: 8 },
  botRow: { display: "flex", justifyContent: "flex-start", alignItems: "flex-start", gap: 8 },
  userAvatar: {
    width: 30, height: 30, borderRadius: "50%", background: "#6366f1",
    display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0,
  },
  botAvatar: {
    width: 30, height: 30, borderRadius: "50%", background: "#1a1a2e",
    border: "1px solid #2a2a3e", display: "flex", alignItems: "center",
    justifyContent: "center", flexShrink: 0,
  },
  userBubble: {
    background: "#6366f1", color: "#fff", borderRadius: "18px 18px 4px 18px",
    padding: "10px 14px", maxWidth: "70%",
  },
  botBubble: {
    background: "#1e1e2e", border: "1px solid #2a2a3e", color: "#e5e5e5",
    borderRadius: "18px 18px 18px 4px", padding: "10px 14px", maxWidth: "75%",
  },
  bubbleText: { fontSize: 14, lineHeight: 1.6, whiteSpace: "pre-wrap" },
  steps: {
    marginTop: 8, fontSize: 10, color: "#6b7280",
    display: "flex", alignItems: "center", flexWrap: "wrap",
    borderTop: "1px solid #2a2a3e", paddingTop: 6,
  },
  inputBar: {
    display: "flex", gap: 8, padding: "12px 16px",
    background: "#1a1a2e", borderTop: "1px solid #2a2a3e",
  },
  textarea: {
    flex: 1, background: "#0f0f0f", border: "1px solid #2a2a3e",
    borderRadius: 12, padding: "10px 14px", color: "#e5e5e5",
    fontSize: 14, lineHeight: 1.5,
  },
  sendBtn: {
    background: "#6366f1", border: "none", borderRadius: 12,
    padding: "0 16px", color: "#fff", cursor: "pointer",
    display: "flex", alignItems: "center",
  },
};