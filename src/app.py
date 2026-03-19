from fastapi import FastAPI
from routes import commands, me ,messages, role_assignments, sprites, status, auth, users, roles, prompts
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    'http://localhost:4000'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(role_assignments.router)
app.include_router(commands.router)
app.include_router(messages.router)
app.include_router(status.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(prompts.router)
app.include_router(sprites.router)
app.include_router(me.router)
