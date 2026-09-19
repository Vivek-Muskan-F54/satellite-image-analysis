import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardBody } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { imageApi } from '../services/api';
import { Image as ImageIcon, Trash2, Eye } from 'lucide-react';

export const Analyses: React.FC = () => {
  const [images, setImages] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchImages();
  }, []);

  const fetchImages = async () => {
    try {
      const res = await imageApi.list();
      setImages(res.data.items);
    } catch (err) {
      setError('Failed to load image history.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this image?')) return;
    
    try {
      await imageApi.delete(id);
      setImages(images.filter(img => img.id !== id));
    } catch (err) {
      alert('Failed to delete image.');
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-slate-900">Analysis History</h1>
        <Link to="/upload">
          <Button>Upload New</Button>
        </Link>
      </div>
      
      <Card>
        <CardBody>
          {error && (
            <div className="mb-4 bg-red-50 text-red-600 p-3 rounded-md">{error}</div>
          )}
          
          {isLoading ? (
            <div className="text-center py-12 text-slate-500">Loading...</div>
          ) : images.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              <ImageIcon className="mx-auto h-12 w-12 text-slate-300 mb-3" />
              <p className="mb-2 text-lg">No images uploaded yet.</p>
              <Link to="/upload" className="text-blue-600 hover:underline">Upload your first image</Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200">
                <thead>
                  <tr>
                    <th className="px-4 py-3 bg-slate-50 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Filename</th>
                    <th className="px-4 py-3 bg-slate-50 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Upload Date</th>
                    <th className="px-4 py-3 bg-slate-50 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Size</th>
                    <th className="px-4 py-3 bg-slate-50 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Dimensions</th>
                    <th className="px-4 py-3 bg-slate-50 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Status</th>
                    <th className="px-4 py-3 bg-slate-50 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-slate-200">
                  {images.map((img) => (
                    <tr key={img.id}>
                      <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-slate-900 truncate max-w-[200px]">
                        {img.original_filename}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-slate-500">
                        {new Date(img.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-slate-500">
                        {(img.file_size / (1024 * 1024)).toFixed(2)} MB
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-slate-500">
                        {img.width && img.height ? `${img.width} × ${img.height}` : 'N/A'}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm">
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                          Uploaded
                        </span>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-right text-sm font-medium space-x-3">
                        <Link to={`/analyses/${img.id}`} className="text-blue-600 hover:text-blue-900 inline-flex items-center">
                          <Eye className="h-4 w-4 mr-1" /> View
                        </Link>
                        <button onClick={() => handleDelete(img.id)} className="text-red-600 hover:text-red-900 inline-flex items-center">
                          <Trash2 className="h-4 w-4 mr-1" /> Delete
                        </button>
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
