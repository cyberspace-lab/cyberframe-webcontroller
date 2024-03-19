FROM node:19-bullseye

WORKDIR /home/node/app

COPY package.json package-lock.json ./

#COPY ./testApp/package-lock.json ./home/node/app/

RUN npm install

COPY src ./home/node/app

CMD ["npm", "run", "serve"]