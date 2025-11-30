FROM nginx:alpine

# Copy UI files
COPY . /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 6033

CMD ["nginx", "-g", "daemon off;"]
