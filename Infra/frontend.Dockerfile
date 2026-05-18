# Use a lightweight Node.js 20 image
FROM node:20-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy package files first to cache the npm install step
COPY package.json package-lock.json* ./

# Clean install of all dependencies
RUN npm ci

# Copy the rest of your React/Vite code
COPY . .

# Expose the Vite dev server port
EXPOSE 5173

# Command to start the Vite dev server and expose it to the Docker network
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]