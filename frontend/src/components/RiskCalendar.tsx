type Props = { riskSeries: number[] };

export default function RiskCalendar({ riskSeries }: Props) {
  // Simple 7-day blocks with color
  const colors = (r: number) => r > 0.7 ? "bg-red-500" : r > 0.5 ? "bg-yellow-500" : "bg-green-500";
  return (
    <div className="card p-6">
      <h3 className="font-semibold mb-3">Risk Calendar (Next 7 Days)</h3>
      <div className="grid grid-cols-7 gap-2">
        {riskSeries.map((r, i) => (
          <div key={i} className="text-center">
            <div className={`w-8 h-8 rounded ${colors(r)}`} />
            <div className="text-xs mt-1">D{i+1}</div>
          </div>
        ))}
      </div>
    </div>
  );
}


