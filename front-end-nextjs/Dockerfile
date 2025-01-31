FROM node:18-alpine

WORKDIR /usr/src/app

# Install dependencies first
COPY package*.json ./
RUN npm install

# Copy rest of the application
COPY . .

# Expose port
EXPOSE 3000

# Start development server
CMD ["npm", "run", "dev"]