import React, { useState, useEffect } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import Header from './components/Header';
import Footer from './components/Footer';
import FileUpload from './components/FileUpload';
import ProcessingStatus from './components/ProcessingStatus';
import { uploadCSV, getProcessingStatus, downloadProcessedFile } from './services/api';
import { ArrowDownTrayIcon } from '@heroicons/react/24/outline';

function App() {
  const [file, setFile] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState('idle');
  const [progress, setProgress] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);

  // Poll for status updates when a job is processing
  useEffect(() => {
    let interval;
    
    if (jobId && status === 'processing') {
      interval = setInterval(async () => {
        try {
          const response = await getProcessingStatus(jobId);
          setProgress(response.progress);
          
          if (response.status === 'completed') {
            setStatus('completed');
            clearInterval(interval);
            toast.success('Your file has been processed successfully!');
            // Auto-download the file
            handleDownload();
          } else if (response.status === 'failed') {
            setStatus('failed');
            clearInterval(interval);
            toast.error('Processing failed. Please try again.');
          }
        } catch (error) {
          console.error('Error checking status:', error);
          toast.error('Error checking processing status');
          setStatus('failed');
          clearInterval(interval);
        }
      }, 3000);
    }
    
    return () => {
      clearInterval(interval);
    };
  }, [jobId, status]);

  const handleFileSelect = (selectedFile) => {
    setFile(selectedFile);
    // Reset state when a new file is selected
    setJobId(null);
    setStatus('idle');
    setProgress(0);
    console.log("File selected:", selectedFile);
  };

  const handleUpload = async () => {
    if (!file) {
      toast.error('Please select a file first');
      return;
    }
    
    setIsProcessing(true);
    setStatus('processing');
    setProgress(0);
    console.log("Starting upload for file:", file.name);
    
    try {
      const response = await uploadCSV(file);
      setJobId(response.jobId);
      console.log("Upload response:", response);
      toast.success('File uploaded successfully!');
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Error uploading file. Please try again.');
      setStatus('failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownload = async () => {
    if (!jobId) return;
    
    try {
      await downloadProcessedFile(jobId);
      toast.success('File downloaded successfully!');
    } catch (error) {
      console.error('Download error:', error);
      toast.error('Error downloading file. Please try again.');
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-secondary-50">
      <Toaster position="top-right" />
      <Header />
      
      <main className="flex-grow">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold text-secondary-900">Contact Information Scraper</h2>
            <p className="mt-3 text-lg text-secondary-600">
              Upload a CSV file with website URLs and we'll extract contact information and social media links.
            </p>
          </div>
          
          <div className="bg-white rounded-lg shadow-custom p-6 mb-8">
            <h3 className="text-xl font-semibold text-secondary-800 mb-4">Upload Your File</h3>
            <FileUpload onFileSelect={handleFileSelect} />
            
            <div className="mt-6 flex justify-end">
              <button
                onClick={handleUpload}
                disabled={!file || isProcessing || status === 'processing'}
                className={`px-4 py-2 rounded-md text-white font-medium ${
                  !file || isProcessing || status === 'processing'
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
                }`}
              >
                {isProcessing ? 'Uploading...' : 'Process File'}
              </button>
            </div>

          </div>
          
          <ProcessingStatus status={status} progress={progress} />
          
          {status === 'completed' && (
            <div className="mt-8 text-center">
              <button
                onClick={handleDownload}
                className="inline-flex items-center px-4 py-2 rounded-md text-white font-medium bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
                Download Processed File
              </button>
              <p className="mt-2 text-sm text-secondary-500">
                Your file has been processed and is ready for download.
              </p>
            </div>
          )}
          
          <div className="mt-12 bg-white rounded-lg shadow-custom p-6">
            <h3 className="text-xl font-semibold text-secondary-800 mb-4">How It Works</h3>
            <div className="space-y-4">
              <div className="flex items-start">
                <div className="flex-shrink-0 h-6 w-6 rounded-full bg-primary-100 flex items-center justify-center">
                  <span className="text-sm font-medium text-primary-800">1</span>
                </div>
                <p className="ml-3 text-secondary-600">
                  Upload a CSV file containing a list of website URLs in the first column.
                </p>
              </div>
              <div className="flex items-start">
                <div className="flex-shrink-0 h-6 w-6 rounded-full bg-primary-100 flex items-center justify-center">
                  <span className="text-sm font-medium text-primary-800">2</span>
                </div>
                <p className="ml-3 text-secondary-600">
                  Our system will visit each website and extract email addresses and social media links.
                </p>
              </div>
              <div className="flex items-start">
                <div className="flex-shrink-0 h-6 w-6 rounded-full bg-primary-100 flex items-center justify-center">
                  <span className="text-sm font-medium text-primary-800">3</span>
                </div>
                <p className="ml-3 text-secondary-600">
                  Download the processed CSV file with all the extracted contact information.
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  );
}

export default App;