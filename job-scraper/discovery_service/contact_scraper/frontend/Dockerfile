# job-scraper/discovery_service/contact_scraper/frontend/Dockerfile
# job-scraper/discovery_service/contact_scraper/frontend/Dockerfile
# Build stage
FROM node:18-slim as build

WORKDIR /app

# Install necessary build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a new React app as a base
RUN npx create-react-app my-app

# Move to the app directory
WORKDIR /app/my-app

# Install dependencies required by your components
RUN npm install axios react-hot-toast @headlessui/react @heroicons/react react-dropzone

# Install Tailwind CSS
RUN npm install -D tailwindcss@3.3.3 postcss@8.4.27 autoprefixer@10.4.14

# Initialize Tailwind CSS
RUN npx tailwindcss init -p && \
    sed -i 's/content: \[\]/content: \["\.\/src\/\*\*\/\*\.{js,jsx,ts,tsx}", "\.\/public\/index.html"\]/' tailwind.config.js

# Remove the default src directory to replace with your code
RUN rm -rf ./src

# Create src directory
RUN mkdir -p ./src/components ./src/services

# Copy your existing React components
COPY ./src/index.js ./src/
COPY ./src/index.css ./src/
COPY ./src/App.jsx ./src/
COPY ./src/App.css ./src/
COPY ./src/components/FileUpload.jsx ./src/components/
COPY ./src/components/ProcessingStatus.jsx ./src/components/
COPY ./src/components/Header.jsx ./src/components/
COPY ./src/components/Footer.jsx ./src/components/
COPY ./src/services/api.js ./src/services/
COPY ./tailwind.config.js ./

# If index.js doesn't exist, create it
RUN if [ ! -f ./src/index.js ]; then \
    echo "import React from 'react';" > ./src/index.js && \
    echo "import ReactDOM from 'react-dom/client';" >> ./src/index.js && \
    echo "import './index.css';" >> ./src/index.js && \
    echo "import App from './App';" >> ./src/index.js && \
    echo "const root = ReactDOM.createRoot(document.getElementById('root'));" >> ./src/index.js && \
    echo "root.render(" >> ./src/index.js && \
    echo "  <React.StrictMode>" >> ./src/index.js && \
    echo "    <App />" >> ./src/index.js && \
    echo "  </React.StrictMode>" >> ./src/index.js && \
    echo ");" >> ./src/index.js; \
    fi

# Set environment variables
ARG REACT_APP_API_URL=http://localhost:8007
ENV REACT_APP_API_URL=${REACT_APP_API_URL}

# Update API URL in the api.js file - FIXED SED COMMAND
RUN sed -i 's#const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8006"#const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8007"#g' ./src/services/api.js || true

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy the build output
COPY --from=build /app/my-app/build/ /usr/share/nginx/html/

# Create nginx configuration
RUN echo 'server { \
    listen 80; \
    client_max_body_size 10M; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg)$ { \
        root /usr/share/nginx/html; \
        expires 1y; \
        add_header Cache-Control "public, max-age=31536000"; \
        access_log off; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]