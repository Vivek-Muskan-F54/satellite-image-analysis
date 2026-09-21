import React from 'react';

interface ConfidenceBarProps {
  label: string;
  confidence: number;
  isHighest?: boolean;
}

export const ConfidenceBar: React.FC<ConfidenceBarProps> = ({
  label,
  confidence,
  isHighest = false
}) => {
  const percentage = (confidence * 100).toFixed(1);
  const width = `${Math.max(1, confidence * 100)}%`; // Ensure at least 1% width for visibility

  return (
    <div className="mb-4">
      <div className="flex justify-between items-center mb-1.5">
        <span className={`text-sm ${isHighest ? 'font-semibold text-slate-900' : 'font-medium text-slate-600'}`}>
          {label}
        </span>
        <span className={`text-sm ${isHighest ? 'font-bold text-blue-700' : 'font-medium text-slate-500'}`}>
          {percentage}%
        </span>
      </div>
      <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden flex">
        <div
          className={`h-2.5 rounded-full transition-all duration-1000 ease-out ${
            isHighest ? 'bg-blue-600' : 'bg-slate-300'
          }`}
          style={{ width }}
          role="progressbar"
          aria-valuenow={confidence * 100}
          aria-valuemin={0}
          aria-valuemax={100}
        ></div>
      </div>
    </div>
  );
};
