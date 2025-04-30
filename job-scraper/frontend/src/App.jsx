import React, { useState, useEffect } from 'react';
import axios from 'axios';
import JobCard from './Components/JobCard';

function App() {
  const [jobs, setJobs] = useState([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

   // Get API URL from environment variables
   const API_URL = import.meta.env.VITE_API_URL || 'http://search:8005';

  useEffect(() => {
    fetchJobs();
  }, [page]);

  const fetchJobs = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log(`Fetching from: ${API_URL}/search?page=${page}&size=10`);
      const response = await axios.get(`${API_URL}/search`, {
        params: { page, size: 10 },
        timeout: 5000, // 10 seconds timeout
      });
      console.log('Response Data:', response.data);
      if (response.data && Array.isArray(response.data.data)) {
        setJobs(response.data.data); // Ensure this is an array
      } else {
        console.warn('Unexpected response format:', response.data);
        setJobs([]);
      }
      setTotal(response.data.total || 0);
    } catch (error) {
      console.error('Error fetching jobs:', error);
      setError('Failed to load jobs. Please check the backend or try again later.');
      setJobs([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (newPage) => {
    const totalPages = Math.ceil(total / 10);
    if (newPage > 0 && newPage <= totalPages) {
      setPage(newPage);
    }
  };

  return (
    <div className="container mx-auto p-4 bg-gray-100 min-h-screen">
      <header className="bg-primary text-white p-4 rounded-lg mb-6 shadow-md">
        <h1 className="text-2xl font-bold">Job Scraper Dashboard</h1>
      </header>
      {loading ? (
        <div className="flex justify-center">
          <div className="animate-spin h-10 w-10 border-4 border-t-primary border-gray-200 rounded-full"></div>
        </div>
      ) : error ? (
        <div className="text-center text-red-600">{error}</div>
      ) : jobs.length === 0 ? (
        <div className="text-center text-gray-600">No jobs found.</div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {jobs.map((job) => (
              <JobCard key={job.url} job={job} />
            ))}
          </div>
          <div className="mt-6 flex justify-center space-x-4">
            <button
              onClick={() => handlePageChange(page - 1)}
              disabled={page === 1}
              className="px-4 py-2 bg-gray-300 text-gray-800 rounded-lg disabled:opacity-50 hover:bg-gray-400 transition"
            >
              Previous
            </button>
            <span className="px-4 py-2 text-gray-800">{`Page ${page} of ${Math.ceil(total / 10)}`}</span>
            <button
              onClick={() => handlePageChange(page + 1)}
              disabled={page === Math.ceil(total / 10)}
              className="px-4 py-2 bg-primary text-white rounded-lg disabled:opacity-50 hover:bg-blue-600 transition"
            >
              Next
            </button>
          </div>
        </>
      )}
      <footer className="mt-6 text-center text-gray-600">
        Powered by <b>Shelly Saxena</b> &copy; {new Date().getFullYear()}
      </footer>
    </div>
  );
}

export default App;