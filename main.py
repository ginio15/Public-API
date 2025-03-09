from fastapi import FastAPI
from routes import users, projects, auth
from services.db.db_config import init_db  



app = FastAPI()

# Initialize database
init_db()

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.get("/")
def read_root():
    return {"message": "Lets Rock"}
