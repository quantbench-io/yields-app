FROM python:3-alpine AS yields-backend
RUN pip install uv
COPY ./backend/uv.lock /backend/uv.lock
COPY ./backend/pyproject.toml /backend/pyproject.toml
COPY ./backend/src/backend/__init__.py /backend/src/backend/__init__.py
WORKDIR /backend
RUN uv sync

FROM node:26-alpine AS yields-frontend
COPY ./frontend-ts/package.json /frontend-ts/package.json
COPY ./frontend-ts/package-lock.json /frontend-ts/package-lock.json
WORKDIR /frontend-ts
RUN npm install
COPY ./frontend-ts /frontend-ts
WORKDIR /frontend-ts
RUN npm run build

FROM yields-backend
COPY ./backend /backend
RUN chmod +x /backend/docker-entrypoint.sh
COPY --from=yields-frontend /frontend-ts/dist/ /frontend-ts/dist
ENTRYPOINT ["/backend/docker-entrypoint.sh"]