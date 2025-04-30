import React from 'react';

function JobCard({ job }) {
  return (
    <div className="bg-white shadow-md rounded-lg p-4 hover:shadow-lg transition-shadow">
      <h2 className="text-xl font-bold text-gray-800">{job.title || 'Untitled Job'}</h2>
      <p className="text-gray-600">{(job.company || 'Unknown') + ', ' + (job.location || 'N/A')}</p>
      <p className="mt-2 text-gray-700">Salary: {job.salary || `~${job.salary_midpoint_usd || 'N/A'} USD`}</p>
      <p className="mt-1">
        <span className="inline-block bg-green-200 text-green-800 text-xs px-2 py-1 rounded-full">
          {job.posting_age_days || 0} days ago
        </span>
      </p>
      <a
        href={job.url || '#'}
        target="_blank"
        rel="noopener noreferrer"
        className="mt-2 inline-block text-primary hover:underline"
      >
        View Post
      </a>
    </div>
  );
}

export default JobCard;