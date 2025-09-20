type Props = { risk: number };

export default function TipsAndBadges({ risk }: Props) {
  const tips = risk > 0.7
    ? ["Stay indoors during peak heat.", "Drink more water today!", "Check on elderly neighbors."]
    : ["Enjoy the day!", "Keep hydrated.", "Light outdoor activity is fine."];
  const badge = risk < 0.3 ? "Safe Day Award!" : risk < 0.5 ? "Steady Day Badge" : risk < 0.7 ? "Caution Badge" : "Heat Watch Badge";
  return (
    <div className="card p-6">
      <h3 className="font-semibold mb-2">Health Tips</h3>
      <ul className="list-disc pl-5 text-sm text-gray-700">
        {tips.map((t, i) => <li key={i}>{t}</li>)}
      </ul>
      <div className="mt-3 text-sm"><span className="px-2 py-1 rounded-md bg-black/5">{badge}</span></div>
    </div>
  );
}


