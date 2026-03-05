# TradeFlow AI v2.0

**Système intelligent de génération automatique de devis pour artisans**

TradeFlow AI transforme les appels téléphoniques et notes vocales en devis PDF professionnels, envoyés instantanément aux clients.

## 🚀 Fonctionnalités

- **📞 Appel → Devis en 3 secondes** : Vapi.ai répond aux clients, extrait les informations
- **🤖 Claude Sonnet** : Analyse intelligente des transcripts (FR/DE/ES/IT/NL)
- **📄 PDF Professionnels** : Devis conformes avec design moderne
- **📱 SMS Artisan** : Notification instantanée sur chaque devis généré
- **📧 Email Client** : Envoi automatique du devis PDF au client
- **📊 Google Sheets** : Synchronisation automatique via Make.com
- **🔧 API REST** : Intégration complète avec webhooks

## 📋 Prérequis

- Python 3.8+
- Comptes : Anthropic, Twilio, Resend, Vapi.ai, Make.com

## 🛠️ Installation

### 1. Cloner et installer

```bash
git clone <repository>
cd tradeflow-ai
pip install -r requirements.txt
```

### 2. Configurer les variables d'environnement

```bash
cp .env.example .env
# Éditer .env avec vos clés API
```

### 3. Démarrer le serveur

```bash
python main.py
```

Le serveur démarre sur `http://localhost:8000`

## 🔗 Configuration des services

### Anthropic Claude
```
console.anthropic.com → API Keys
Clé requise : sk-ant-xxx
```

### Twilio (SMS)
```
1. twilio.com → Sign up
2. Get a trial number (+33 français recommandé)
3. Account SID + Auth Token
4. Numéro d'envoi français
```

### Resend (Email)
```
1. resend.com → Sign up
2. API Keys → Create API Key
3. Domains → Ajouter votre domaine ou utiliser onboarding@resend.dev
```

### Vapi.ai (Appels AI)
```
1. vapi.ai → Sign up
2. Phone Numbers → Buy Number (+33)
3. Assistants → Create Assistant
4. System Prompt : copier VAPI_SYSTEM_PROMPT du code
5. Functions/Tools → Webhook vers votre serveur
```

### Make.com (Google Sheets)
```
1. make.com → Create scenario
2. Module 1: Webhooks → Custom Webhook
3. Module 2: Google Sheets → Add a Row
4. Connecter et mapper les champs
```

## 📡 API Endpoints

### Génération de devis manuelle
```bash
curl -X POST http://localhost:8000/api/devis/generate \
  -H "Content-Type: application/json" \
  -d '{"transcript": "Pour Monsieur Dupont au 12 rue de Rivoli, remplacement tableau électrique 500 euros et 4 heures main oeuvre à 65 euros"}'
```

### Webhook Vapi
```
POST /vapi-webhook
Reçoit automatiquement les rapports d'appels Vapi
```

### Téléchargement PDF
```
GET /api/devis/pdf/{numero}
Ex: http://localhost:8000/api/devis/pdf/DEV-202603-4521
```

### Note vocale
```bash
curl -X POST http://localhost:8000/api/voice/note \
  -H "Content-Type: application/json" \
  -d '{"text": "Client Martin, changement prise salon, 150€ forfait"}'
```

## 🚀 Déploiement sur Render

1. **Push sur GitHub**
```bash
git init
git add .
git commit -m "TradeFlow AI v2.0"
git remote add origin https://github.com/username/tradeflow-ai
git push -u origin main
```

2. **Configuration Render**
- Runtime: Python 3
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Ajouter toutes les variables d'environnement

3. **Webhook Vapi**
Mettre à jour l'URL webhook dans Vapi.ai vers votre URL Render

## 📊 Flux complet

```
📞 Appel client → Vapi.ai (Sophie)
       ↓
🤖 Analyse transcript → Claude Sonnet
       ↓
📄 Génération PDF → ReportLab
       ↓
📱 SMS Artisan → Twilio
📧 Email Client → Resend
📊 Google Sheets → Make.com
```

## 🔧 Variables d'environnement

| Variable | Description | Exemple |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Clé API Claude | `sk-ant-xxx` |
| `ARTISAN_NAME` | Nom de l'entreprise | `Martin Électricité` |
| `ARTISAN_SIRET` | Numéro SIRET | `123 456 789 00010` |
| `ARTISAN_TVA_INTRA` | TVA Intracommunautaire | `FR12345678900` |
| `ARTISAN_ADDRESS` | Adresse de l'entreprise | `12 Rue de la Paix, 75001 Paris` |
| `ARTISAN_EMAIL` | Email de l'entreprise | `jean@martin-electricite.fr` |
| `ARTISAN_PHONE` | Téléphone de l'artisan | `+33612345678` |
| `TWILIO_ACCOUNT_SID` | SID Twilio | `ACxxx` |
| `TWILIO_AUTH_TOKEN` | Token Twilio | `xxx` |
| `TWILIO_FROM_NUMBER` | Numéro Twilio | `+33XXXXXXXXX` |
| `RESEND_API_KEY` | Clé Resend | `re_xxx` |
| `MAKE_WEBHOOK_URL` | URL Make.com | `https://hook.eu1.make.com/xxx` |

## 🎯 Exemples d'utilisation

### Français
```
"Pour Monsieur Dupont rue de la Paix, remplacement tableau électrique 500 euros et 4 heures main d'oeuvre à 65 euros"
```

### Allemand
```
"Für Herrn Müller, Austausch Sicherungskasten 600 Euro und 3 Stunden Arbeit à 70 Euro"
```

### Espagnol
```
"Para el señor García, sustitución cuadro eléctrico 550 euros y 4 horas de mano de obra a 60 euros"
```

## 🐛 Dépannage

### Erreurs courantes
- **ImportError** : `pip install -r requirements.txt`
- **Claude JSON invalide** : Retry automatique intégré
- **Vapi webhook** : Vérifier les logs Vapi.ai
- **Render déploiement** : Vérifier Procfile et variables env

### Logs et monitoring
```bash
# Logs de l'application
python main.py

# Test endpoint
curl http://localhost:8000/health
```

## 📈 Support

- 📧 Email support : support@tradeflow.ai
- 📖 Documentation : docs.tradeflow.ai
- 🐛 Issues : GitHub Issues

---

**TradeFlow AI v2.0** - *J'aide les artisans à récupérer leur temps* ⚡
