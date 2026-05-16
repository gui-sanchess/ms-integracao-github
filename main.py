import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from adapters.inbound.controllers import router
from infrastructure.database import engine, Base


Base.metadata.create_all(bind=engine)
app = FastAPI(title="Microsserviço de Integração Git - DocuIA")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    # A Azure injeta a variável PORT. O 8000 fica como segurança local.
    porta = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=porta)