from fastapi import FastAPI
from routes import assignRole, commands,sprite, messages, photo, status, auth, users, roles, prompts

app = FastAPI()

app.include_router(assignRole.router)
app.include_router(commands.router)
app.include_router(messages.router)
app.include_router(photo.router)
app.include_router(status.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(prompts.router)
app.include_router(sprite.router)
