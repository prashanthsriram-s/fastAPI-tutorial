# fastAPI-tutorial

Currently Using the auth.py to test the OAuth2 with JWT tokens -> Seems to be working

# If you want to run this
1. download this
2. install the requirements from the requirements.txt using ```pip install -r requirements.txt``` (I would advise using a virtual enviroment for doing this)
3. run ```uvicorn auth:app --reload```
4. goto http://127.0.0.1:8000/docs to view the api and try stuff out or alternatively use your browser or postman or any thing to call the apis

(Set your own secret key in a .env file in the same folder before running with ```SECRET_KEY=XXXXXXXXXX```. You can generate the secret key online or using ```openssl rand -hex 32```)