export default function ReadinessShare() {
  const share = () => {
    const text = "Hospital readiness is strong. Stay safe and hydrated!";
    if (navigator.share) navigator.share({ title: "CRHS Update", text });
    else alert(text);
  };
  return (
    <div className="card p-6">
      <h3 className="font-semibold mb-2">Readiness & Share</h3>
      <ul className="list-disc pl-5 text-sm text-gray-700">
        <li>Cooling stations available</li>
        <li>Water supplies stocked</li>
        <li>Staff briefed on heat plans</li>
      </ul>
      <button className="btn-primary mt-3" onClick={share}>Share Update</button>
    </div>
  );
}


