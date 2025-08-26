FROM node:alpine

RUN mkdir -p /frontend

WORKDIR /frontend

COPY package*.json /frontend

RUN npm install --legacy-peer-deps

COPY . /frontend

EXPOSE 3000

CMD ["npm", "run", "dev"]