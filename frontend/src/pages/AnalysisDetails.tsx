import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Card, CardHeader, CardBody } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { imageApi } from '../services/api';
import { ArrowLeft, Trash2, AlertCircle } from 'lucide-react';
import { apiClient } from '../services/api';

const ImagePreview: React.FC<{ imageId: string, originalFilename: string }> = ({ imageId, originalFilename }) => {
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

    fetchImage();

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
      alt={originalFilename}
      className="w-full h-auto object-contain max-h-[500px]"
    />
  );
};

export const AnalysisDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [image, setImage] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (id) {
      fetchImageDetails();
    }
  }, [id]);

  const fetchImageDetails = async () => {
    try {
      const res = await imageApi.get(id!);
      setImage(res.data);
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError('Image not found.');
      } else {
        setError('Failed to load image details.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this image?')) return;
    
    try {
      await imageApi.delete(id!);
      navigate('/analyses');
    } catch (err) {
      alert('Failed to delete image.');
    }
  };

  if (isLoading) {
    return <div className="p-8 text-slate-500">Loading...</div>;
  }

  if (error || !image) {
    return (
      <div className="p-8">
        <div className="bg-red-50 text-red-600 p-4 rounded-md mb-4">{error}</div>
        <Link to="/analyses" className="text-blue-600 hover:underline inline-flex items-center">
          <ArrowLeft className="h-4 w-4 mr-1" /> Back to History
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center space-x-4">
        <Link to="/analyses" className="p-2 text-slate-400 hover:bg-slate-100 rounded-full transition-colors">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <h1 className="text-2xl font-bold text-slate-900 truncate flex-1">{image.original_filename}</h1>
        <Button variant="outline" className="text-red-600 border-red-200 hover:bg-red-50" onClick={handleDelete}>
          <Trash2 className="h-4 w-4 mr-2 inline" /> Delete
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <h2 className="font-semibold text-slate-800">Image Preview</h2>
            </CardHeader>
            <CardBody>
              <div className="bg-slate-100 rounded-md flex flex-col items-center justify-center border border-slate-200 overflow-hidden min-h-[300px]">
                <ImagePreview imageId={image.id} originalFilename={image.original_filename} />
              </div>
            </CardBody>
          </Card>
          
          <Card>
            <CardHeader>
              <h2 className="font-semibold text-slate-800">Analysis Status</h2>
            </CardHeader>
            <CardBody>
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-md">
                <p className="text-blue-800 font-medium">Status: Uploaded</p>
                <p className="text-sm text-blue-600 mt-1">Image ingestion complete. Machine learning analysis will be implemented in future phases.</p>
              </div>
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
                <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Filename</p>
                <p className="text-sm font-medium text-slate-900 break-all">{image.original_filename}</p>
              </div>
              
              <div>
                <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Upload Date</p>
                <p className="text-sm text-slate-900">{new Date(image.created_at).toLocaleString()}</p>
              </div>
              
              <div>
                <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">File Size</p>
                <p className="text-sm text-slate-900">{(image.file_size / (1024 * 1024)).toFixed(2)} MB</p>
              </div>
              
              <div>
                <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Format</p>
                <p className="text-sm text-slate-900">{image.mime_type}</p>
              </div>
              
              <div>
                <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Dimensions</p>
                <p className="text-sm text-slate-900">{image.width && image.height ? `${image.width} × ${image.height} px` : 'Unknown'}</p>
              </div>
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  );
};
