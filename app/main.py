from fastapi import FastAPI
import uvicorn
from routers import opord_route, items_route, users_route, customers_route, orders_route
from database import engine, Base
from fastapi.middleware.cors import CORSMiddleware
import multiprocessing
import uvicorn


Base.metadata.create_all(bind=engine)  # Add bind=engine here

description = """
Mobile Order Apps for HMBR, GI Corporation & Zepto Chemicals. 🚀


## Users

You will be able to:

* **Create users** (_not implemented_).
* **Read users** (_not implemented_).

## Items
You can **read items**.

"""

tags_metadata = [
    {
        "name": "Users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "Items",
        "description": "Get all items from all section",
        # "externalDocs": {
        #     "description": "Items external docs",
        #     "url": "https://fastapi.tiangolo.com/",
        # },
    },
]


app = FastAPI(
    title="HMBR Mobile Apps API",
    description=description,
    summary="Api Version v1",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Bashar",
        "url": "https://bashar.pythonanywhere.com/",
        "email": "mat197194@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
        "identifier": "MIT",
    },
    openapi_tags=tags_metadata,
)


# add cors
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    items_route.router,
    prefix="/api/v1/items",
    tags=["Items"],
    responses={418: {"description": "Inventory, Items, Stock endpoint "}},
)

app.include_router(
    users_route.router,
    prefix="/api/v1/users",
    tags=["Users"],
    responses={418: {"description": "Users endpoint"}},
)

app.include_router(
    customers_route.router,
    prefix="/api/v1/customers",
    tags=["Customers"],
    responses={418: {"description": "Customers endpoint"}},
)
app.include_router(
    orders_route.router,
    prefix="/api/v1/order",
    tags=["Orders"],
    responses={418: {"description": "Create Order endpoint"}},
)

if __name__ == "__main__":

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, workers=4)
