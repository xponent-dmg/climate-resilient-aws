type Risks = { heat?: number; flood?: number; resp?: number; vector?: number };

type Props = { risks: Risks };

const color = (v: number | undefined) => {
  const r = v ?? 0;
  if (r > 0.7) return "bg-red-500";
  if (r > 0.5) return "bg-yellow-500";
  if (r > 0.3) return "bg-orange-400";
  return "bg-green-500";
};

export default function MultiRiskCards({ risks }: Props) {
  const items: { key: keyof Risks; label: string }[] = [
    { key: "heat", label: "Heat Stress" },
    { key: "flood", label: "Flood" },
    { key: "resp", label: "Respiratory" },
    { key: "vector", label: "Vector-borne" },
  ];
  return (
    <div className="grid md:grid-cols-4 sm:grid-cols-2 gap-4">
      {items.map(({ key, label }) => {
        const v = risks[key] ?? 0;
        return (
          <div key={key} className="card p-4">
            <div className="text-sm text-gray-600">{label}</div>
            <div className="mt-2 flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${color(v)}`} />
              <div className="text-lg font-semibold">{v.toFixed(2)}</div>
            </div>
            <div className="mt-2 w-full h-2 bg-black/10 rounded-full">
              <div className={`h-full ${color(v)}`} style={{ width: `${Math.min(100, Math.max(0, v*100))}%` }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}


