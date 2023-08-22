FROM node:lts-alpine

ARG bibex_model_endpoint=http://localhost
ARG bibex_model_port=8000

# install simple http server for serving static content
RUN npm install -g http-server

# make the 'app' folder the current working directory
WORKDIR /app

# copy both 'package.json' and 'package-lock.json' (if available)
COPY package*.json ./

# copy project files and folders to the current working directory (i.e. 'app' folder)
COPY ./public ./public
COPY ./src ./src
COPY ./index.html ./index.html
COPY ./.env ./.env
COPY ./set_api_endpoint.sh ./set_api_endpoint.sh
COPY ./vite.config.js ./vite.config.js

# install project dependencies
RUN npm install

# set api endpoint
RUN ./set_api_endpoint.sh -e $bibex_model_endpoint

# build app for production with minification
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]