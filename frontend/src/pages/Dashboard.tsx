import React from 'react';
import { Card, CardHeader, CardBody } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Upload } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Dashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
        <Link to="/upload">
          <Button className="flex items-center">
            <Upload className="h-4 w-4 mr-2" />
            New Analysis
          </Button>
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <h2 className="font-semibold text-slate-800">Recent Analyses</h2>
          </CardHeader>
          <CardBody>
            <div className="text-center py-8 text-slate-500 flex flex-col items-center">
              <p className="mb-4">No analyses yet.</p>
              <p className="text-sm">Upload a satellite image to begin your first analysis.</p>
            </div>
          </CardBody>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <h2 className="font-semibold text-slate-800">System Overview (Coming Soon)</h2>
          </CardHeader>
          <CardBody>
            <div className="text-center py-8 text-slate-500">
              <p>Overall land classification statistics and usage metrics will appear here.</p>
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  );
};
