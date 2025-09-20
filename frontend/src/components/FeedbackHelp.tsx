"use client";
import { useState } from "react";

export default function FeedbackHelp() {
  const [text, setText] = useState("");
  const submit = () => {
    if (!text.trim()) return;
    alert("Thanks for the feedback! Vibes noted.");
    setText("");
  };
  return (
    <div className="card p-6">
      <h3 className="font-semibold mb-2">Feedback & Help</h3>
      <p className="text-sm text-gray-700">This system predicts heat stress risk using recent climate trends and suggests resource readiness steps. Keep it simple: hydrate, shade, rest.</p>
      <div className="mt-3 flex gap-2">
        <input className="input" placeholder="Your idea to improve..." value={text} onChange={(e) => setText(e.target.value)} />
        <button className="btn-primary" onClick={submit}>Send</button>
      </div>
    </div>
  );
}


