FROM python:3-alpine AS yields-backend
RUN pip install uv
COPY ./backend /backend
RUN chmod +x /backend/docker-entrypoint.sh
WORKDIR /backend
RUN uv sync

FROM node:26-alpine AS yields-frontend
COPY ./frontend-ts /frontend-ts
WORKDIR /frontend-ts
RUN npm install && npm run build

FROM yields-backend
COPY --from=yields-frontend /frontend-ts/dist /frontend-ts/dist
WORKDIR /backend
ENTRYPOINT ["/backend/docker-entrypoint.sh"]