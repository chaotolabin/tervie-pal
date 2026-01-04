# Build stage
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build
RUN npm run build

# Production stage with nginx
FROM nginx:alpine

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx config (sẽ tạo ở bước sau)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]