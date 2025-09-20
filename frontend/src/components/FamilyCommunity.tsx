type Props = { risk: number };

export default function FamilyCommunity({ risk }: Props) {
  const family = risk > 0.7 ? ["Keep kids cool with indoor games.", "Avoid midday sun."] : ["Outdoor play is okay in the morning."];
  const community = risk > 0.7 ? ["Organize indoor community gatherings.", "Distribute water at clinics."] : ["Plan community walks in the evening."];
  return (
    <div className="card p-6">
      <h3 className="font-semibold mb-2">Family & Community Tips</h3>
      <div className="grid sm:grid-cols-2 gap-4 text-sm">
        <div>
          <div className="font-medium mb-1">Family</div>
          <ul className="list-disc pl-5 text-gray-700">{family.map((t, i) => <li key={i}>{t}</li>)}</ul>
        </div>
        <div>
          <div className="font-medium mb-1">Community</div>
          <ul className="list-disc pl-5 text-gray-700">{community.map((t, i) => <li key={i}>{t}</li>)}</ul>
        </div>
      </div>
    </div>
  );
}


