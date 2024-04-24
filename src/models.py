from pydantic import BaseModel, Field
from typing import Optional
import uuid


class User(BaseModel):
    username: str
    pin: int
    profile_picture: int
    isAdmin: bool = Field(default=False)
    apikey: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))


class participant(BaseModel):
    id: int
    year: int
    country: str
    country_img: str
    name: str
    song: str
    img: str
    url: str
    round_num: int
    turn: int


class Review(BaseModel):
    id: int
    user_id: int = Field(ge=1)
    country_id: int = Field(ge=1)
    round_num: int = Field(ge=1, le=3)
    melody: int = Field(ge=4, le=10)
    performance: int = Field(ge=4, le=10)
    wardrobe: int = Field(ge=4, le=10)
