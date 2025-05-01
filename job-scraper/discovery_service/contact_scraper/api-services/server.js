const express = require('express');
const multer = require('multer');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const app = express();
const port = process.env.PORT || 8006;
app.listen(port, '0.0.0.0', () => {
    console.log(`Server running on port ${port}`);
  });
    

// Configure CORS
app.use(cors());
app.use(express.json());

// Configure file upload storage
const uploadDir = process.env.UPLOAD_DIR || path.join(__dirname, 'uploads');
const outputDir = process.env.OUTPUT_DIR || path.join(__dirname, 'output');

// Ensure directories exist
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, uploadDir);
  },
  filename: function (req, file, cb) {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + '.csv');
  }
});

const upload = multer({ 
  storage: storage,
  fileFilter: function (req, file, cb) {
    // Accept only CSV files
    if (file.mimetype !== 'text/csv' && !file.originalname.endsWith('.csv')) {
      return cb(new Error('Only CSV files are allowed'));
    }
    cb(null, true);
  },
  limits: {
    fileSize: 10 * 1024 * 1024 // 10MB limit
  }
});

// Store jobs in memory (in production, use a database)
const jobs = {};

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy' });
});

// Upload endpoint
app.post('/upload', upload.single('file'), (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const jobId = Date.now().toString();
    const inputPath = req.file.path;
    const outputPath = path.join(outputDir, `output_${jobId}.csv`);
    
    console.log(`Job ${jobId} created. Input: ${inputPath}, Output: ${outputPath}`);
    
    // Store job information
    jobs[jobId] = {
      id: jobId,
      status: 'processing',
      inputPath: inputPath,
      outputPath: outputPath,
      startTime: new Date(),
      progress: 0,
      error: null
    };

    // Start processing in background
    processFile(jobId, inputPath, outputPath);
    
    return res.status(200).json({ 
      jobId: jobId,
      message: 'File uploaded successfully and processing started'
    });
  } catch (error) {
    console.error('Upload error:', error);
    return res.status(500).json({ error: 'Server error during upload' });
  }
});

// Status endpoint
app.get('/status/:jobId', (req, res) => {
  const { jobId } = req.params;
  
  if (!jobs[jobId]) {
    return res.status(404).json({ error: 'Job not found' });
  }
  
  // Check if the output file exists to verify completion
  if (jobs[jobId].status === 'processing') {
    if (fs.existsSync(jobs[jobId].outputPath)) {
      jobs[jobId].status = 'completed';
      jobs[jobId].progress = 100;
      jobs[jobId].endTime = new Date();
    }
  }
  
  return res.status(200).json({
    id: jobs[jobId].id,
    status: jobs[jobId].status,
    progress: jobs[jobId].progress,
    startTime: jobs[jobId].startTime,
    endTime: jobs[jobId].endTime || null,
    error: jobs[jobId].error
  });
});

// List all jobs
app.get('/jobs', (req, res) => {
  const jobList = Object.values(jobs).map(job => ({
    id: job.id,
    status: job.status,
    progress: job.progress,
    startTime: job.startTime,
    endTime: job.endTime || null
  }));
  
  return res.status(200).json(jobList);
});

// Download endpoint
app.get('/download/:jobId', (req, res) => {
  const { jobId } = req.params;
  
  if (!jobs[jobId]) {
    return res.status(404).json({ error: 'Job not found' });
  }
  
  if (jobs[jobId].status !== 'completed') {
    return res.status(400).json({ error: 'Job not completed yet' });
  }
  
  if (!fs.existsSync(jobs[jobId].outputPath)) {
    return res.status(404).json({ error: 'Output file not found' });
  }
  
  res.download(jobs[jobId].outputPath, `contact_data_${jobId}.csv`);
});

// Function to process the file using the scraper
function processFile(jobId, inputPath, outputPath) {
  console.log(`Processing job ${jobId}...`);
  jobs[jobId].progress = 10;
  
  try {
    // For Heroku deployment, we'll use a simulated process
    // In a real environment with Docker, you would use the actual scraper
    
    // Simulate processing stages
    setTimeout(() => {
      jobs[jobId].progress = 30;
      console.log(`Job ${jobId} progress: 30%`);
      
      setTimeout(() => {
        jobs[jobId].progress = 60;
        console.log(`Job ${jobId} progress: 60%`);
        
        setTimeout(() => {
          // Create a sample output file if in development/test mode
          if (process.env.NODE_ENV !== 'production') {
            const sampleData = 'url,emails,linkedin,twitter,facebook\n' +
                              'https://example.com,info@example.com,https://linkedin.com/company/example,https://twitter.com/example,https://facebook.com/example\n' +
                              'https://sample.org,contact@sample.org,https://linkedin.com/company/sample,https://twitter.com/sample,https://facebook.com/sample';
            
            fs.writeFileSync(outputPath, sampleData);
          }
          
          // Check if the output file exists
          if (fs.existsSync(outputPath)) {
            jobs[jobId].status = 'completed';
            jobs[jobId].progress = 100;
            jobs[jobId].endTime = new Date();
            console.log(`Job ${jobId} completed successfully`);
          } else {
            jobs[jobId].status = 'failed';
            jobs[jobId].error = 'Output file was not created';
            console.error(`Job ${jobId} failed: Output file was not created`);
          }
        }, 5000);
      }, 5000);
    }, 5000);
    
    // Uncomment this section to use the actual scraper in a Docker environment
    /*
    const scrapy = spawn('python', [
      '-m',
      'scrapy',
      'crawl',
      'contact_spider',
      '-a', `csv_file=${inputPath}`,
      '-o', outputPath
    ], {
      cwd: process.env.SCRAPER_DIR || '/app'
    });
    
    scrapy.stdout.on('data', (data) => {
      console.log(`Scraper output: ${data}`);
      // Update progress based on output
      if (data.includes('Crawled')) {
        jobs[jobId].progress = Math.min(jobs[jobId].progress + 5, 90);
      }
    });
    
    scrapy.stderr.on('data', (data) => {
      console.error(`Scraper error: ${data}`);
    });
    
    scrapy.on('close', (code) => {
      console.log(`Scraper process exited with code ${code}`);
      if (code === 0) {
        jobs[jobId].status = 'completed';
        jobs[jobId].progress = 100;
        jobs[jobId].endTime = new Date();
      } else {
        jobs[jobId].status = 'failed';
        jobs[jobId].error = `Process exited with code ${code}`;
      }
    });
    */
  } catch (error) {
    console.error(`Error processing job ${jobId}:`, error);
    jobs[jobId].status = 'failed';
    jobs[jobId].error = error.message;
  }
}

// Clean up old jobs and files periodically (every hour)
setInterval(() => {
  const now = new Date();
  const jobIds = Object.keys(jobs);
  
  jobIds.forEach(jobId => {
    const job = jobs[jobId];
    // Remove jobs older than 24 hours
    if (job.startTime && (now - new Date(job.startTime)) > 24 * 60 * 60 * 1000) {
      console.log(`Cleaning up job ${jobId}`);
      
      // Delete input file
      if (job.inputPath && fs.existsSync(job.inputPath)) {
        fs.unlinkSync(job.inputPath);
      }
      
      // Delete output file if it's older than 24 hours
      if (job.outputPath && fs.existsSync(job.outputPath)) {
        const stats = fs.statSync(job.outputPath);
        if ((now - stats.mtime) > 24 * 60 * 60 * 1000) {
          fs.unlinkSync(job.outputPath);
        }
      }
      
      // Remove job from memory
      delete jobs[jobId];
    }
  });
}, 60 * 60 * 1000); // Run every hour

// Start the server
app.listen(port, () => {
  console.log(`API server running on port ${port}`);
});