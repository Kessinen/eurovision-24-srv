from fastapi.routing import APIRouter, Response
from fastapi import Request, Path, HTTPException
from typing import Annotated
from pydantic import BaseModel, Field

from db import users_db, participants_db, reviews_db
from models import User, participant, Review

user_router = APIRouter(prefix="/api/v1/user")
participant_router = APIRouter(prefix="/api/v1/participant")
review_router = APIRouter(prefix="/api/v1/review")


# User routes
@user_router.get("/all")
def get_all_users(request: Request):
    """
    Retrieve all users with their usernames and profile pictures.

    Parameters:
        request (Request): The request object

    Returns:
        list: A list of dictionaries containing usernames and profile pictures of users
    """
    users = users_db.getAll()
    retval = [
        {"username": user["username"], "profile_picture": user["profile_picture"]}
        for user in users
    ]
    return retval


@user_router.post("/add_user/{apikey}")
def add_user(request: Request, user: User, apikey: str):
    from uuid import uuid4

    """
    Add a new user to the database.

    Parameters:
        request (Request): The request object.
        user (User): The user object to be added. apikey WILL be overwritten by system.

    Returns:
        dict: A dictionary containing the username, profile picture, admin status, and API key of the new user.
    """
    # Check if is authorized
    result = users_db.getBy({"apikey": apikey, "isAdmin": True})
    if len(result) == 0:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Check if user already exists
    if users_db.getBy({"username": user.username}):
        raise HTTPException(status_code=409, detail="User already exists")
    user.apikey = str(uuid4())
    users_db.add(user.model_dump())
    return {"msg": "User added successfully"}


@user_router.get("/user/{apikey}")
def get_user_by_apikey(request: Request, apikey: str):
    """
    Retrieve a user from the database based on their API key.

    Parameters:
        request (Request): The request object.
        apikey (str): The API key of the user to retrieve.

    Returns:
        dict: A dictionary containing the user's username, profile picture, admin status, and API key.
    """
    users = users_db.getBy({"apikey": apikey})
    retval = {
        "username": users[0]["username"],
        "profile_picture": users[0]["profile_picture"],
        "isAdmin": users[0]["isAdmin"],
        "apikey": users[0]["apikey"],
    }
    return retval


@user_router.post("/login")
def login(request: Request, username: str, pin: int):
    retval = {"apikey": None}
    result = users_db.getBy({"username": username, "pin": pin})
    if len(result) > 0:
        retval = {"apikey": result[0]["apikey"]}
    return retval


# Participant routes
@participant_router.get("/all")
async def get_participants():
    """
    Retrieves all participants from the database.
    """

    return participants_db.getAll()


@participant_router.get("/round/{round_num}")
async def get_participants_by_round(
    round_num: Annotated[int, Path(title="Round number", gt=0, lt=4)]
):
    """
    Get participants by a specific round number.

    Parameters:
    round (int): The round number for which participants are requested. Must be an integer between 1 and 3.

    Returns:
    list: A sorted list of participants if found, otherwise returns an error dictionary.
    """
    result = participants_db.getBy({"round_num": round_num})
    if len(result) > 0:
        result = sorted(result, key=lambda x: x["turn"])
        return result
    return {"error": "Round not found"}


@participant_router.get("/{country}")
async def get_participants_by_country(country: str):
    """
    Get participants by country.

    Parameters:
    country (str): The country to filter participants by.

    Returns:
    list or dict: A list of participants if found, otherwise a dictionary with an error message.
    """
    result = participants_db.getBy({"country": country})
    if len(result) == 1:
        return result
    return HTTPException(status_code=404, detail="Country not found")


# Review routes


@review_router.get("/all")
async def get_reviews():
    return reviews_db.getAll()


@review_router.get("/{user_id}/{round_num}/{country_id}")
async def get_user_review_by_count_and_round(round_num: int, country: int, user: int):
    result = reviews_db.getBy(
        {"round": round_num, "country_id": country, "user_id": user}
    )
    if len(result) == 0:
        return {"melody": 0, "performance": 0, "wardrobe": 0}
    retval = {
        "melody": result[0]["melody"],
        "performance": result[0]["performance"],
        "wardrobe": result[0]["wardrobe"],
    }
    return retval


@review_router.get("/mean/{round_num}/{country_id}")
async def get_mean_score_by_count_and_round(round_num: int, country: int):
    retval = 0.0
    result = reviews_db.getBy({"round": round_num, "country_id": country})
    if len(result) == 0:
        return 0.0
    for review in result:
        retval += (review["melody"] + review["performance"] + review["wardrobe"]) / 3
    return {"mean_score": round(retval / len(result), 2)}


@review_router.post("/add_review")
async def add_review(review: Review):
    """
    Add a review to the database.

    Parameters:
    review (Review): The review object to be added. Review scores must be between 4 and 10. user_id and country_id are required.

    Returns:
    The result of adding the review to the database.
    """
    # Check if review already exists
    result = reviews_db.getBy(
        {
            "user_id": review.user_id,
            "country_id": review.country_id,
            "round": review.round,
        }
    )
    if len(result) == 0:
        return reviews_db.add(review.model_dump())

    # Update review
    return reviews_db.update(
        {
            "user_id": review.user_id,
            "country_id": review.country_id,
            "round": review.round,
        },
        review.model_dump(),
    )
