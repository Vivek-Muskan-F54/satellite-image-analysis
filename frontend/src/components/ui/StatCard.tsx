import React from 'react';
import { Card, CardBody } from './Card';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ElementType;
  iconColorClass?: string;
  iconBgClass?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon: Icon,
  iconColorClass = "text-blue-600",
  iconBgClass = "bg-blue-50"
}) => {
  return (
    <Card className="hover:shadow-md transition-shadow duration-200">
      <CardBody className="p-5 flex items-center">
        <div className={`p-3 rounded-xl ${iconBgClass} mr-4`}>
          <Icon className={`h-6 w-6 ${iconColorClass}`} />
        </div>
        <div className="overflow-hidden">
          <p className="text-sm font-medium text-slate-500 mb-1">{title}</p>
          <p className="text-2xl font-bold text-slate-900 truncate" title={String(value)}>
            {value}
          </p>
        </div>
      </CardBody>
    </Card>
  );
};
