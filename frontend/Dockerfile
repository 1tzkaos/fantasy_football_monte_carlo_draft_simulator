FROM node:alpine

RUN mkdir -p /frontend

WORKDIR /frontend

COPY package*.json /frontend

RUN npm install

COPY . /frontend

EXPOSE 3000

CMD ["npm", "run", "dev"]