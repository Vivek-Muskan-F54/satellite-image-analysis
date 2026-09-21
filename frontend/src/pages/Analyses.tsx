import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardBody } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { analysesApi } from '../services/api';
import { Image as ImageIcon, Eye } from 'lucide-react';

export const Analyses: React.FC = () => {
  const [analyses, setAnalyses] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAnalyses();
  }, []);

  const fetchAnalyses = async () => {
    try {
      const res = await analysesApi.list();
      setAnalyses(res.data.items);
    } catch (err) {
      setError('Failed to load analysis history.');
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Completed</span>;
      case 'PENDING':
      case 'PROCESSING':
        return <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">{status}</span>;
      case 'FAILED':
        return <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">Failed</span>;
      default:
        return <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">{status}</span>;
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-slate-900">Analysis History</h1>
        <Link to="/upload">
          <Button>Upload New Image</Button>
        </Link>
      </div>
      
      <Card>
        <CardBody>
          {error && (
            <div className="mb-4 bg-red-50 text-red-600 p-3 rounded-md">{error}</div>
          )}
          
          {isLoading ? (
            <div className="text-center py-12 text-slate-500">Loading...</div>
          ) : analyses.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              <ImageIcon className="mx-auto h-12 w-12 text-slate-300 mb-3" />
              <p className="mb-2 text-lg">No analyses yet.</p>
              <Link to="/upload" className="text-blue-600 hover:underline">Start your first analysis</Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200">
                <thead>
                  <tr>
                    <th className="px-4 py-3 bg-slate-50 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Date</th>
                    <th className="px-4 py-3 bg-slate-50 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Status</th>
                    <th className="px-4 py-3 bg-slate-50 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Prediction</th>
                    <th className="px-4 py-3 bg-slate-50 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Confidence</th>
                    <th className="px-4 py-3 bg-slate-50 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-slate-200">
                  {analyses.map((analysis) => (
                    <tr key={analysis.id}>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-slate-500">
                        {new Date(analysis.created_at).toLocaleString()}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm">
                        {getStatusBadge(analysis.status)}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-slate-900 font-medium">
                        {analysis.status === 'COMPLETED' && analysis.prediction ? analysis.prediction.predicted_class : '-'}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-slate-500">
                        {analysis.status === 'COMPLETED' && analysis.prediction ? `${(analysis.prediction.confidence * 100).toFixed(1)}%` : '-'}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-right text-sm font-medium space-x-3">
                        <Link to={`/analyses/${analysis.id}`} className="text-blue-600 hover:text-blue-900 inline-flex items-center">
                          <Eye className="h-4 w-4 mr-1" /> View Details
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  );
};
