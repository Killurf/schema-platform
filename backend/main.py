from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Tillåt anrop från din webbplats (byt till din egen domän när du vill låsa ner)
origins = [
    "*",  # för test. Senare kan du t.ex. sätta "https://dindomän.se"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enkel modell för inloggning
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Enkel "databas" i minnet bara för demo
FAKE_USER_DB = {
    "ulf": {
        "username": "ulf",
        "password": "hemligt",  # i verkligheten: ALDRIG spara klartext
    }
}


@app.get("/")
def read_root():
    return {"message": "Hello from Schema API"}


@app.post("/auth/login", response_model=LoginResponse)
def login(data: LoginRequest):
    user = FAKE_USER_DB.get(data.username)

    # Kolla användare + lösenord
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Fel användarnamn eller lösenord")

    # I riktig lösning skulle du skapa en JWT-token här
    token = f"demo-token-for-{data.username}"
    return {"access_token": token, "token_type": "bearer"}
