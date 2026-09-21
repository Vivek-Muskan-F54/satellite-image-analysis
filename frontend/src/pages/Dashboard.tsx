import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardBody } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { StatCard } from '../components/ui/StatCard';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Upload, Activity, CheckCircle, Clock, Server, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { analysesApi } from '../services/api';

export const Dashboard: React.FC = () => {
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
      setError('Unable to load recent analyses.');
    } finally {
      setIsLoading(false);
    }
  };

  const recentAnalyses = analyses.slice(0, 5);

  const totalAnalyses = analyses.length;
  const completedAnalyses = analyses.filter(a => a.status === 'COMPLETED').length;
  const completedWithPredictions = analyses.filter(a => a.status === 'COMPLETED' && a.prediction);
  const mostRecentPrediction = completedWithPredictions.length > 0
    ? completedWithPredictions[0].prediction.predicted_class
    : '-';
  const modelVersion = analyses.length > 0 && analyses[0].model_version ? analyses[0].model_version : 'v1.0';

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header section */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Dashboard</h1>
          <p className="text-sm text-slate-500 mt-1">Monitor your satellite image analyses and land-cover predictions.</p>
        </div>
        <Link to="/upload">
          <Button className="flex items-center">
            <Upload className="h-4 w-4 mr-2" />
            New Analysis
          </Button>
        </Link>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Analyses"
          value={isLoading ? '-' : totalAnalyses}
          icon={Activity}
          iconColorClass="text-blue-600"
          iconBgClass="bg-blue-50"
        />
        <StatCard
          title="Completed"
          value={isLoading ? '-' : completedAnalyses}
          icon={CheckCircle}
          iconColorClass="text-emerald-600"
          iconBgClass="bg-emerald-50"
        />
        <StatCard
          title="Latest Prediction"
          value={isLoading ? '-' : mostRecentPrediction}
          icon={Clock}
          iconColorClass="text-purple-600"
          iconBgClass="bg-purple-50"
        />
        <StatCard
          title="Model Version"
          value={isLoading ? '-' : modelVersion}
          icon={Server}
          iconColorClass="text-slate-600"
          iconBgClass="bg-slate-100"
        />
      </div>

      {/* Recent Analyses Table */}
      <Card>
        <CardHeader className="flex justify-between items-center">
          <h2 className="text-lg font-semibold text-slate-900">Recent Analyses</h2>
          {analyses.length > 0 && (
            <Link to="/analyses" className="text-sm font-medium text-blue-600 hover:text-blue-800 flex items-center group">
              View all
              <ArrowRight className="h-4 w-4 ml-1 transition-transform group-hover:translate-x-1" />
            </Link>
          )}
        </CardHeader>

        {isLoading ? (
          <CardBody>
            <div className="animate-pulse space-y-4 py-4">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="flex space-x-4">
                  <div className="h-4 bg-slate-200 rounded w-1/4"></div>
                  <div className="h-4 bg-slate-200 rounded w-1/4"></div>
                  <div className="h-4 bg-slate-200 rounded w-1/4"></div>
                  <div className="h-4 bg-slate-200 rounded w-1/4"></div>
                </div>
              ))}
            </div>
          </CardBody>
        ) : error ? (
          <CardBody>
            <div className="text-center py-12">
              <p className="text-red-500 mb-4">{error}</p>
              <Button onClick={fetchAnalyses} variant="outline">Try Again</Button>
            </div>
          </CardBody>
        ) : recentAnalyses.length === 0 ? (
          <CardBody>
            <div className="text-center py-16 flex flex-col items-center justify-center">
              <div className="bg-slate-50 p-4 rounded-full mb-4">
                <Upload className="h-8 w-8 text-slate-400" />
              </div>
              <h3 className="text-lg font-medium text-slate-900 mb-1">No analyses yet</h3>
              <p className="text-slate-500 mb-6 max-w-sm">Upload a satellite image to generate your first land-cover prediction.</p>
              <Link to="/upload">
                <Button variant="primary">Start your first analysis</Button>
              </Link>
            </div>
          </CardBody>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-slate-50/50">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Date</th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Prediction</th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Confidence</th>
                  <th className="px-6 py-4 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-100">
                {recentAnalyses.map((analysis) => (
                  <tr key={analysis.id} className="hover:bg-slate-50/50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                      {new Date(analysis.created_at).toLocaleDateString(undefined, {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <StatusBadge status={analysis.status} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {analysis.status === 'COMPLETED' && analysis.prediction ? (
                        <span className="font-medium text-slate-900">{analysis.prediction.predicted_class}</span>
                      ) : (
                        <span className="text-slate-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {analysis.status === 'COMPLETED' && analysis.prediction ? (
                        <span className="text-slate-600">{(analysis.prediction.confidence * 100).toFixed(1)}%</span>
                      ) : (
                        <span className="text-slate-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <Link to={`/analyses/${analysis.id}`}>
                        <Button variant="ghost" size="sm" className="text-blue-600 hover:text-blue-800">
                          View Details
                        </Button>
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
};
