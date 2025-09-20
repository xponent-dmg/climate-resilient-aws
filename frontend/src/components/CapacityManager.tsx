"use client";
import { useMemo, useState } from "react";
import axios from "axios";
import { API_BASE } from "@/lib/config";

type Props = { suggestedBeds: number; suggestedStaff: number };

export default function CapacityManager({ suggestedBeds, suggestedStaff }: Props) {
  const [beds, setBeds] = useState(50);
  const [staff, setStaff] = useState(20);
  const [msg, setMsg] = useState<string | null>(null);

  const readiness = useMemo(() => {
    const bedsScore = Math.min(100, (beds / (50 + suggestedBeds)) * 100);
    const staffScore = Math.min(100, (staff / (20 + suggestedStaff)) * 100);
    return Math.round((bedsScore * 0.6 + staffScore * 0.4));
  }, [beds, staff, suggestedBeds, suggestedStaff]);

  const applySuggestions = async () => {
    const nb = beds + suggestedBeds;
    const ns = staff + suggestedStaff;
    setBeds(nb);
    setStaff(ns);
    try {
      await axios.post(`${API_BASE}/capacity`, { beds: nb, staff: ns });
      setMsg("Suggestions applied. Capacity updated!");
    } catch {
      setMsg("Updated locally. Backend save failed.");
    }
    setTimeout(() => setMsg(null), 2000);
  };

  return (
    <div className="card p-6">
      <h3 className="font-semibold mb-4">Hospital Capacity</h3>
      <div className="grid sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm mb-1">Beds</label>
          <input className="input" type="number" value={beds} onChange={(e) => setBeds(parseInt(e.target.value || "0"))} />
          <p className="text-xs text-gray-500 mt-1">Suggested: +{suggestedBeds} beds</p>
        </div>
        <div>
          <label className="block text-sm mb-1">Staff</label>
          <input className="input" type="number" value={staff} onChange={(e) => setStaff(parseInt(e.target.value || "0"))} />
          <p className="text-xs text-gray-500 mt-1">Suggested: +{suggestedStaff} staff</p>
        </div>
      </div>
      <div className="mt-4">
        <div className="text-sm mb-1">Readiness</div>
        <div className="w-full h-3 bg-black/10 rounded-full overflow-hidden">
          <div className="h-full bg-green-600" style={{ width: `${readiness}%` }} />
        </div>
        <div className="text-xs text-gray-600 mt-1">{readiness}% ready</div>
      </div>
      <div className="mt-4 flex gap-3">
        <button className="btn-primary" onClick={applySuggestions}>Apply Suggestions</button>
        <button className="px-4 py-2 rounded-md border" onClick={async () => {
          try { await axios.post(`${API_BASE}/capacity`, { beds, staff }); setMsg("Capacity saved!"); }
          catch { setMsg("Save failed."); }
          setTimeout(() => setMsg(null), 2000);
        }}>Save</button>
      </div>
      {msg && <div className="text-sm text-green-700 mt-2">{msg}</div>}
    </div>
  );
}


