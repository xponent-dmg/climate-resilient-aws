"use client";
import { useState } from "react";

export default function NotesChat() {
  const [notes, setNotes] = useState<string[]>([]);
  const [text, setText] = useState("");
  const add = () => {
    if (!text.trim()) return;
    setNotes((n) => [...n, text.trim()]);
    setText("");
  };
  return (
    <div className="card p-6">
      <h3 className="font-semibold mb-2">Team Notes</h3>
      <div className="space-y-2 max-h-48 overflow-auto border rounded-md p-2 bg-white">
        {notes.length === 0 ? <div className="text-sm text-gray-500">No notes yet</div> : notes.map((n, i) => (
          <div key={i} className="text-sm bg-black/5 rounded-md px-2 py-1">{n}</div>
        ))}
      </div>
      <div className="flex gap-2 mt-3">
        <input className="input" value={text} onChange={(e) => setText(e.target.value)} placeholder="Add a note about alerts..." />
        <button className="btn-primary" onClick={add}>Add</button>
      </div>
    </div>
  );
}


