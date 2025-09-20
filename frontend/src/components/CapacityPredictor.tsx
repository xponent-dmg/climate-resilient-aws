"use client";
import { useState } from "react";
import axios from "axios";
import { API_BASE } from "@/lib/config";

type Season = "winter" | "summer" | "monsoon" | "autumn";

type Props = {
  onApply?: (beds: number, staff: number) => void;
};

export default function CapacityPredictor({ onApply }: Props) {
  const [so2, setSo2] = useState(10);
  const [no2, setNo2] = useState(20);
  const [pm10, setPm10] = useState(60);
  const [pm25, setPm25] = useState(30);
  const [region, setRegion] = useState("Delhi");
  const [season, setSeason] = useState<Season>("winter");
  const [prediction, setPrediction] = useState<{ beds: number; staff: number; method: string; factors?: any } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const predict = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await axios.post(`${API_BASE}/capacity/predict`, {
        so2,
        no2,
        pm10,
        pm25,
        region,
        season
      });
      setPrediction(res.data);
    } catch (err: any) {
      setError(err.message || "Failed to predict capacity");
    } finally {
      setLoading(false);
    }
  };

  const handleApply = () => {
    if (prediction && onApply) {
      onApply(prediction.beds, prediction.staff);
    }
  };

  const trainModel = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await axios.post(`${API_BASE}/capacity/train`);
      if (res.data.success) {
        alert(`Model trained successfully! R² scores: Beds=${res.data.metrics.beds_r2}, Staff=${res.data.metrics.staff_r2}`);
      } else {
        setError("Training failed: " + (res.data.error || "Unknown error"));
      }
    } catch (err: any) {
      setError(err.message || "Failed to train model");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card p-6">
      <h3 className="font-semibold mb-3">Capacity Predictor</h3>
      <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-3 mb-4">
        <div>
          <label className="block text-sm mb-1">SO₂ (μg/m³)</label>
          <input
            type="number"
            className="input"
            value={so2}
            onChange={(e) => setSo2(Number(e.target.value))}
          />
        </div>
        <div>
          <label className="block text-sm mb-1">NO₂ (μg/m³)</label>
          <input
            type="number"
            className="input"
            value={no2}
            onChange={(e) => setNo2(Number(e.target.value))}
          />
        </div>
        <div>
          <label className="block text-sm mb-1">PM10 (μg/m³)</label>
          <input
            type="number"
            className="input"
            value={pm10}
            onChange={(e) => setPm10(Number(e.target.value))}
          />
        </div>
        <div>
          <label className="block text-sm mb-1">PM2.5 (μg/m³)</label>
          <input
            type="number"
            className="input"
            value={pm25}
            onChange={(e) => setPm25(Number(e.target.value))}
          />
        </div>
        <div>
          <label className="block text-sm mb-1">Region</label>
          <select
            className="input"
            value={region}
            onChange={(e) => setRegion(e.target.value)}
          >
            <option value="Delhi">Delhi</option>
            <option value="Mumbai">Mumbai</option>
            <option value="Kolkata">Kolkata</option>
            <option value="Chennai">Chennai</option>
            <option value="Bangalore">Bangalore</option>
            <option value="Hyderabad">Hyderabad</option>
            <option value="Ahmedabad">Ahmedabad</option>
            <option value="Pune">Pune</option>
            <option value="Kanpur">Kanpur</option>
            <option value="Lucknow">Lucknow</option>
            <option value="Patna">Patna</option>
          </select>
        </div>
        <div>
          <label className="block text-sm mb-1">Season</label>
          <select
            className="input"
            value={season}
            onChange={(e) => setSeason(e.target.value as Season)}
          >
            <option value="winter">Winter (Jan-Feb)</option>
            <option value="summer">Summer (Mar-May)</option>
            <option value="monsoon">Monsoon (Jun-Sep)</option>
            <option value="autumn">Autumn (Oct-Dec)</option>
          </select>
        </div>
      </div>

      <div className="flex gap-3 mb-4">
        <button
          className="btn-primary"
          onClick={predict}
          disabled={loading}
        >
          {loading ? "Loading..." : "Predict Capacity"}
        </button>
        <button
          className="px-4 py-2 rounded-md border"
          onClick={trainModel}
          disabled={loading}
        >
          Train Model
        </button>
      </div>

      {error && <div className="text-sm text-red-600 mb-4">{error}</div>}

      {prediction && (
        <div className="border rounded-md p-4 bg-blue-50">
          <h4 className="font-medium mb-2">Prediction Results</h4>
          <div className="grid sm:grid-cols-2 gap-3 mb-3">
            <div>
              <div className="text-sm text-gray-600">Beds needed:</div>
              <div className="text-xl font-semibold">{prediction.beds}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Staff needed:</div>
              <div className="text-xl font-semibold">{prediction.staff}</div>
            </div>
          </div>
          <div className="text-xs text-gray-500">Method: {prediction.method}</div>
          {onApply && (
            <button
              className="btn-primary mt-3 w-full"
              onClick={handleApply}
            >
              Apply to Capacity Manager
            </button>
          )}
        </div>
      )}
    </div>
  );
}
