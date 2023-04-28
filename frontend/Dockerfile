# Use the official Node.js image as the base image
FROM node:14

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json, and install the dependencies
COPY package.json package-lock.json ./
RUN npm i

# Copy the rest of the application code
COPY . .

# Expose the port the frontend will run on
EXPOSE 3000

# Start the frontend
CMD ["npm", "run", "dev"]
