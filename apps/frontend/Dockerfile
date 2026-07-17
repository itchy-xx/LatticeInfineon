FROM node:20-alpine
WORKDIR /workspace
COPY package.json apps/frontend/package.json ./
RUN npm install
COPY apps/frontend apps/frontend
WORKDIR /workspace/apps/frontend
CMD ["npm","run","dev"]
