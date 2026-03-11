from fastapi import FastAPI
from routes import commands,messages, role_assignments, sprites, status, auth, users, roles, prompts

app = FastAPI()

app.include_router(role_assignments.router)
app.include_router(commands.router)
app.include_router(messages.router)
app.include_router(status.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(prompts.router)
app.include_router(sprites.router)
