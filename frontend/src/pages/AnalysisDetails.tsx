import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card, CardHeader, CardBody } from '../components/ui/Card';
import { StatusBadge } from '../components/ui/StatusBadge';
import { ConfidenceBar } from '../components/ui/ConfidenceBar';
import { imageApi, analysesApi, apiClient } from '../services/api';
import { ArrowLeft, AlertCircle, Calendar, Server, HardDrive, FileImage } from 'lucide-react';

const ImagePreview: React.FC<{ imageId: string }> = ({ imageId }) => {
  const [url, setUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let objectUrl: string | null = null;

    const fetchImage = async () => {
      try {
        const response = await apiClient.get(`/api/images/${imageId}/content`, {
          responseType: 'blob'
        });
        objectUrl = URL.createObjectURL(response.data);
        setUrl(objectUrl);
      } catch (err) {
        setError(true);
      } finally {
        setLoading(false);
      }
    };

    if (imageId) fetchImage();

    return () => {
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
    };
  }, [imageId]);

  if (loading) return (
    <div className="flex flex-col items-center justify-center py-20 text-slate-400">
      <svg className="animate-spin h-8 w-8 mb-4 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <p>Loading preview...</p>
    </div>
  );

  if (error || !url) return (
    <div className="flex flex-col items-center justify-center py-20 text-slate-400">
      <AlertCircle className="h-10 w-10 mb-3 opacity-50" />
      <p>Preview unavailable</p>
    </div>
  );

  return (
    <img
      src={url}
      alt="Satellite Image Preview"
      className="w-full h-auto object-contain max-h-[500px] transition-opacity duration-300 rounded-lg shadow-sm"
    />
  );
};

export const AnalysisDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  const [analysis, setAnalysis] = useState<any>(null);
  const [image, setImage] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (id) {
      fetchDetails();
    }
  }, [id]);

  const fetchDetails = async () => {
    try {
      const res = await analysesApi.get(id!);
      setAnalysis(res.data);
      const imgRes = await imageApi.get(res.data.image_id);
      setImage(imgRes.data);
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError('Analysis or Image not found.');
      } else {
        setError('Failed to load analysis details.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto py-12 flex flex-col items-center justify-center">
        <svg className="animate-spin h-10 w-10 text-blue-600 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p className="text-slate-500 font-medium">Loading analysis data...</p>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="max-w-3xl mx-auto mt-8">
        <div className="bg-red-50 border border-red-100 text-red-600 p-6 rounded-xl mb-6 shadow-sm flex items-center">
          <AlertCircle className="h-6 w-6 mr-3" />
          <p className="font-medium">{error}</p>
        </div>
        <Link to="/analyses" className="text-blue-600 hover:text-blue-800 font-medium inline-flex items-center transition-colors">
          <ArrowLeft className="h-4 w-4 mr-2" /> Back to History
        </Link>
      </div>
    );
  }

  const renderProbabilities = () => {
    if (!analysis.prediction || !analysis.prediction.probabilities) return null;
    const probs = analysis.prediction.probabilities;
    const predictedClass = analysis.prediction.predicted_class;

    const sortedClasses = Object.keys(probs).sort((a, b) => probs[b] - probs[a]);

    return (
      <div className="mt-8 pt-8 border-t border-slate-100">
        <h3 className="font-semibold text-slate-800 mb-6">Class Probabilities</h3>
        <div className="space-y-4">
          {sortedClasses.map((clsName) => (
            <ConfidenceBar
              key={clsName}
              label={clsName}
              confidence={probs[clsName]}
              isHighest={clsName === predictedClass}
            />
          ))}
        </div>
      </div>
    );
  };

  const renderResult = () => {
    if (analysis.status === 'COMPLETED' && analysis.prediction) {
      return (
        <div>
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-8 pb-8 border-b border-slate-100">
            <div>
              <p className="text-sm text-slate-500 font-medium uppercase tracking-wider mb-2">Predicted Class</p>
              <h2 className="text-4xl font-extrabold text-slate-900 tracking-tight">
                {analysis.prediction.predicted_class}
              </h2>
            </div>
            <div className="mt-4 md:mt-0 bg-blue-50 px-6 py-4 rounded-xl border border-blue-100">
              <p className="text-sm text-blue-600 font-semibold uppercase tracking-wider mb-1">Confidence</p>
              <p className="text-3xl font-bold text-blue-700">
                {(analysis.prediction.confidence * 100).toFixed(1)}%
              </p>
            </div>
          </div>
          {renderProbabilities()}
        </div>
      );
    }

    if (analysis.status === 'FAILED') {
      return (
        <div className="py-6 flex flex-col items-center justify-center text-center">
          <div className="bg-red-50 p-4 rounded-full mb-4">
            <AlertCircle className="h-10 w-10 text-red-500" />
          </div>
          <h2 className="text-xl font-bold text-slate-900 mb-2">Analysis Failed</h2>
          <p className="text-slate-600 max-w-md">{analysis.error_message || 'An error occurred during inference. Please try uploading the image again.'}</p>
        </div>
      );
    }

    return (
      <div className="py-12 flex flex-col items-center justify-center text-center">
        <svg className="animate-spin h-10 w-10 text-blue-500 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <h2 className="text-xl font-bold text-slate-900 mb-2">Analysis in Progress</h2>
        <p className="text-slate-500">The machine learning model is currently processing this image...</p>
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center space-x-4">
        <Link to="/analyses" className="p-2.5 text-slate-500 hover:text-slate-900 hover:bg-slate-200/50 rounded-full transition-all">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div className="flex-1">
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              Analysis Details
            </h1>
            <StatusBadge status={analysis.status} />
          </div>
          <p className="text-sm text-slate-500 mt-1">ID: <span className="font-mono">{analysis.id}</span></p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        <div className="lg:col-span-2 space-y-8">
          <Card>
            <CardBody className="p-8">
              {renderResult()}
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <h2 className="font-semibold text-slate-900">Source Image</h2>
            </CardHeader>
            <CardBody className="bg-slate-50 p-6">
              <div className="rounded-lg overflow-hidden flex items-center justify-center">
                <ImagePreview imageId={analysis.image_id} />
              </div>
            </CardBody>
          </Card>
        </div>

        <div className="space-y-6 lg:sticky lg:top-24">
          <Card>
            <CardHeader>
              <h2 className="font-semibold text-slate-900">Metadata</h2>
            </CardHeader>
            <CardBody className="p-0">
              <div className="divide-y divide-slate-100">
                <div className="p-5 flex items-start space-x-4">
                  <Server className="h-5 w-5 text-slate-400 mt-0.5" />
                  <div>
                    <p className="text-xs text-slate-500 font-semibold uppercase tracking-wider mb-1">Model Version</p>
                    <p className="text-sm font-medium text-slate-900">{analysis.model_version}</p>
                  </div>
                </div>

                <div className="p-5 flex items-start space-x-4">
                  <Calendar className="h-5 w-5 text-slate-400 mt-0.5" />
                  <div>
                    <p className="text-xs text-slate-500 font-semibold uppercase tracking-wider mb-1">Analysis Date</p>
                    <p className="text-sm font-medium text-slate-900">
                      {new Date(analysis.created_at).toLocaleDateString(undefined, {
                        year: 'numeric', month: 'long', day: 'numeric'
                      })}
                    </p>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {new Date(analysis.created_at).toLocaleTimeString()}
                    </p>
                  </div>
                </div>

                {image && (
                  <>
                    <div className="p-5 flex items-start space-x-4 bg-slate-50/50">
                      <FileImage className="h-5 w-5 text-slate-400 mt-0.5" />
                      <div className="overflow-hidden">
                        <p className="text-xs text-slate-500 font-semibold uppercase tracking-wider mb-1">Image Name</p>
                        <p className="text-sm font-medium text-slate-900 truncate" title={image.original_filename}>
                          {image.original_filename}
                        </p>
                      </div>
                    </div>
                    <div className="p-5 flex items-start space-x-4 bg-slate-50/50 rounded-b-xl">
                      <HardDrive className="h-5 w-5 text-slate-400 mt-0.5" />
                      <div>
                        <p className="text-xs text-slate-500 font-semibold uppercase tracking-wider mb-1">File Size</p>
                        <p className="text-sm font-medium text-slate-900">
                          {(image.file_size / (1024 * 1024)).toFixed(2)} MB
                        </p>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  );
};
