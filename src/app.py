from fastapi import FastAPI
from routing.users import router as user_routing
from routing.roles import router as role_routing

app = FastAPI(docs_url="/core/docs")

app.include_router(user_routing)
app.include_router(role_routing)



