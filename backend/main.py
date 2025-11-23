from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# CORS – tillåt allt för test (kan låsas senare)
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====== MODELLER ======

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ====== "FAKE" DATABAS ======

FAKE_USER_DB = {
    "ulf": {
        "username": "ulf",
        "password": "hemligt",  # i verkligheten: använd hashade lösenord
    }
}


# ====== ENDPOINTS ======

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI"}


@app.post("/auth/login", response_model=LoginResponse)
def login(data: LoginRequest):
    user = FAKE_USER_DB.get(data.username)

    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Fel användarnamn eller lösenord")

    token = f"demo-token-for-{data.username}"
    return {"access_token": token, "token_type": "bearer"}


# ====== SKYDDAD LOGIK ======

def get_current_user(authorization: str = Header(None)):
    """
    Förväntar sig en header:
    Authorization: Bearer demo-token-for-<username>
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Ingen Authorization-header")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Felaktigt Authorization-format")

    token = parts[1]
    prefix = "demo-token-for-"
    if not token.startswith(prefix):
        raise HTTPException(status_code=401, detail="Ogiltig token")

    username = token[len(prefix):]
    return {"username": username}


@app.get("/me")
def read_me(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}
