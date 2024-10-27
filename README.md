# Options Trading Portal backend

Developed in python with FastAPI and uvicorn server.

Exposes POST "/api/submit" endpoint to handle form submission. It fetches derivative history using nsepython library
and computes the max profit, loss and break even for the strategy provided.

## Available Scripts

In the project directory, you can run:

### `pip install fastapi uvicorn`

Installs the FastAPI and an ASGI server like uvicorn

### `pip install fastapi[all]`

Installs CORS and all under fast api

### `uvicorn app:app --reload`

Server can be run using uvicorn, which will make the app available at http://127.0.0.1:8000.
The page will reload when you make changes.