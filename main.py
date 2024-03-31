import firebase_admin
import os
import random
import string

from google.cloud import firestore
from google.cloud.exceptions import Conflict
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, Response

DATABASE = os.getenv("DATABASE") # Datastore Database
COLLECTION = os.getenv("COLLECTION") # Datastore Database Collection (table)
PORT = os.getenv("PORT") # Cloud Run port

app = FastAPI()
firebase_init = firebase_admin.initialize_app()

db = firestore.Client(database=DATABASE)
collection = db.collection(COLLECTION)


@app.get("/{url_id}")
def get_smol_url(url_id: str) -> Response:
    """
    Retrieve the original URL for a given shortened URL identifier and redirect to it.

    Args:
        url_id (str): The unique identifier of the shortened URL.

    Raises:
        HTTPException: An exception with status code 404 if the URL is not found in the database.

    Returns:
        RedirectResponse: A redirection to the original URL associated with the given `url_id`.
    """
    hit = collection.document(url_id).get().to_dict()

    if not hit:
        raise HTTPException(status_code=404, detail="Url not found.")
    return RedirectResponse(hit["url"], status_code=302)


@app.post("/")
def create_smol_url(url: str) -> Response:
    """
    Create a new shortened URL that redirects to the supplied original URL.

    Args:
        url (str): The original URL that needs to be shortened.

    Raises:
        HTTPException: An exception with status code 500 indicating a need to retry the request due to a conflict (e.g., duplicate id).

    Returns:
        Response: the newly generated shortend URL.
    """
    raise HTTPException(status_code=500, detail="Not Implemented.")

    try:
        url_id = create_url_id()
        while collection.document(url_id).get().exists:
            url_id = create_url_id()

        collection.document(url_id).create({"url": url})

    except Conflict:
        raise HTTPException(status_code=500, detail="Retry Request.")

    return Response(status_code=200, content="/" + url_id)


def create_url_id() -> str:
    """
    Generate a random, unique identifier for a new shortened URL.

    The identifier consists of a string composed of 4 randomly chosen alphanumeric characters.

    Returns:
        str: A string representing the unique identifier for a shortened URL.
    """
    return "".join(
        random.SystemRandom().choices(string.ascii_letters + string.digits, k=4)
    )
