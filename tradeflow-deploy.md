# TRADEFLOW AI — DÉPLOIEMENT

## 1. LOCAL (tester en 2 minutes)

```bash
pip install -r requirements.txt
ANTHROPIC_API_KEY=sk-ant-xxx python main.py
```

Test immédiat:
```bash
curl -X POST http://localhost:8000/api/devis/generate \
  -H "Content-Type: application/json" \
  -d '{"transcript": "Pour Monsieur Dupont rue de Rivoli, remplacement tableau électrique 500 euros et 4 heures de main oeuvre à 60 euros"}'
```

---

## 2. RENDER.COM (gratuit pour démarrer)

1. Créer compte sur render.com
2. New → Web Service → Connect GitHub
3. Environment Variables:
   ```
   ANTHROPIC_API_KEY = sk-ant-xxx
   ```
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Deploy → URL: https://tradeflow-ai.onrender.com

---

## 3. VAPI.AI SETUP

1. vapi.ai → Create Assistant
2. System Prompt → copier VAPI_SYSTEM_PROMPT depuis main.py
3. Remplacer {{COMPANY_NAME}}, {{ARTISAN_NAME}}, {{HORAIRES}}
4. Tools → Add Webhook:
   - URL: https://tradeflow-ai.onrender.com/vapi-webhook
   - Events: end-of-call-report
5. Phone Numbers → Buy French number (+33) → $2/mois
6. Assign assistant → Done

---

## 4. STRIPE (paiement €79/mois)

```bash
pip install stripe
```

Ajouter dans main.py:
```python
import stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.post("/create-subscription")
async def create_subscription(request: Request):
    body = await request.json()
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price": "price_xxx",  # Ton Price ID Stripe
            "quantity": 1,
        }],
        mode="subscription",
        success_url="https://tradeflow.ai/merci",
        cancel_url="https://tradeflow.ai/tarifs",
    )
    return {"url": session.url}
```

---

## 5. FLOW COMPLET

```
Client appelle → Vapi répond en FR/DE/ES
       ↓
Vapi collecte: nom, adresse, travaux
       ↓
Fin d'appel → Webhook → /vapi-webhook
       ↓
Claude extrait les données (0.3 sec)
       ↓
ReportLab génère PDF devis (0.5 sec)
       ↓
Email au client (Resend) + SMS à l'artisan (Twilio)
       ↓
Total: 30 secondes après la fin d'appel
```

---

## VARIABLES D'ENVIRONNEMENT REQUISES

```
ANTHROPIC_API_KEY=sk-ant-xxx
STRIPE_SECRET_KEY=sk_live_xxx     (optionnel au début)
TWILIO_SID=xxx                    (pour SMS, optionnel)
TWILIO_TOKEN=xxx
RESEND_API_KEY=xxx                (pour email, optionnel)
```
