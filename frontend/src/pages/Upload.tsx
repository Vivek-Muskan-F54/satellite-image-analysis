import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardBody } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Upload as UploadIcon, X, CheckCircle, Activity, Image as ImageIcon } from 'lucide-react';
import { imageApi, analysesApi } from '../services/api';

export const Upload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [isSuccess, setIsSuccess] = useState(false);
  const [uploadedImageId, setUploadedImageId] = useState<string | null>(null);

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
    setUploadedImageId(null);
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setProgress(0);
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await imageApi.upload(formData, (progressEvent) => {
        if (progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setProgress(percentCompleted);
        }
      });
      setUploadedImageId(res.data.id);
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

  const handleAnalyze = async () => {
    if (!uploadedImageId) return;
    setIsAnalyzing(true);
    setError('');
    try {
      const res = await analysesApi.create(uploadedImageId);
      navigate(`/analyses/${res.data.id}`);
    } catch (err: any) {
      setIsAnalyzing(false);
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Analysis failed. Please try again.');
      }
    }
  };

  if (isSuccess) {
    return (
      <div className="max-w-3xl mx-auto space-y-6 pt-12">
        <Card className="border-t-4 border-t-emerald-500">
          <CardBody className="text-center py-20 px-8">
            <div className="bg-emerald-50 rounded-full h-24 w-24 flex items-center justify-center mx-auto mb-6">
              <CheckCircle className="h-12 w-12 text-emerald-600" />
            </div>
            <h2 className="text-3xl font-bold text-slate-900 mb-3">Upload Successful</h2>
            <p className="text-slate-500 mb-10 text-lg max-w-lg mx-auto">
              Your satellite image has been securely saved. You can now initiate the AI land-cover classification.
            </p>
            {error && (
              <div className="mb-6 max-w-lg mx-auto bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md text-sm">
                {error}
              </div>
            )}
            <div className="flex flex-col sm:flex-row justify-center items-center space-y-4 sm:space-y-0 sm:space-x-4">
              <Button onClick={() => {
                setIsSuccess(false);
                clearFile();
              }} variant="secondary" className="w-full sm:w-auto text-base">
                Upload Another
              </Button>
              <Button
                onClick={handleAnalyze}
                disabled={isAnalyzing}
                className="w-full sm:w-auto text-base min-w-[200px]"
                size="lg"
              >
                {isAnalyzing ? (
                  <span className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Analyzing Image...
                  </span>
                ) : (
                  <span className="flex items-center">
                    <Activity className="h-5 w-5 mr-2" />
                    Analyze Image Now
                  </span>
                )}
              </Button>
            </div>
          </CardBody>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">New Analysis</h1>
        <p className="text-slate-500 mt-2">Upload a satellite image for AI-driven land cover classification.</p>
      </div>

      <Card>
        <CardBody className="p-8">
          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm flex items-center">
              <CheckCircle className="h-5 w-5 mr-2 hidden" />
              {error}
            </div>
          )}

          {!file ? (
            <div
              className="border-2 border-dashed border-blue-200 bg-slate-50 hover:bg-blue-50/50 hover:border-blue-400 rounded-2xl p-16 flex flex-col items-center justify-center text-center transition-all cursor-pointer group"
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="bg-white p-4 rounded-full shadow-sm mb-5 group-hover:scale-110 transition-transform">
                <UploadIcon className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-2">Click to upload or drag and drop</h3>
              <p className="text-slate-500 mb-2">Supported formats: JPEG, PNG, TIFF</p>
              <p className="text-slate-400 text-xs font-medium uppercase tracking-wider">Maximum file size: 10MB</p>
              <input
                type="file"
                className="hidden"
                ref={fileInputRef}
                onChange={handleChange}
                accept=".jpg,.jpeg,.png,.tif,.tiff,image/jpeg,image/png,image/tiff"
              />
            </div>
          ) : (
            <div className="border border-slate-200 bg-white rounded-2xl p-8 shadow-sm">
              <div className="flex flex-col md:flex-row items-center md:items-start justify-between gap-6">
                <div className="flex flex-col md:flex-row items-center md:items-start space-y-4 md:space-y-0 md:space-x-6 w-full">
                  <div className="h-32 w-32 bg-slate-100 rounded-xl flex items-center justify-center overflow-hidden flex-shrink-0 border border-slate-200">
                    {preview ? (
                      <img src={preview} alt="Preview" className="h-full w-full object-cover" />
                    ) : (
                      <ImageIcon className="h-10 w-10 text-slate-300" />
                    )}
                  </div>
                  <div className="text-center md:text-left flex-1 min-w-0">
                    <h3 className="text-lg font-semibold text-slate-900 break-all mb-1">{file.name}</h3>
                    <p className="text-slate-500 font-medium">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>

                    {isUploading && (
                      <div className="mt-4 w-full">
                        <div className="flex justify-between text-xs text-blue-600 font-medium mb-1">
                          <span>Uploading...</span>
                          <span>{progress}%</span>
                        </div>
                        <div className="w-full bg-blue-100 rounded-full h-2">
                          <div className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out" style={{ width: `${progress}%` }}></div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {!isUploading && (
                  <button onClick={clearFile} className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-full transition-colors self-end md:self-start">
                    <X className="h-6 w-6" />
                  </button>
                )}
              </div>

              {!isUploading && (
                <div className="mt-8 pt-6 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-end space-y-3 sm:space-y-0 sm:space-x-4">
                  <Button variant="ghost" onClick={clearFile} disabled={isUploading} className="w-full sm:w-auto text-slate-500">
                    Cancel
                  </Button>
                  <Button onClick={handleUpload} disabled={isUploading} className="w-full sm:w-auto min-w-[160px]" size="lg">
                    Upload Image
                  </Button>
                </div>
              )}
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  );
};
