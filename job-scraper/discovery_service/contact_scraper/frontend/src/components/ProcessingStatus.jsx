import React from 'react';
import { ArrowPathIcon, CheckCircleIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline';

const ProcessingStatus = ({ status, progress }) => {
  const getStatusContent = () => {
    switch (status) {
      case 'processing':
        return {
          icon: <ArrowPathIcon className="h-8 w-8 text-primary-500 animate-spin" />,
          title: 'Processing your file',
          description: 'This may take a few minutes depending on the file size.',
          progressBar: true,
        };
      case 'completed':
        return {
          icon: <CheckCircleIcon className="h-8 w-8 text-green-500" />,
          title: 'Processing complete!',
          description: 'Your file has been processed successfully.',
          progressBar: false,
        };
      case 'failed':
        return {
          icon: <ExclamationCircleIcon className="h-8 w-8 text-red-500" />,
          title: 'Processing failed',
          description: 'There was an error processing your file. Please try again.',
          progressBar: false,
        };
      default:
        return {
          icon: <ArrowPathIcon className="h-8 w-8 text-primary-500" />,
          title: 'Ready to process',
          description: 'Upload a file to begin processing.',
          progressBar: false,
        };
    }
  };

  const content = getStatusContent();

  return (
    <div className="w-full bg-white rounded-lg shadow-custom p-6">
      <div className="flex flex-col items-center text-center">
        {content.icon}
        <h3 className="mt-4 text-lg font-semibold text-secondary-800">{content.title}</h3>
        <p className="mt-1 text-sm text-secondary-500">{content.description}</p>
        
        {content.progressBar && (
          <div className="w-full mt-4">
            <div className="w-full bg-secondary-200 rounded-full h-2.5">
              <div 
                className="bg-primary-500 h-2.5 rounded-full transition-all duration-300" 
                style={{ width: `${progress || 0}%` }}
              ></div>
            </div>
            <p className="mt-1 text-xs text-secondary-500 text-right">{progress || 0}%</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProcessingStatus;
