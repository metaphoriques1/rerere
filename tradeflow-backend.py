"""
TRADEFLOW AI — BACKEND COMPLET
FastAPI + Claude + PDF + Vapi Webhook
"""

import anthropic
import json
import datetime
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
import uvicorn

app = FastAPI(title="TradeFlow AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", "YOUR_KEY"))

# ═══════════════════════════════════════════════════
# CORE: CLAUDE EXTRAIT LES DONNÉES DU TRANSCRIPT
# ═══════════════════════════════════════════════════

def extract_devis_from_transcript(transcript: str) -> dict:
    """
    Claude analyse la transcription vocale et retourne JSON structuré.
    Fonctionne en FR, DE, ES, IT, NL.
    """
    prompt = f"""
Tu es un comptable professionnel français spécialisé dans l'artisanat.

Analyse cette transcription d'appel ou note vocale d'un artisan:
"{transcript}"

Extrais et structure les informations pour créer un devis français légal.

Règles:
- Si le prix HT n'est pas mentionné, estime un prix raisonnable pour ce type de travail en France
- TVA standard: 10% pour travaux de rénovation logement, 20% pour autres
- Retourne UNIQUEMENT du JSON valide, rien d'autre

Format JSON requis:
{{
  "client_name": "Nom du client extrait",
  "client_email": "email si mentionné sinon null",
  "client_address": "adresse si mentionnée sinon null",
  "artisan_name": "Martin Électricité",
  "description_travaux": "Description générale des travaux",
  "items": [
    {{
      "description": "Description précise de la prestation",
      "quantite": 1,
      "unite": "forfait",
      "prix_unitaire_ht": 0
    }}
  ],
  "tva_rate": 10,
  "total_ht": 0,
  "tva_montant": 0,
  "total_ttc": 0,
  "validite_jours": 30,
  "notes": "Notes ou conditions particulières"
}}
"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",  # Rapide et économique
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.content[0].text
    # Nettoyage si Claude ajoute des backticks
    text = text.replace("```json", "").replace("```", "").strip()

    data = json.loads(text)

    # Recalcul sécurisé des totaux
    total_ht = sum(
        item["quantite"] * item["prix_unitaire_ht"]
        for item in data["items"]
    )
    tva = round(total_ht * data["tva_rate"] / 100, 2)
    data["total_ht"] = round(total_ht, 2)
    data["tva_montant"] = tva
    data["total_ttc"] = round(total_ht + tva, 2)

    return data


# ═══════════════════════════════════════════════════
# PDF: DEVIS PROFESSIONNEL FRANÇAIS
# ═══════════════════════════════════════════════════

def create_devis_pdf(data: dict, numero: str = None) -> str:
    """
    Génère un PDF devis conforme aux standards français.
    """
    if not numero:
        numero = f"DEV-{datetime.date.today().strftime('%Y%m%d')}-{str(hash(data['client_name']))[-4:]}"

    filename = f"/tmp/devis_{numero}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # ─── COULEURS ───
    ORANGE = colors.HexColor("#f5a623")
    DARK = colors.HexColor("#0e0e0b")
    GRAY = colors.HexColor("#6b6b6b")
    LIGHT = colors.HexColor("#f5f5f2")

    # ─── BANDE HEADER ───
    c.setFillColor(DARK)
    c.rect(0, height - 90*mm, width, 90*mm, fill=1, stroke=0)

    # Logo / Nom entreprise
    c.setFillColor(ORANGE)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(20*mm, height - 28*mm, "⚡ TradeFlow")

    c.setFillColor(colors.white)
    c.setFont("Helvetica", 10)
    c.drawString(20*mm, height - 36*mm, data.get("artisan_name", "Entreprise Artisanale"))

    # Titre DEVIS
    c.setFillColor(ORANGE)
    c.setFont("Helvetica-Bold", 28)
    c.drawRightString(width - 20*mm, height - 28*mm, "DEVIS")

    c.setFillColor(colors.white)
    c.setFont("Helvetica", 10)
    c.drawRightString(width - 20*mm, height - 36*mm, f"N° {numero}")
    c.drawRightString(width - 20*mm, height - 42*mm,
                      f"Date: {datetime.date.today().strftime('%d/%m/%Y')}")
    c.drawRightString(width - 20*mm, height - 48*mm,
                      f"Validité: {data.get('validite_jours', 30)} jours")

    # ─── INFOS ARTISAN + CLIENT ───
    y = height - 105*mm

    # Bloc Artisan (gauche)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20*mm, y, "ÉMETTEUR")
    c.setFont("Helvetica", 9)
    c.setFillColor(GRAY)
    c.drawString(20*mm, y - 6*mm, data.get("artisan_name", "Martin Électricité"))
    c.drawString(20*mm, y - 11*mm, "SIRET: 123 456 789 00010")
    c.drawString(20*mm, y - 16*mm, "TVA: FR12345678900")
    c.drawString(20*mm, y - 21*mm, "Paris, France")

    # Bloc Client (droite)
    c.setFillColor(LIGHT)
    c.rect(width/2, y + 5*mm, width/2 - 20*mm, -35*mm, fill=1, stroke=0)

    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(width/2 + 5*mm, y, "CLIENT")
    c.setFont("Helvetica", 9)
    c.setFillColor(GRAY)
    c.drawString(width/2 + 5*mm, y - 6*mm, data.get("client_name", "Client"))
    if data.get("client_email"):
        c.drawString(width/2 + 5*mm, y - 11*mm, data["client_email"])
    if data.get("client_address"):
        c.drawString(width/2 + 5*mm, y - 16*mm, data["client_address"])

    # ─── DESCRIPTION TRAVAUX ───
    y -= 45*mm
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20*mm, y, "OBJET DES TRAVAUX")
    c.setFont("Helvetica", 9)
    c.setFillColor(GRAY)
    c.drawString(20*mm, y - 6*mm, data.get("description_travaux", "Travaux d'artisanat"))

    # ─── TABLEAU PRESTATIONS ───
    y -= 22*mm

    # En-têtes
    c.setFillColor(DARK)
    c.rect(20*mm, y, width - 40*mm, 8*mm, fill=1, stroke=0)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(22*mm, y + 2*mm, "DÉSIGNATION")
    c.drawString(width - 95*mm, y + 2*mm, "QTÉ")
    c.drawString(width - 80*mm, y + 2*mm, "UNITÉ")
    c.drawString(width - 60*mm, y + 2*mm, "PRIX UNIT. HT")
    c.drawString(width - 35*mm, y + 2*mm, "TOTAL HT")

    # Lignes
    y -= 8*mm
    for i, item in enumerate(data["items"]):
        bg = LIGHT if i % 2 == 0 else colors.white
        c.setFillColor(bg)
        c.rect(20*mm, y - 1*mm, width - 40*mm, 8*mm, fill=1, stroke=0)

        total_ligne = item["quantite"] * item["prix_unitaire_ht"]
        c.setFillColor(DARK)
        c.setFont("Helvetica", 9)
        c.drawString(22*mm, y + 1.5*mm, item["description"][:50])
        c.drawString(width - 95*mm, y + 1.5*mm, str(item["quantite"]))
        c.drawString(width - 80*mm, y + 1.5*mm, item.get("unite", "forfait"))
        c.drawString(width - 60*mm, y + 1.5*mm, f"{item['prix_unitaire_ht']:.2f} €")
        c.drawString(width - 35*mm, y + 1.5*mm, f"{total_ligne:.2f} €")
        y -= 8*mm

    # ─── TOTAUX ───
    y -= 10*mm
    c.setFillColor(LIGHT)
    c.rect(width - 90*mm, y - 20*mm, 70*mm, 28*mm, fill=1, stroke=0)

    c.setFillColor(DARK)
    c.setFont("Helvetica", 9)
    c.drawString(width - 88*mm, y, "Total HT:")
    c.drawRightString(width - 22*mm, y, f"{data['total_ht']:.2f} €")

    c.drawString(width - 88*mm, y - 7*mm, f"TVA ({data['tva_rate']}%):")
    c.drawRightString(width - 22*mm, y - 7*mm, f"{data['tva_montant']:.2f} €")

    # Total TTC — mis en valeur
    c.setFillColor(DARK)
    c.rect(width - 90*mm, y - 22*mm, 70*mm, 10*mm, fill=1, stroke=0)
    c.setFillColor(ORANGE)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(width - 88*mm, y - 18*mm, "TOTAL TTC:")
    c.drawRightString(width - 22*mm, y - 18*mm, f"{data['total_ttc']:.2f} €")

    # ─── NOTES ───
    if data.get("notes"):
        y -= 40*mm
        c.setFillColor(DARK)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(20*mm, y, "CONDITIONS PARTICULIÈRES")
        c.setFont("Helvetica", 8)
        c.setFillColor(GRAY)
        c.drawString(20*mm, y - 6*mm, data["notes"])

    # ─── SIGNATURE ───
    y = 40*mm
    c.setFillColor(LIGHT)
    c.rect(width - 90*mm, y, 70*mm, 30*mm, fill=1, stroke=0)
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 8)
    c.drawString(width - 88*mm, y + 22*mm, "Bon pour accord — Signature client:")
    c.drawString(width - 88*mm, y + 8*mm, "Date:")

    # Footer
    c.setFillColor(DARK)
    c.rect(0, 0, width, 15*mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica", 7)
    c.drawCentredString(width/2, 6*mm,
        "Document généré par TradeFlow AI · tradeflow.ai · Devis valable 30 jours")

    c.save()
    print(f"✅ Devis PDF créé: {filename}")
    return filename


# ═══════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════

@app.get("/")
async def root():
    return {"status": "TradeFlow AI running", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/devis/generate")
async def generate_devis(request: Request):
    """
    Endpoint principal: transcript → JSON devis + PDF
    
    Body: { "transcript": "Pour Monsieur Dupont, remplacement tableau 500€..." }
    """
    body = await request.json()
    transcript = body.get("transcript", "")

    if not transcript:
        raise HTTPException(400, "transcript requis")

    try:
        # 1. Claude extrait les données
        devis_data = extract_devis_from_transcript(transcript)

        # 2. Générer PDF
        numero = f"DEV-{datetime.date.today().strftime('%Y%m')}-{str(abs(hash(transcript)))[-4:]}"
        pdf_path = create_devis_pdf(devis_data, numero)

        return JSONResponse({
            "success": True,
            "numero": numero,
            "data": devis_data,
            "pdf_url": f"/api/devis/pdf/{numero}",
            "message": f"Devis {numero} généré — {devis_data['total_ttc']}€ TTC"
        })

    except json.JSONDecodeError as e:
        raise HTTPException(422, f"Erreur parsing Claude: {str(e)}")
    except Exception as e:
        raise HTTPException(500, f"Erreur: {str(e)}")


@app.get("/api/devis/pdf/{numero}")
async def get_devis_pdf(numero: str):
    """Télécharger le PDF du devis"""
    path = f"/tmp/devis_{numero}.pdf"
    if not os.path.exists(path):
        raise HTTPException(404, "Devis non trouvé")
    return FileResponse(path, media_type="application/pdf",
                        filename=f"devis_{numero}.pdf")


@app.post("/vapi-webhook")
async def vapi_webhook(request: Request):
    """
    Webhook Vapi.ai — reçoit le rapport de fin d'appel.
    Génère automatiquement le devis depuis la transcription.
    """
    payload = await request.json()

    print(f"📞 Vapi webhook reçu: {payload.get('type')}")

    if payload.get("type") == "end-of-call-report":
        summary = payload.get("summary", "")
        transcript = payload.get("transcript", summary)
        customer_number = payload.get("customer", {}).get("number", "inconnu")

        print(f"📱 Appel de {customer_number}: {summary[:100]}...")

        if transcript or summary:
            try:
                text = transcript or summary
                devis_data = extract_devis_from_transcript(text)
                numero = f"DEV-{datetime.date.today().strftime('%Y%m%d')}-{customer_number[-4:]}"
                pdf_path = create_devis_pdf(devis_data, numero)

                print(f"✅ Devis auto-généré: {numero} — {devis_data['total_ttc']}€")

                # TODO: Envoyer SMS à l'artisan via Twilio
                # TODO: Envoyer email au client via Resend

                return {
                    "status": "success",
                    "devis_numero": numero,
                    "total_ttc": devis_data["total_ttc"],
                    "client": devis_data["client_name"]
                }

            except Exception as e:
                print(f"❌ Erreur génération devis: {e}")
                return {"status": "error", "message": str(e)}

    return {"status": "received"}


@app.post("/api/voice/process")
async def process_voice_note(request: Request):
    """
    L'artisan dicte une note vocale dans l'app.
    Transcription → Claude → Devis en 30 secondes.
    
    Body: { "text": "Pour Dupont, remplacement prises 3h à 60€..." }
    """
    body = await request.json()
    text = body.get("text", "")

    if not text:
        raise HTTPException(400, "text requis")

    devis_data = extract_devis_from_transcript(text)
    numero = f"DEV-{datetime.date.today().strftime('%Y%m%d')}-{str(abs(hash(text)))[-4:]}"
    pdf_path = create_devis_pdf(devis_data, numero)

    return {
        "success": True,
        "numero": numero,
        "client": devis_data["client_name"],
        "total_ttc": devis_data["total_ttc"],
        "items_count": len(devis_data["items"]),
        "pdf_url": f"/api/devis/pdf/{numero}"
    }


@app.get("/api/stats")
async def get_stats():
    """Stats dashboard mock — connecter à DB en prod"""
    return {
        "mrr": 3950,
        "clients_actifs": 50,
        "devis_ce_mois": 187,
        "appels_traites": 342,
        "ca_genere": 48200,
        "taux_conversion": 79
    }


# ═══════════════════════════════════════════════════
# VAPI SYSTEM PROMPT — Coller dans Vapi Dashboard
# ═══════════════════════════════════════════════════

VAPI_SYSTEM_PROMPT = """
Role: Tu es Marie, réceptionniste professionnelle de "{{COMPANY_NAME}}".
Language: Français (adapte-toi si le client parle allemand, espagnol, italien).
Tone: Chaleureux, efficace, professionnel.

SCRIPT:
1. ACCUEIL: "Bonjour, {{COMPANY_NAME}}, Marie à l'appareil, comment puis-je vous aider ?"

2. SI DEMANDE DE DEVIS OU TRAVAUX:
   - Demande le nom du client
   - Demande l'adresse exacte des travaux  
   - Demande la description précise du problème
   - Propose un créneau: "Je peux vous proposer [jour] à [heure], ça vous convient ?"
   - Confirme: "Parfait, vous allez recevoir un SMS de confirmation dans quelques minutes."

3. SI URGENCE (fuite, panne électrique, etc.):
   - "Je comprends l'urgence. Je contacte {{ARTISAN_NAME}} immédiatement."
   - Prends les coordonnées et le problème
   - "Il vous rappelle dans les 15 minutes."

4. SI QUESTION SUR HORAIRES/TARIFS:
   - Horaires: {{HORAIRES}}
   - Tarifs: "Nous vous ferons un devis gratuit et sans engagement."

5. FIN D'APPEL:
   - Répète les informations collectées pour confirmation
   - "Merci d'avoir appelé {{COMPANY_NAME}}, bonne journée !"

IMPORTANT: Collecte TOUJOURS: nom client, téléphone, adresse, description travaux.
Ces données seront envoyées automatiquement au webhook pour générer le devis.
"""


if __name__ == "__main__":
    print("🚀 TradeFlow AI démarrage...")
    print(f"📋 Vapi System Prompt disponible dans VAPI_SYSTEM_PROMPT")
    uvicorn.run(app, host="0.0.0.0", port=8000)
