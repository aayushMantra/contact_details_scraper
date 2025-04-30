# Use Node.js 18 as base image (compatible with React 18 and Vite)
FROM node:18-slim

# Set working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package.json ./

RUN npm install
RUN npm rebuild esbuild
RUN npm install esbuild@0.25.2 --save-exact

# Copy the rest of the application
COPY . .

# Create a .env file from environment variables at runtime
ARG VITE_API_URL=http://host.docker.internal:8005
RUN echo "VITE_API_URL=${VITE_API_URL}" > .env && \
    npm run build && \
    npm install -g serve

# Serve the build
CMD ["serve", "-s", "dist", "-l", "3000"]