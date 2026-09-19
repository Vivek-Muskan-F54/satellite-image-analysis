import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardBody } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Upload as UploadIcon, X, Image as ImageIcon, CheckCircle } from 'lucide-react';
import { imageApi } from '../services/api';

export const Upload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [isSuccess, setIsSuccess] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const handleFile = (selectedFile: File) => {
    setError('');
    
    // Client-side validation
    const allowedTypes = ['image/jpeg', 'image/png', 'image/tiff'];
    if (!allowedTypes.includes(selectedFile.type)) {
      setError('Invalid file type. Only JPEG, PNG, and TIFF are supported.');
      return;
    }
    
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (selectedFile.size > maxSize) {
      setError('File is too large. Maximum size is 10MB.');
      return;
    }
    
    setFile(selectedFile);
    
    // Generate preview
    const objectUrl = URL.createObjectURL(selectedFile);
    setPreview(objectUrl);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
  };

  const clearFile = () => {
    setFile(null);
    if (preview) {
      URL.revokeObjectURL(preview);
      setPreview(null);
    }
    setProgress(0);
    setError('');
  };

  const handleUpload = async () => {
    if (!file) return;
    
    setIsUploading(true);
    setProgress(0);
    setError('');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      await imageApi.upload(formData, (progressEvent) => {
        if (progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setProgress(percentCompleted);
        }
      });
      setIsSuccess(true);
    } catch (err: any) {
      setIsUploading(false);
      setProgress(0);
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Upload failed. Please try again.');
      }
    }
  };

  if (isSuccess) {
    return (
      <div className="max-w-3xl mx-auto space-y-6">
        <Card>
          <CardBody className="text-center py-16">
            <CheckCircle className="mx-auto h-16 w-16 text-green-500 mb-4" />
            <h2 className="text-2xl font-bold text-slate-900 mb-2">Upload successful</h2>
            <p className="text-slate-600 mb-8">
              Image uploaded successfully. Analysis will be available in the next processing phase.
            </p>
            <div className="space-x-4">
              <Button onClick={() => navigate('/analyses')} variant="outline">
                View History
              </Button>
              <Button onClick={() => {
                setIsSuccess(false);
                clearFile();
              }}>
                Upload Another
              </Button>
            </div>
          </CardBody>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Upload Satellite Imagery</h1>
      
      <Card>
        <CardBody>
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md text-sm">
              {error}
            </div>
          )}

          {!file ? (
            <div 
              className="border-2 border-dashed border-slate-300 rounded-lg p-12 text-center hover:bg-slate-50 transition-colors cursor-pointer"
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <UploadIcon className="mx-auto h-12 w-12 text-slate-400 mb-4" />
              <p className="text-slate-600 font-medium mb-1">Click to upload or drag and drop</p>
              <p className="text-slate-500 text-sm">JPEG, PNG, or TIFF (max. 10MB)</p>
              <input 
                type="file" 
                className="hidden" 
                ref={fileInputRef} 
                onChange={handleChange}
                accept=".jpg,.jpeg,.png,.tif,.tiff,image/jpeg,image/png,image/tiff"
              />
            </div>
          ) : (
            <div className="border border-slate-200 rounded-lg p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-4">
                  <div className="h-24 w-24 bg-slate-100 rounded flex items-center justify-center overflow-hidden flex-shrink-0">
                    {preview ? (
                      <img src={preview} alt="Preview" className="h-full w-full object-cover" />
                    ) : (
                      <ImageIcon className="h-8 w-8 text-slate-400" />
                    )}
                  </div>
                  <div>
                    <h3 className="font-medium text-slate-900 break-all">{file.name}</h3>
                    <p className="text-sm text-slate-500 mt-1">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
                  </div>
                </div>
                {!isUploading && (
                  <button onClick={clearFile} className="text-slate-400 hover:text-red-500">
                    <X className="h-5 w-5" />
                  </button>
                )}
              </div>
              
              <div className="mt-8 flex items-center justify-end space-x-4">
                <Button variant="outline" onClick={clearFile} disabled={isUploading}>
                  Cancel
                </Button>
                <Button onClick={handleUpload} disabled={isUploading} className="min-w-[120px]">
                  {isUploading ? `Uploading ${progress}%` : 'Upload'}
                </Button>
              </div>
              
              {isUploading && (
                <div className="mt-4 w-full bg-slate-200 rounded-full h-1.5">
                  <div className="bg-blue-600 h-1.5 rounded-full transition-all duration-300" style={{ width: `${progress}%` }}></div>
                </div>
              )}
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  );
};
