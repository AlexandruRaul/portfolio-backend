# main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

# --- NOUVEAUX IMPORTS ---
import os                     # Pour lire les variables d'environnement
from dotenv import load_dotenv  # Pour charger le fichier .env
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
# --- FIN DES NOUVEAUX IMPORTS ---

# Charge les variables (SENDGRID_API_KEY, etc.) depuis notre .env
load_dotenv()

app = FastAPI()

# Configuration CORS (ne change pas)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schéma Pydantic (ne change pas)
class Message(BaseModel):
    nom: str
    email: EmailStr
    message: str

@app.get("/")
def read_root():
    return {"Hello": "API is running"}

# -----------------------------------------------
# --- MISE À JOUR DE LA ROUTE /contact ---
# -----------------------------------------------
@app.post("/contact")
def receive_message(msg: Message):
    
    # 1. Préparer l'e-mail à envoyer
    message = Mail(
        # L'expéditeur (doit être votre e-mail vérifié)
        from_email=os.environ.get('FROM_EMAIL'),
        
        # Le destinataire (vous !)
        to_emails=os.environ.get('TO_EMAIL'),
        
        # Le sujet de l'e-mail
        subject=f"Nouveau message de portfolio de : {msg.nom}",
        
        # Le "Pourquoi" : On formate le message en HTML
        # On utilise les données (msg.nom, msg.email) du formulaire
        html_content=f"""
            <div style="font-family: Arial, sans-serif; line-height: 1.6;">
                <p>Vous avez reçu un nouveau message de votre portfolio :</p>
                <p><strong>Nom :</strong> {msg.nom}</p>
                <p><strong>Email :</strong> {msg.email}</p>
                <hr style="border: 0; border-top: 1px solid #eee;">
                <p><strong>Message :</strong></p>
                
                <p>{msg.message.replace(chr(10), '<br>')}</p>
            </div>
        """
    )
    
    # 2. Envoyer l'e-mail via l'API SendGrid
    try:
        # On récupère la clé API depuis l'environnement
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        
        # On envoie la requête
        response = sg.send(message)
        
        # On vérifie si l'envoi a réussi (code 202)
        if response.status_code == 202:
            return {"status": "succès", "message": "Email envoyé !"}
        else:
            # Si SendGrid renvoie une erreur
            raise HTTPException(status_code=response.status_code, detail=response.body)
            
    except Exception as e:
        # Si notre code ou la connexion échoue
        print(f"Erreur lors de l'envoi de l'email: {e}")
        # On renvoie une erreur 500 (Erreur Serveur) à React
        raise HTTPException(status_code=500, detail=f"Erreur serveur lors de l'envoi de l'email: {str(e)}")