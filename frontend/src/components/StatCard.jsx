import React from 'react';

const StatCard = ({ title, value, subtext, icon: Icon, alert = false, onClick }) => {
  return (
    <div
      onClick={onClick}
      className={`bg-white p-4 rounded-lg border transition-colors ${
        alert ? 'border-red-300 bg-red-50/20' : 'border-gray-200'
      } ${onClick ? 'cursor-pointer hover:border-gray-300' : ''}`}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">{title}</span>
        {Icon && (
          <div className={`p-2 rounded ${alert ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-600'}`}>
            <Icon size={16} />
          </div>
        )}
      </div>
      <div className="mt-2 flex items-baseline">
        <span className="text-2xl font-semibold text-gray-900">{value}</span>
      </div>
      {subtext && (
        <p className={`mt-1 text-xs ${alert ? 'text-red-600 font-medium' : 'text-gray-500'}`}>
          {subtext}
        </p>
      )}
    </div>
  );
};

export default StatCard;

