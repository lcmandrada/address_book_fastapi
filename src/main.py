from fastapi import FastAPI

import models
from database import engine
from routers import address

# Create the database tables.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Address Book")
app.include_router(address.router)
