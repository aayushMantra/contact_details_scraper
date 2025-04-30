import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { CloudArrowUpIcon, DocumentTextIcon, XMarkIcon } from '@heroicons/react/24/outline';

const FileUpload = ({ onFileSelect }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  
  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      setSelectedFile(file);
      onFileSelect(file);
    }
  }, [onFileSelect]);
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
    },
    maxFiles: 1,
  });
  
  const removeFile = () => {
    setSelectedFile(null);
    onFileSelect(null);
  };
  
  return (
    <div className="w-full">
      <div 
        {...getRootProps()} 
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200 ${
          isDragActive 
            ? 'border-primary-500 bg-primary-50' 
            : 'border-secondary-300 hover:border-primary-400 hover:bg-secondary-50'
        }`}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center justify-center space-y-3">
          <CloudArrowUpIcon className={`h-12 w-12 ${isDragActive ? 'text-primary-500' : 'text-secondary-400'}`} />
          <p className="text-lg font-medium text-secondary-700">
            {isDragActive ? 'Drop the file here' : 'Drag & drop a CSV/Excel file here'}
          </p>
          <p className="text-sm text-secondary-500">or click to browse files</p>
          <p className="text-xs text-secondary-400 mt-2">
            Supported formats: .csv, .xls, .xlsx
          </p>
        </div>
      </div>
      
      {selectedFile && (
        <div className="mt-4 p-3 bg-secondary-100 rounded-lg flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <DocumentTextIcon className="h-6 w-6 text-primary-500" />
            <div>
              <p className="text-sm font-medium text-secondary-700">{selectedFile.name}</p>
              <p className="text-xs text-secondary-500">
                {(selectedFile.size / 1024).toFixed(2)} KB
              </p>
            </div>
          </div>
          <button 
            onClick={removeFile}
            className="p-1 rounded-full hover:bg-secondary-200 text-secondary-500"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>
      )}
    </div>
  );
};

export default FileUpload;