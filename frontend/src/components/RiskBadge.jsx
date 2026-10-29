import React from 'react';

const RiskBadge = ({ level, score }) => {
  const normalized = (level || 'Low').toLowerCase();
  
  const styles = {
    low: 'bg-green-50 text-green-700 border-green-200',
    medium: 'bg-amber-50 text-amber-700 border-amber-200',
    high: 'bg-orange-50 text-orange-700 border-orange-200',
    critical: 'bg-red-50 text-red-700 border-red-200'
  }[normalized] || 'bg-gray-50 text-gray-700 border-gray-200';

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${styles}`}>
      <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${
        normalized === 'low' ? 'bg-green-500' :
        normalized === 'medium' ? 'bg-amber-500' :
        normalized === 'high' ? 'bg-orange-500' : 'bg-red-500'
      }`} />
      {level} {score !== undefined && `(${score})`}
    </span>
  );
};

export default RiskBadge;

