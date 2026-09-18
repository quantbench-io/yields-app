FROM python:3-alpine AS yields-backend
RUN pip install uv
COPY ./backend /backend
RUN chmod +x /backend/docker-entrypoint.sh
WORKDIR /backend
RUN uv sync

FROM node:26-alpine AS yields-frontend
COPY ./frontend-js /frontend-js
WORKDIR /frontend-js
RUN npm install && npm run build

FROM yields-backend
COPY --from=yields-frontend /frontend-js/dist /frontend-js/dist
WORKDIR /backend
ENTRYPOINT ["/backend/docker-entrypoint.sh"]