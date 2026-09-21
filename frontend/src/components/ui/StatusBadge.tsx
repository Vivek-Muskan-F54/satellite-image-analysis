import React from 'react';

export const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  switch (status) {
    case 'COMPLETED':
      return (
        <span className="px-2.5 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
          Completed
        </span>
      );
    case 'PENDING':
    case 'PROCESSING':
      return (
        <span className="px-2.5 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-50 text-blue-700 border border-blue-200">
          <span className="animate-pulse mr-1.5 h-1.5 w-1.5 bg-blue-500 rounded-full inline-block align-middle"></span>
          {status === 'PENDING' ? 'Pending' : 'Processing'}
        </span>
      );
    case 'FAILED':
      return (
        <span className="px-2.5 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-rose-50 text-rose-700 border border-rose-200">
          Failed
        </span>
      );
    default:
      return (
        <span className="px-2.5 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-slate-100 text-slate-700 border border-slate-200">
          {status}
        </span>
      );
  }
};
