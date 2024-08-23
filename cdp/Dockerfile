# cdp/Dockerfile

# Base image
FROM node:18-alpine

# Set working directory
WORKDIR /cdp

# Copy package.json and install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of the application
COPY . .

# Expose the port the server runs on
EXPOSE 3000

# Start the application
CMD ["node", "index.js"]
