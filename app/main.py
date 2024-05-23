from fastapi import FastAPI
import uvicorn
from routers import opord_route, items_route, users_route
from database import engine, Base


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
        "description": "Manage items. So _fancy_ they have their own docs.",
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
        "email": "mat197194@gmail.com"
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
        "identifier": "MIT",
    },
    openapi_tags=tags_metadata

)






app.include_router(items_route.router, 
                   prefix="/api/v1/items",
                   tags=["Items"],
                   responses={418: {"description": "Inventory, Items, Stock endpoint "}},)

app.include_router(users_route.router,
                   prefix="/api/v1/users",
                   tags=["Users"],
                   responses={418: {"description": "Users endpoint"}},)


# if __name__ == "__main__":
#     uvicorn.run(app, host="localhost", port=9800, reload=True)
