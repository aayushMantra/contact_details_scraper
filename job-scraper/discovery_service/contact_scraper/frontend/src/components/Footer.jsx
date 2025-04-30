import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-white border-t border-secondary-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <p className="text-sm text-secondary-500">
            &copy; {new Date().getFullYear()} Contact Scraper. All rights reserved.
          </p>
          <div className="mt-4 md:mt-0 flex space-x-6">
            <a 
              href="#" 
              className="text-sm text-secondary-500 hover:text-primary-600 transition-colors"
            >
              Privacy Policy
            </a>
            <a 
              href="#" 
              className="text-sm text-secondary-500 hover:text-primary-600 transition-colors"
            >
              Terms of Service
            </a>
            <a 
              href="#" 
              className="text-sm text-secondary-500 hover:text-primary-600 transition-colors"
            >
              Contact
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
