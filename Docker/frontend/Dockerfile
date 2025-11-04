FROM nginx:1.25

RUN apt-get update && \
    apt-get install -y curl net-tools && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /front-end/formulavis
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

