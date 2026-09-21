import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardBody } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { StatusBadge } from '../components/ui/StatusBadge';
import { analysesApi } from '../services/api';
import { Upload, Eye, Search } from 'lucide-react';

export const Analyses: React.FC = () => {
  const [analyses, setAnalyses] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAnalyses();
  }, []);

  const fetchAnalyses = async () => {
    setIsLoading(true);
    setError('');
    try {
      const res = await analysesApi.list();
      const sorted = res.data.items.sort((a: any, b: any) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
      setAnalyses(sorted);
    } catch (err) {
      setError('Failed to load analysis history.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Analysis History</h1>
          <p className="text-sm text-slate-500 mt-1">Review all your past land-cover predictions and metadata.</p>
        </div>
        <Link to="/upload">
          <Button className="flex items-center">
            <Upload className="h-4 w-4 mr-2" />
            New Analysis
          </Button>
        </Link>
      </div>

      <Card>
        {/* Simple header with search-like visual (functional part left out to avoid complicating the API) */}
        <div className="px-6 py-4 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
          <div className="relative text-slate-400">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4" />
            <input
              type="text"
              placeholder="Search analyses..."
              className="pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white w-64"
              disabled
            />
          </div>
          <p className="text-sm text-slate-500 font-medium">Total: {analyses.length}</p>
        </div>

        <CardBody className="p-0">
          {error && (
            <div className="m-6 bg-red-50 text-red-600 p-4 rounded-lg border border-red-100 flex items-center justify-between">
              <span>{error}</span>
              <Button variant="outline" size="sm" onClick={fetchAnalyses}>Retry</Button>
            </div>
          )}

          {isLoading ? (
            <div className="p-6">
              <div className="animate-pulse space-y-4 py-4">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="flex space-x-4 border-b border-slate-100 pb-4">
                    <div className="h-4 bg-slate-100 rounded w-1/5"></div>
                    <div className="h-4 bg-slate-100 rounded w-1/5"></div>
                    <div className="h-4 bg-slate-100 rounded w-1/5"></div>
                    <div className="h-4 bg-slate-100 rounded w-1/5"></div>
                    <div className="h-4 bg-slate-100 rounded w-1/5"></div>
                  </div>
                ))}
              </div>
            </div>
          ) : analyses.length === 0 && !error ? (
            <div className="text-center py-20 px-6">
              <div className="bg-slate-50 p-6 rounded-full inline-flex mb-6">
                <Upload className="h-10 w-10 text-slate-300" />
              </div>
              <h3 className="text-xl font-medium text-slate-900 mb-2">No analyses history</h3>
              <p className="text-slate-500 mb-8 max-w-md mx-auto">You haven't analyzed any satellite images yet. Upload your first image to begin generating land-cover classifications.</p>
              <Link to="/upload">
                <Button>Start your first analysis</Button>
              </Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-100">
                <thead className="bg-slate-50/30">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Date & Time</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Predicted Class</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Confidence</th>
                    <th className="px-6 py-4 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">Action</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-slate-100">
                  {analyses.map((analysis) => (
                    <tr key={analysis.id} className="hover:bg-slate-50/50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                        <div className="font-medium text-slate-900">
                          {new Date(analysis.created_at).toLocaleDateString(undefined, {
                            year: 'numeric', month: 'short', day: 'numeric'
                          })}
                        </div>
                        <div className="text-slate-400 text-xs mt-0.5">
                          {new Date(analysis.created_at).toLocaleTimeString()}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <StatusBadge status={analysis.status} />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {analysis.status === 'COMPLETED' && analysis.prediction ? (
                          <span className="font-semibold text-slate-800">{analysis.prediction.predicted_class}</span>
                        ) : (
                          <span className="text-slate-400">-</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {analysis.status === 'COMPLETED' && analysis.prediction ? (
                          <div className="flex items-center">
                            <span className="text-slate-600 w-12">{(analysis.prediction.confidence * 100).toFixed(1)}%</span>
                            <div className="w-16 h-1.5 bg-slate-100 rounded-full overflow-hidden ml-2">
                              <div
                                className="h-full bg-blue-500 rounded-full"
                                style={{ width: `${analysis.prediction.confidence * 100}%` }}
                              ></div>
                            </div>
                          </div>
                        ) : (
                          <span className="text-slate-400">-</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <Link to={`/analyses/${analysis.id}`}>
                          <Button variant="ghost" className="text-blue-600 hover:text-blue-800 flex items-center justify-end w-full">
                            <Eye className="h-4 w-4 mr-1.5" /> View
                          </Button>
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
