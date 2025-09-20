type Props = { ml?: Record<string, number> };

const LABEL_MAP: Record<string, string> = {
  high_heat: "Heat Stress",
  high_flood: "Flooding",
  high_resp: "Respiratory",
  high_vector: "Vector-borne",
  high_drought: "Drought",
  high_storm: "Storms",
  high_air: "Air Pollution"
};

export default function MLOutlook({ ml }: Props) {
  if (!ml || Object.keys(ml).length === 0) {
    return (
      <div className="card p-6">
        <h3 className="font-semibold mb-2">ML Outlook</h3>
        <p className="text-sm text-gray-600">No ML predictions available. Run model training first.</p>
      </div>
    );
  }

  return (
    <div className="card p-6">
      <h3 className="font-semibold mb-2">ML Outlook</h3>
      <p className="text-xs text-gray-600 mb-3">Probability of high-risk conditions in next 7 days:</p>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {Object.entries(ml).map(([key, value]) => {
          const label = LABEL_MAP[key] || key;
          const color = value > 0.7 
            ? "bg-red-100 border-red-300 text-red-800" 
            : value > 0.5 
              ? "bg-yellow-100 border-yellow-300 text-yellow-800" 
              : "bg-green-100 border-green-300 text-green-800";
          
          return (
            <div key={key} className={`rounded-md border px-3 py-2 ${color}`}>
              <div className="text-xs font-medium">{label}</div>
              <div className="text-sm font-semibold">{Math.round(value * 100)}%</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
