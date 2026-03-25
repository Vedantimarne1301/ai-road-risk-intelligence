const Explanation = ({ explanation }) => {
  if (!explanation) return null;
  const { risk_summary, primary_drivers } = explanation;

  return (
    <div className="space-y-4">
      <p className="text-slate-300 text-sm leading-relaxed italic border-l-2 border-slate-600 pl-3">
        "{risk_summary}"
      </p>
      
      <div>
        <p className="text-xs font-bold text-slate-400 mb-2 uppercase">Key Risk Drivers:</p>
        <div className="flex flex-wrap gap-2">
          {primary_drivers?.map((driver, index) => (
            <span key={index} className="px-2 py-1 bg-slate-700 text-blue-300 text-[11px] rounded border border-slate-600">
              {driver}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Explanation;