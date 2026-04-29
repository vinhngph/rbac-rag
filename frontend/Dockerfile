# ---- BUILD STAGE ----
FROM dhi.io/node:25-debian13-sfw-dev AS builder

WORKDIR /app

COPY package*.json ./

RUN npm install --legacy-peer-deps

COPY . .

RUN npm run build

# ---- PRODUCTION STAGE ----
FROM dhi.io/nginx:1.30

COPY --chown=nginx:nginx --from=builder /app/dist /usr/share/nginx/html

COPY --chown=nginx:nginx nginx.conf /etc/nginx/conf.d/default.conf