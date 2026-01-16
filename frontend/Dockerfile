# Stage 1: Build the React App
FROM node:22-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve the App using a lightweight server (Nginx)
FROM nginx:alpine
# Copy the build output from Stage 1 to Nginx's serve folder
# Vite defaults to 'dist', check this matches your vite.config.ts defaults
COPY --from=build /app/dist /usr/share/nginx/html
# Expose port 80 (standard web port)
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
