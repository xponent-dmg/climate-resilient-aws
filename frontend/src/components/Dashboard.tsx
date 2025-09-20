"use client";
import { useAuth } from "@/context/AuthContext";
import { mockRegion, mockRisk, mockTemps, mockRiskTrend7Days, mockPatients, mockAlerts, mockReportCsv, delhiCoords } from "@/data/mockData";
import RiskScore from "@/components/RiskScore";
import TrendCharts from "@/components/TrendCharts";
import PatientTable from "@/components/PatientTable";
import ResourceSuggestions from "@/components/ResourceSuggestions";
import AlertsList from "@/components/AlertsList";
import ReportDownload from "@/components/ReportDownload";
import RiskMap from "@/components/RiskMap";
import ThemeToggle from "@/components/ThemeToggle";
import Sidebar from "@/components/Sidebar";
import CapacityManager from "@/components/CapacityManager";
import TipsAndBadges from "@/components/TipsAndBadges";
import RiskCalendar from "@/components/RiskCalendar";
import NotesChat from "@/components/NotesChat";
import FamilyCommunity from "@/components/FamilyCommunity";
import ReadinessShare from "@/components/ReadinessShare";
import FeedbackHelp from "@/components/FeedbackHelp";
import MultiRiskCards from "@/components/MultiRiskCards";
import MLOutlook from "@/components/MLOutlook";
import CapacityPredictor from "@/components/CapacityPredictor";
import ErrorBanner from "@/components/ErrorBanner";
import axios from "axios";
import { API_BASE } from "@/lib/config";
import { useMemo, useState, useEffect } from "react";

export default function Dashboard() {
  const { role, username, logout } = useAuth();
  const labels = mockTemps.map((t) => t.label);
  const [temps, setTemps] = useState<number[]>(mockTemps.map((t) => t.value));
  const [liveRisk, setLiveRisk] = useState<number>(mockRisk);
  const [multiRisks, setMultiRisks] = useState<{ heat?: number; flood?: number; resp?: number; vector?: number }>({ heat: mockRisk });
  const [mlPredictions, setMlPredictions] = useState<Record<string, number> | undefined>(undefined);
  const [section, setSection] = useState("overview");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const isAdmin = role === "Admin";
  const isClinician = role === "Clinician";
  const isAnalyst = role === "Analyst";
  const editablePatients = useMemo(() => isAdmin, [isAdmin]);

  // Auto-fetch on load
  useEffect(() => {
    fetchPredict();
  }, []);

  async function fetchPredict() {
    try {
      setLoading(true);
      setError(null);
      const res = await axios.post(`${API_BASE}/predict`, { region: mockRegion });
      if (res.data?.risks) {
        setMultiRisks(res.data.risks);
        if (res.data.risks.heat !== undefined) setLiveRisk(res.data.risks.heat);
      }
      if (Array.isArray(res.data?.temps)) setTemps(res.data.temps.map((v: any) => Number(v)));
      if (res.data?.ml && Object.keys(res.data.ml).length > 0) {
        setMlPredictions(res.data.ml);
      }
    } catch (e: any) {
      setError("Failed to fetch prediction: " + (e.message || "Unknown error"));
    } finally {
      setLoading(false);
    }
  }

  async function fetchReport() {
    try {
      setLoading(true);
      setError(null);
      const res = await axios.get(`${API_BASE}/reports`, { responseType: "blob" });
      // Create a download link
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'climate_health_report.csv');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (e: any) {
      setError("Failed to fetch report: " + (e.message || "Unknown error"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-gray-800">Climate-Resilient Healthcare Dashboard</h1>
          <p className="text-xs text-gray-500">Region: {mockRegion}</p>
        </div>
        <div className="flex items-center gap-3">
          <ThemeToggle />
          <span className="text-sm rounded-md px-2 py-1 bg-black/5">{role}</span>
          <button className="btn-primary" onClick={logout} aria-label="Logout">Logout {username ? `(${username})` : ""}</button>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 pb-2">
        {error && <ErrorBanner message={error} onClose={() => setError(null)} />}
        {loading && <div className="text-sm text-gray-600 py-2">Loading...</div>}
      </div>

      <div className="max-w-6xl mx-auto px-4 pb-10 grid md:grid-cols-[16rem_1fr] gap-6">
        <Sidebar selected={section} onSelect={setSection} />
        <div className="space-y-6">
          {section === "overview" && (
            <>
              <RiskScore risk={liveRisk} />
              <MultiRiskCards risks={multiRisks} />
              {mlPredictions && <MLOutlook ml={mlPredictions} />}
              <TrendCharts labels={labels} temps={temps} risk7={mockRiskTrend7Days} />
              <div className="flex gap-3">
                <button className="btn-primary" onClick={fetchPredict}>Refresh Data</button>
                <button className="px-4 py-2 rounded-md border" onClick={fetchReport}>Download Report</button>
              </div>
              <RiskMap coords={delhiCoords} risk={liveRisk} region={mockRegion} />
              <TipsAndBadges risk={liveRisk} />
            </>
          )}
          {section === "patients" && (
            <PatientTable patients={mockPatients} editable={editablePatients} />
          )}
          {section === "capacity" && isAdmin && (
            <>
              <CapacityManager suggestedBeds={liveRisk > 0.7 ? 10 : 5} suggestedStaff={liveRisk > 0.7 ? 5 : 2} />
              <CapacityPredictor onApply={(beds, staff) => {
                axios.post(`${API_BASE}/capacity`, { beds, staff })
                  .catch(e => setError("Failed to update capacity: " + (e.message || "Unknown error")));
              }} />
            </>
          )}
          {section === "resources" && isAdmin && (
            <ResourceSuggestions risk={liveRisk} />
          )}
          {section === "alerts" && (
            <AlertsList alerts={mockAlerts} />
          )}
          {section === "tips" && (
            <TipsAndBadges risk={liveRisk} />
          )}
          {section === "calendar" && (
            <RiskCalendar riskSeries={mockRiskTrend7Days.map((v) => Math.min(1, Math.max(0, v / 50)))} />
          )}
          {section === "notes" && (
            <NotesChat />
          )}
          {section === "family" && (
            <FamilyCommunity risk={liveRisk} />
          )}
          {section === "community" && (
            <FamilyCommunity risk={liveRisk} />
          )}
          {section === "readiness" && (
            <ReadinessShare />
          )}
          {section === "badges" && (
            <TipsAndBadges risk={liveRisk} />
          )}
          {section === "share" && (
            <ReadinessShare />
          )}
          {section === "reports" && (
            <ReportDownload csv={mockReportCsv} />
          )}
          {section === "feedback" && (
            <FeedbackHelp />
          )}
          {section === "help" && (
            <div className="card p-6">
              <h3 className="font-semibold mb-2">Help Guide</h3>
              <div className="space-y-3 text-sm">
                <p>The Climate-Resilient Healthcare System helps hospitals prepare for climate-related health risks in India.</p>
                <div>
                  <div className="font-medium">Key Features:</div>
                  <ul className="list-disc pl-5">
                    <li>Multi-risk monitoring (heat, floods, respiratory, vector-borne)</li>
                    <li>ML predictions for upcoming risks</li>
                    <li>Capacity planning tools</li>
                    <li>Health tips and community guidance</li>
                  </ul>
                </div>
                <div>
                  <div className="font-medium">Getting Started:</div>
                  <ol className="list-decimal pl-5">
                    <li>View current risks on the Overview page</li>
                    <li>Check ML Outlook for upcoming predictions</li>
                    <li>Use Capacity Predictor to plan resources</li>
                    <li>Download reports for sharing</li>
                  </ol>
                </div>
              </div>
            </div>
          )}
          {section === "settings" && isAdmin && (
            <div className="card p-6 text-sm text-gray-600">
              <h3 className="font-semibold mb-3">Settings</h3>
              <div className="space-y-4">
                <div>
                  <label className="block mb-1">API Endpoint</label>
                  <input className="input" value={API_BASE} disabled />
                </div>
                <div>
                  <label className="block mb-1">Default Region</label>
                  <input className="input" value={mockRegion} disabled />
                </div>
                <div>
                  <label className="block mb-1">Alert Threshold</label>
                  <input className="input" value="0.7" disabled />
                </div>
                <button className="btn-primary mt-2" disabled>Save Settings</button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}