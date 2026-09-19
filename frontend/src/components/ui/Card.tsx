import React from 'react';

export const Card: React.FC<{children: React.ReactNode, className?: string}> = ({ children, className = '' }) => (
  <div className={`bg-white shadow-sm border border-slate-200 rounded-lg overflow-hidden ${className}`}>
    {children}
  </div>
);

export const CardHeader: React.FC<{children: React.ReactNode, className?: string}> = ({ children, className = '' }) => (
  <div className={`px-6 py-4 border-b border-slate-200 ${className}`}>
    {children}
  </div>
);

export const CardBody: React.FC<{children: React.ReactNode, className?: string}> = ({ children, className = '' }) => (
  <div className={`px-6 py-4 ${className}`}>
    {children}
  </div>
);
