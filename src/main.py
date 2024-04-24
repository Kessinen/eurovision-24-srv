from fastapi import FastAPI
from routes import user_router, participant_router, review_router

app = FastAPI()
app.include_router(user_router)
app.include_router(participant_router)
app.include_router(review_router)
