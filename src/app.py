from fastapi import FastAPI
from routing.users import router as user_routing

app = FastAPI(docs_url="/docs")

app.include_router(user_routing)



