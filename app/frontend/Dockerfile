# 1. aşama: statik dosyaları üret
FROM node:24-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# 2. aşama: sadece build çıktısını Nginx ile servis et (root olmadan, 8080 portunda)
FROM nginxinc/nginx-unprivileged:1.30-alpine

# Base image'dan sonra yayınlanan güvenlik düzeltmelerini al, sonra tekrar root olmayan kullanıcıya dön
USER root
RUN apk upgrade --no-cache
USER 101

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 8080
