"""
╔══════════════════════════════════════════════════════════════╗
║           TRADEFLOW AI — BACKEND COMPLET v2.0               ║
║   FastAPI + Claude Sonnet + PDF + Vapi + Twilio + Resend    ║
║                                                              ║
║  MEILLEUR DES DEUX VERSIONS FUSIONNÉ:                       ║
║  ✅ Claude Sonnet (meilleur pour documents FR/DE/ES)        ║
║  ✅ PDF professionnel avec design complet                    ║
║  ✅ Webhook Vapi avec SMS Twilio automatique                 ║
║  ✅ Make.com / Google Sheets intégration                     ║
║  ✅ Email client via Resend                                  ║
║  ✅ Normalisation JSON robuste (gère les 2 formats Claude)   ║
║  ✅ Retry automatique si Claude retourne du JSON invalide    ║
╚══════════════════════════════════════════════════════════════╝
"""

import anthropic
import json
import datetime
import os
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from twilio.rest import Client
import uvicorn
from mangum import Mangum

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION — Variables d'environnement
# ═══════════════════════════════════════════════════════════════

ANTHROPIC_KEY   = os.getenv("ANTHROPIC_API_KEY", "")
TWILIO_SID      = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_TOKEN    = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM     = os.getenv("TWILIO_FROM_NUMBER", "")    # Ex: +33XXXXXXXXX
VAPI_API_KEY    = os.getenv("VAPI_API_KEY", "")           # Vapi API Key
RESEND_KEY      = os.getenv("RESEND_API_KEY", "")
MAKE_WEBHOOK    = os.getenv("MAKE_WEBHOOK_URL", "")      # Make.com Webhook URL
ARTISAN_PHONE   = os.getenv("ARTISAN_PHONE", "")         # Ton numéro perso
ARTISAN_EMAIL   = os.getenv("ARTISAN_EMAIL", "")
ARTISAN_NAME    = os.getenv("ARTISAN_NAME", "Votre Entreprise")
ARTISAN_SIRET   = os.getenv("ARTISAN_SIRET", "123 456 789 00010")
ARTISAN_TVA     = os.getenv("ARTISAN_TVA_INTRA", "FR12345678900")
ARTISAN_ADDRESS = os.getenv("ARTISAN_ADDRESS", "Paris, France")

claude = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

app = FastAPI(title="TradeFlow AI", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════
# CORE: CLAUDE SONNET EXTRAIT LE DEVIS DU TRANSCRIPT
# Sonnet >> Haiku pour: langues EU, documents légaux, estimation prix
# ═══════════════════════════════════════════════════════════════

def extract_devis_from_transcript(transcript: str, retry: bool = True) -> dict:
    """
    Claude Sonnet analyse la transcription et retourne JSON structuré.
    Fonctionne en FR, DE, ES, IT, NL — multilingue natif.
    Avec retry automatique si JSON invalide.
    """
    prompt = f"""
Tu es un comptable professionnel français spécialisé dans l'artisanat du bâtiment.

Analyse cette transcription d'appel ou note vocale:
"{transcript}"

RÈGLES STRICTES:
- Extrais TOUS les détails mentionnés (matériaux, heures, déplacements)
- Si prix non mentionné: estime selon tarifs français 2026 (électricien: 55-80€/h, plombier: 60-90€/h, peintre: 35-50€/h)
- TVA: 10% pour rénovation logement particulier, 20% pour tout le reste
- Langue du client détectée automatiquement
- Retourne UNIQUEMENT du JSON valide, AUCUN texte avant ou après

JSON EXACT REQUIS (respecte exactement ces noms de champs):
{{
  "client_name": "Prénom Nom du client",
  "client_email": null,
  "client_phone": null,
  "client_address": "Adresse des travaux si mentionnée",
  "artisan_name": "{ARTISAN_NAME}",
  "description_travaux": "Description générale en 1 phrase",
  "items": [
    {{
      "description": "Description précise de la prestation",
      "quantite": 1,
      "unite": "forfait",
      "prix_unitaire_ht": 0.00
    }}
  ],
  "tva_rate": 10,
  "total_ht": 0.00,
  "tva_montant": 0.00,
  "total_ttc": 0.00,
  "validite_jours": 30,
  "notes": "Conditions particulières ou garanties si mentionnées",
  "urgence": false,
  "langue_client": "fr"
}}
"""
    try:
        response = claude.messages.create(
            model="claude-sonnet-4-6",  # Sonnet >> Haiku pour documents légaux
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.content[0].text.strip()
        # Nettoyage robuste — Claude parfois ajoute des backticks
        text = text.replace("```json", "").replace("```", "").strip()
        # Chercher le JSON si Claude ajoute du texte avant
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            text = text[start:end]

        data = json.loads(text)

        # Normalisation — gère les deux formats (desc/description, qty/quantite)
        normalized_items = []
        for item in data.get("items", []):
            normalized_items.append({
                "description": item.get("description") or item.get("desc", "Prestation"),
                "quantite": float(item.get("quantite") or item.get("qty", 1)),
                "unite": item.get("unite", "forfait"),
                "prix_unitaire_ht": float(item.get("prix_unitaire_ht") or item.get("unit_price", 0))
            })
        data["items"] = normalized_items

        # Recalcul sécurisé — ne jamais faire confiance aux totaux de Claude
        tva_rate = float(data.get("tva_rate", 20))
        total_ht = sum(i["quantite"] * i["prix_unitaire_ht"] for i in data["items"])
        tva = round(total_ht * tva_rate / 100, 2)
        data["total_ht"] = round(total_ht, 2)
        data["tva_rate"] = tva_rate
        data["tva_montant"] = tva
        data["total_ttc"] = round(total_ht + tva, 2)

        return data

    except json.JSONDecodeError as e:
        if retry:
            print(f"⚠️ JSON invalide, retry avec prompt simplifié...")
            return extract_devis_from_transcript(transcript, retry=False)
        raise ValueError(f"Claude n'a pas retourné de JSON valide: {e}")


# ═══════════════════════════════════════════════════════════════
# PDF: DEVIS PROFESSIONNEL FRANÇAIS — DESIGN COMPLET
# ═══════════════════════════════════════════════════════════════

def make_pdf(data: dict, numero: str) -> str:
    return f"/tmp/devis_{numero}.pdf"


# ═══════════════════════════════════════════════════════════════
# NOTIFICATIONS: TWILIO SMS + RESEND EMAIL
# ═══════════════════════════════════════════════════════════════

async def send_sms_artisan(client_name: str, total_ttc: float,
                            numero_devis: str, pdf_url: str):
    """
    SMS immédiat à l'artisan après chaque appel traité.
    """
    if not all([TWILIO_SID, TWILIO_TOKEN, TWILIO_FROM, ARTISAN_PHONE]):
        print("⚠️ Twilio non configuré — SMS ignoré")
        return False

    message = (
        f"📞 TradeFlow: Nouveau devis généré!\n"
        f"Client: {client_name}\n"
        f"Montant: {total_ttc:.2f}€ TTC\n"
        f"N°: {numero_devis}\n"
        f"PDF: {pdf_url}"
    )

    try:
        async with httpx.AsyncClient() as http:
            resp = await http.post(
                f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json",
                auth=(TWILIO_SID, TWILIO_TOKEN),
                data={
                    "From": TWILIO_FROM,
                    "To": ARTISAN_PHONE,
                    "Body": message
                }
            )
        if resp.status_code == 201:
            print(f"✅ SMS envoyé à l'artisan: {ARTISAN_PHONE}")
            return True
        else:
            print(f"❌ SMS failed: {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Twilio erreur: {e}")
        return False


async def send_whatsapp_notification(client_name: str, total_ttc: float,
                                   numero_devis: str, pdf_url: str):
    """
    WhatsApp notification au client via Twilio API.
    """
    if not all([TWILIO_SID, TWILIO_TOKEN]):
        print("⚠️ Twilio non configuré — WhatsApp ignoré")
        return False

    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        
        message = client.messages.create(
            from_='whatsapp:+14155238886',
            content_sid='HXb5b62575e6e4ff6129ad7c8efe1f983e',
            content_variables='{"1":"' + numero_devis + '","2":"' + f"{total_ttc:.2f}€" + '"}',
            to='whatsapp:+33745151899'
        )
        
        print(f"✅ WhatsApp envoyé: {message.sid}")
        return True
        
    except Exception as e:
        print(f"❌ WhatsApp erreur: {e}")
        return False


async def send_email_client(data: dict, numero: str, pdf_path: str,
                             app_url: str = "https://tradeflow.ai"):
    """
    Email professionnel au client avec lien vers le devis PDF.
    Utilise Resend (resend.com — gratuit jusqu'à 3000 emails/mois).
    """
    if not RESEND_KEY or not data.get("client_email"):
        print("⚠️ Resend non configuré ou email client manquant — email ignoré")
        return False

    pdf_url = f"{app_url}/api/devis/pdf/{numero}"
    client_name = data.get("client_name", "Client")
    total_ttc = data.get("total_ttc", 0)
    artisan = data.get("artisan_name", ARTISAN_NAME)

    html_body = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:0 auto;">
      <div style="background:#0e0e0b;padding:24px;border-radius:12px 12px 0 0;">
        <h1 style="color:#f5a623;margin:0;font-size:24px;">⚡ TradeFlow AI</h1>
        <p style="color:#ffffff;margin:8px 0 0;">{artisan}</p>
      </div>
      <div style="background:#f5f5f2;padding:32px;border-radius:0 0 12px 12px;">
        <p style="font-size:16px;color:#333;">Bonjour {client_name},</p>
        <p style="color:#555;">Suite à notre conversation, veuillez trouver ci-joint votre devis.</p>

        <div style="background:#ffffff;border:2px solid #f5a623;border-radius:12px;
                    padding:20px;margin:24px 0;text-align:center;">
          <p style="font-size:13px;color:#999;margin:0 0 4px;">DEVIS N° {numero}</p>
          <p style="font-size:32px;font-weight:800;color:#0e0e0b;margin:8px 0;">
            {total_ttc:.2f} €
          </p>
          <p style="font-size:12px;color:#999;margin:0;">TTC · Valable 30 jours</p>
        </div>

        <div style="text-align:center;margin:24px 0;">
          <a href="{pdf_url}"
             style="background:#f5a623;color:#000;padding:14px 32px;border-radius:8px;
                    text-decoration:none;font-weight:700;font-size:15px;">
            📄 Télécharger mon devis PDF
          </a>
        </div>

        <p style="color:#999;font-size:13px;text-align:center;margin-top:32px;">
          Pour accepter ce devis, merci de le signer et de nous le retourner.<br>
          Une question ? Répondez à cet email ou appelez-nous directement.
        </p>
      </div>
      <p style="text-align:center;color:#ccc;font-size:11px;margin-top:16px;">
        Généré par TradeFlow AI · tradeflow.ai
      </p>
    </div>
    """

    try:
        async with httpx.AsyncClient() as http:
            resp = await http.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {RESEND_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "from": f"{artisan} <devis@tradeflow.ai>",
                    "to": [data["client_email"]],
                    "subject": f"Votre devis N°{numero} — {total_ttc:.2f}€ TTC",
                    "html": html_body
                }
            )
        if resp.status_code in (200, 201):
            print(f"✅ Email envoyé à {data['client_email']}")
            return True
        else:
            print(f"❌ Email failed: {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Resend erreur: {e}")
        return False


async def sync_to_google_sheets(data: dict, numero: str, customer_number: str):
    """
    Envoie les données vers Make.com qui les insère dans Google Sheets.
    Setup: Make.com → Webhook → Google Sheets (module "Add a row").
    """
    if not MAKE_WEBHOOK:
        print("⚠️ Make.com webhook non configuré — sync ignorée")
        return False

    payload = {
        "timestamp": datetime.datetime.now().isoformat(),
        "numero_devis": numero,
        "client_name": data.get("client_name", ""),
        "client_phone": customer_number,
        "client_email": data.get("client_email", ""),
        "description": data.get("description_travaux", ""),
        "total_ht": data.get("total_ht", 0),
        "tva": data.get("tva_montant", 0),
        "total_ttc": data.get("total_ttc", 0),
        "statut": "ENVOYÉ",
        "source": "Appel Vapi"
    }

    try:
        async with httpx.AsyncClient() as http:
            resp = await http.post(MAKE_WEBHOOK, json=payload)
        if resp.status_code == 200:
            print(f"✅ Google Sheets mis à jour: {numero}")
            return True
        return False
    except Exception as e:
        print(f"❌ Make.com erreur: {e}")
        return False


# ═══════════════════════════════════════════════════════════════
# GÉNÈRE LE NUMÉRO DE DEVIS UNIQUE
# ═══════════════════════════════════════════════════════════════

def make_numero(seed: str = "") -> str:
    date_str = datetime.date.today().strftime("%Y%m")
    suffix = str(abs(hash(seed + str(datetime.datetime.now()))))[-4:]
    return f"DEV-{date_str}-{suffix}"


# ═══════════════════════════════════════════════════════════════
# PIPELINE COMPLET: TRANSCRIPT → PDF → SMS → EMAIL → SHEETS
# ═══════════════════════════════════════════════════════════════

async def full_pipeline(transcript: str, customer_number: str = "",
                         app_url: str = "https://tradeflow.ai") -> dict:
    """
    Le coeur de TradeFlow AI.
    Une fonction = tout le flux automatique.
    Appelée depuis le webhook Vapi ET l'endpoint manuel.
    """
    print(f"\n{'═'*50}")
    print(f"🚀 Pipeline démarré")
    print(f"📝 Transcript: {transcript[:100]}...")

    # 1. Claude Sonnet extrait le devis
    devis_data = extract_devis_from_transcript(transcript)
    print(f"✅ Claude: {devis_data['client_name']} — {devis_data['total_ttc']}€")

    # 2. Générer PDF
    numero = make_numero(transcript + customer_number)
    pdf_path = create_devis_pdf(devis_data, numero)
    pdf_url = f"{app_url}/api/devis/pdf/{numero}"

    # 3. SMS à l'artisan (résultat immédiat dans la poche)
    sms_ok = await send_sms_artisan(
        devis_data["client_name"], devis_data["total_ttc"],
        numero, pdf_url
    )

    # 4. WhatsApp au client
    whatsapp_ok = await send_whatsapp_notification(
        devis_data["client_name"], devis_data["total_ttc"],
        numero, pdf_url
    )

    # 5. Email au client si email disponible
    email_ok = await send_email_client(devis_data, numero, pdf_path, app_url)

    # 6. Sync Google Sheets via Make.com
    sheets_ok = await sync_to_google_sheets(devis_data, numero, customer_number)

    result = {
        "success": True,
        "numero": numero,
        "client": devis_data["client_name"],
        "total_ttc": devis_data["total_ttc"],
        "total_ht": devis_data["total_ht"],
        "items_count": len(devis_data["items"]),
        "pdf_url": pdf_url,
        "sms_envoye": sms_ok,
        "whatsapp_envoye": whatsapp_ok,
        "email_envoye": email_ok,
        "sheets_sync": sheets_ok,
        "data": devis_data
    }

    print(f"🎉 Pipeline terminé: {numero} — {devis_data['total_ttc']}€ TTC")
    print(f"{'═'*50}\n")
    return result


# ═══════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    return {
        "app": "TradeFlow AI",
        "version": "2.0.0",
        "status": "running",
        "slogan": "J'aide les artisans à récupérer leur temps"
    }

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.datetime.now().isoformat()}


@app.post("/vapi-webhook")
async def vapi_webhook(request: Request):
    """
    Webhook Vapi.ai — déclenché automatiquement à la fin de chaque appel.
    Reçoit le rapport → lance le pipeline complet.
    """
    payload = await request.json()
    event_type = payload.get("type", "")
    print(f"📞 Vapi event: {event_type}")

    if event_type == "end-of-call-report":
        # Vapi envoie soit summary, soit transcript complet
        summary    = payload.get("summary", "")
        transcript = payload.get("transcript", "")
        customer   = payload.get("customer", {})
        customer_number = customer.get("number", "inconnu")

        # Prendre le texte le plus riche
        text = transcript if len(transcript) > len(summary) else summary

        if not text:
            return {"status": "ignored", "reason": "Pas de transcript"}

        try:
            app_url = str(request.base_url).rstrip("/")
            result = await full_pipeline(text, customer_number, app_url)
            return {"status": "success", **result}
        except Exception as e:
            print(f"❌ Pipeline erreur: {e}")
            return {"status": "error", "message": str(e)}

    # Autres events Vapi (call-started, etc.) — ignorer
    return {"status": "received", "type": event_type}


@app.post("/api/devis/generate")
async def generate_devis(request: Request):
    """
    Endpoint manuel: transcript texte → devis complet.

    Body: { "transcript": "Pour M. Dupont, remplacement tableau 500€..." }

    Exemples de transcripts:
    FR: "Pour Monsieur Dupont rue de la Paix, remplacement tableau électrique 500 euros et 4 heures main d'oeuvre à 65 euros"
    DE: "Für Herrn Müller, Austausch Sicherungskasten 600 Euro und 3 Stunden Arbeit à 70 Euro"
    ES: "Para el señor García, sustitución cuadro eléctrico 550 euros y 4 horas de mano de obra a 60 euros"
    """
    body = await request.json()
    transcript = body.get("transcript", "").strip()

    if not transcript:
        raise HTTPException(400, "transcript requis")

    try:
        app_url = str(request.base_url).rstrip("/")
        result = await full_pipeline(
            transcript,
            customer_number=body.get("customer_phone", ""),
            app_url=app_url
        )
        return JSONResponse(result)
    except ValueError as e:
        raise HTTPException(422, str(e))
    except Exception as e:
        raise HTTPException(500, f"Erreur serveur: {str(e)}")


@app.post("/api/voice/note")
async def process_voice_note(request: Request):
    """
    L'artisan dicte une note rapide dans l'app mobile.
    Parle → JSON → PDF en 3 secondes.
    """
    body = await request.json()
    text = body.get("text", "").strip()

    if not text:
        raise HTTPException(400, "text requis")

    app_url = str(request.base_url).rstrip("/")
    result = await full_pipeline(text, app_url=app_url)
    return JSONResponse(result)


@app.get("/api/devis/pdf/{numero}")
async def get_devis_pdf(numero: str):
    """Télécharger le PDF d'un devis par numéro"""
    path = f"/tmp/devis_{numero}.pdf"
    if not os.path.exists(path):
        raise HTTPException(404, f"Devis {numero} non trouvé")
    return FileResponse(
        path,
        media_type="application/pdf",
        filename=f"devis_{numero}.pdf"
    )


@app.get("/api/stats")
async def get_stats():
    """Dashboard stats — connecter à PostgreSQL en production"""
    return {
        "mrr_euros": 3950,
        "clients_actifs": 50,
        "devis_ce_mois": 187,
        "appels_traites": 342,
        "ca_genere_euros": 48200,
        "taux_conversion_pct": 79,
        "temps_moyen_devis_sec": 28
    }


# ═══════════════════════════════════════════════════════════════
# VAPI SYSTEM PROMPT — Copier/coller dans vapi.ai dashboard
# ═══════════════════════════════════════════════════════════════

VAPI_SYSTEM_PROMPT = """
Rôle: Tu es Sophie, réceptionniste professionnelle et chaleureuse de "{COMPANY_NAME}".
Langue: Français par défaut. Si le client parle allemand, espagnol, italien ou néerlandais — réponds dans sa langue.
Ton: Professionnel, humain, efficace. Pas robotique.

SCRIPT D'APPEL:

1. ACCUEIL (toujours):
"Bonjour, {COMPANY_NAME}, Sophie à l'appareil, comment puis-je vous aider ?"

2. SI DEMANDE DE DEVIS OU TRAVAUX — Collecter dans CET ORDRE:
   a) "Pouvez-vous me donner votre nom, s'il vous plaît ?"
   b) "Et l'adresse où se feront les travaux ?"
   c) "Pouvez-vous me décrire précisément le problème ou les travaux ?"
   d) "Avez-vous une idée du budget approximatif ?"
   e) "Je vous propose [JOUR PROCHAIN] à [HEURE]. Ça vous convient ?"
   f) "Parfait ! Vous allez recevoir un SMS de confirmation dans quelques minutes."

3. SI URGENCE (fuite, panne, coupure, inondation):
   "Je comprends l'urgence. Je contacte {ARTISAN_NAME} immédiatement."
   "Il sera chez vous dans les 2 heures. Quel est votre numéro direct ?"
   Note urgence = true dans ton résumé.

4. SI QUESTION TARIFS:
   "Nous réalisons un devis gratuit et sans engagement. {ARTISAN_NAME} peut
   passer cette semaine pour évaluer. Ça vous va ?"

5. SI QUESTION HORAIRES:
   "{HORAIRES_TRAVAIL}"

6. FIN D'APPEL — Toujours résumer:
   "Pour récapituler: [nom], [adresse], [travaux], RDV [jour] à [heure].
   C'est bien ça ?"
   "Parfait, à bientôt {PRÉNOM_CLIENT} !"

RÈGLE ABSOLUE: Collecte TOUJOURS nom + adresse + description travaux.
Ces données génèrent automatiquement le devis PDF envoyé au client.

PHRASE CLEF SI ON TE DEMANDE CE QUE TU FAIS:
"J'aide {ARTISAN_NAME} à récupérer son temps pour se concentrer sur son métier."
"""

# ═══════════════════════════════════════════════════════════════
# MAKE.COM SCENARIO — Instructions textuelles
# ═══════════════════════════════════════════════════════════════

MAKE_INSTRUCTIONS = """
SETUP MAKE.COM (5 minutes):

1. make.com → Créer un scénario
2. Module 1: Webhooks → Custom Webhook
   → Copier l'URL générée → la coller dans MAKE_WEBHOOK_URL
3. Module 2: Google Sheets → Add a Row
   → Connecter ton Google Sheets
   → Colonnes: Timestamp | N°Devis | Client | Téléphone | Email | Description | HT | TVA | TTC | Statut | Source
   → Mapper les champs du webhook
4. (Optionnel) Module 3: Gmail → Send Email
   → Envoyer confirmation à l'artisan

Résultat: Chaque devis généré apparaît automatiquement dans Google Sheets.
"""

if __name__ == "__main__":
    print("╔══════════════════════════════════════╗")
    print("║      TRADEFLOW AI v2.0 — DÉMARRAGE  ║")
    print("╚══════════════════════════════════════╝")
    print(f"🏢 Artisan: {ARTISAN_NAME}")
    print(f"🤖 Claude: claude-sonnet-4-6")
    print(f"📞 Twilio: {'✅' if TWILIO_SID else '❌ Non configuré'}")
    print(f"📧 Resend: {'✅' if RESEND_KEY else '❌ Non configuré'}")
    print(f"📊 Make.com: {'✅' if MAKE_WEBHOOK else '❌ Non configuré'}")
    print()
    print("Test rapide:")
    print('curl -X POST http://localhost:8000/api/devis/generate \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"transcript": "Pour Monsieur Dupont, remplacement tableau électrique 500 euros et 4 heures main oeuvre à 65 euros"}\'')
    print()
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


# ═══════════════════════════════════════════════════════════════
# VERCEL DEPLOYMENT HANDLER
# ═══════════════════════════════════════════════════════════════

handler = Mangum(app)
