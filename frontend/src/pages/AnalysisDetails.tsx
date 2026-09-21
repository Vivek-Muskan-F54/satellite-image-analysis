import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card, CardHeader, CardBody } from '../components/ui/Card';
import { imageApi, analysesApi, apiClient } from '../services/api';
import { ArrowLeft, AlertCircle } from 'lucide-react';

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

  if (loading) return <div className="text-slate-500 py-12">Loading preview...</div>;
  if (error || !url) return (
    <div className="text-slate-400 py-12 flex flex-col items-center">
      <AlertCircle className="h-10 w-10 mb-2 opacity-50" />
      <p>Preview unavailable</p>
    </div>
  );

  return (
    <img
      src={url}
      alt="Satellite Image"
      className="w-full h-auto object-contain max-h-[500px]"
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
    return <div className="p-8 text-slate-500">Loading...</div>;
  }

  if (error || !analysis) {
    return (
      <div className="p-8">
        <div className="bg-red-50 text-red-600 p-4 rounded-md mb-4">{error}</div>
        <Link to="/analyses" className="text-blue-600 hover:underline inline-flex items-center">
          <ArrowLeft className="h-4 w-4 mr-1" /> Back to History
        </Link>
      </div>
    );
  }

  const renderProbabilities = () => {
    if (!analysis.prediction || !analysis.prediction.probabilities) return null;
    const probs = analysis.prediction.probabilities;

    // Sort probabilities descending
    const sortedClasses = Object.keys(probs).sort((a, b) => probs[b] - probs[a]);

    return (
      <div className="space-y-3 mt-4">
        <h3 className="font-semibold text-slate-700 text-sm mb-2 uppercase tracking-wide">Class Probabilities</h3>
        {sortedClasses.map((clsName) => {
          const prob = probs[clsName];
          const percent = (prob * 100).toFixed(1);
          return (
            <div key={clsName} className="flex items-center text-sm">
              <div className="w-32 truncate pr-2 text-slate-600">{clsName}</div>
              <div className="flex-1">
                <div className="w-full bg-slate-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${percent}%` }}></div>
                </div>
              </div>
              <div className="w-16 text-right text-slate-500 text-xs ml-2">{percent}%</div>
            </div>
          )
        })}
      </div>
    );
  };

  const getStatusDisplay = () => {
    if (analysis.status === 'COMPLETED') {
      return (
        <div className="p-4 bg-green-50 border border-green-200 rounded-md">
          <p className="text-green-800 font-medium">Status: Completed</p>
          <div className="mt-2 text-sm text-green-700">
            <p><strong>Predicted Class:</strong> {analysis.prediction?.predicted_class}</p>
            <p><strong>Confidence:</strong> {(analysis.prediction?.confidence * 100).toFixed(1)}%</p>
          </div>
          {renderProbabilities()}
        </div>
      );
    }

    if (analysis.status === 'FAILED') {
      return (
        <div className="p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-800 font-medium">Status: Failed</p>
          <p className="text-sm text-red-600 mt-1">{analysis.error_message || 'An error occurred during analysis.'}</p>
        </div>
      );
    }

    return (
      <div className="p-4 bg-blue-50 border border-blue-200 rounded-md">
        <p className="text-blue-800 font-medium">Status: {analysis.status}</p>
        <p className="text-sm text-blue-600 mt-1">Machine learning analysis is currently running.</p>
      </div>
    );
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center space-x-4">
        <Link to="/analyses" className="p-2 text-slate-400 hover:bg-slate-100 rounded-full transition-colors">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <h1 className="text-2xl font-bold text-slate-900 truncate flex-1">
          Analysis Details
        </h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <h2 className="font-semibold text-slate-800">Image Preview</h2>
            </CardHeader>
            <CardBody>
              <div className="bg-slate-100 rounded-md flex flex-col items-center justify-center border border-slate-200 overflow-hidden min-h-[300px]">
                <ImagePreview imageId={analysis.image_id} />
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <h2 className="font-semibold text-slate-800">Analysis Result</h2>
            </CardHeader>
            <CardBody>
              {getStatusDisplay()}
            </CardBody>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <h2 className="font-semibold text-slate-800">Metadata</h2>
            </CardHeader>
            <CardBody className="space-y-4">
              <div>
                <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Model Version</p>
                <p className="text-sm font-medium text-slate-900 break-all">{analysis.model_version}</p>
              </div>

              <div>
                <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Analysis Date</p>
                <p className="text-sm text-slate-900">{new Date(analysis.created_at).toLocaleString()}</p>
              </div>

              {image && (
                <>
                  <div className="mt-4 pt-4 border-t border-slate-100">
                    <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-2">Image Info</p>
                    <p className="text-sm text-slate-900 break-all">{image.original_filename}</p>
                    <p className="text-sm text-slate-500 mt-1">{(image.file_size / (1024 * 1024)).toFixed(2)} MB</p>
                  </div>
                </>
              )}
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  );
};
