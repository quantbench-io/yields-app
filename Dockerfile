FROM python:3-alpine AS backend
RUN pip install uv
COPY ./backend /backend
RUN chmod +x /backend/docker-entrypoint.sh
WORKDIR /backend
RUN uv sync

FROM node:26-alpine AS frontend
COPY ./frontend /frontend
WORKDIR /frontend
RUN npm install && npm run build

FROM backend
COPY --from=frontend /frontend/dist /frontend/dist
WORKDIR /backend
ENTRYPOINT ["/backend/docker-entrypoint.sh"]