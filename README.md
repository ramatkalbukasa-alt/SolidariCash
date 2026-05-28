# SolidariCash

Plateforme de gestion de tontine — Système de contributions, rotations et distributions.

## Stack Technique
- **Backend**: Python 3.11 · Django 4.2 · Django REST Framework
- **Frontend**: HTML5 · Tailwind CSS (CDN) · JavaScript
- **Base de données**: SQLite (dev) / PostgreSQL (prod)
- **Rapports**: ReportLab (PDF) · OpenPyXL (Excel)
- **Auth**: Django Sessions + JWT (API)

---

## Installation rapide (Windows)

```powershell
# 1. Créer l'environnement virtuel
python -m venv venv
.\venv\Scripts\activate

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Copier la config
copy .env.example .env
# Éditez .env avec vos paramètres

# 4. Migrer la base de données
python manage.py migrate

# 5. Créer l'administrateur
python manage.py create_admin

# 6. Lancer le serveur
python manage.py runserver
```

Accès : http://127.0.0.1:8000

**Identifiants par défaut**
- Username : `admin`
- Password : `Admin@SolidariCash2025`

---

## Structure du projet

```
SolidariCash/
├── apps/
│   ├── authentication/   # Utilisateurs, login, JWT
│   ├── members/          # Membres + Têtes
│   ├── cycles/           # Cycles mensuels
│   ├── contributions/    # Paiements
│   ├── rotation/         # Moteur de rotation
│   ├── distributions/    # Distributions
│   ├── emergencies/      # Demandes urgence
│   ├── notifications/    # Notifications in-app + email
│   ├── reports/          # PDF + Excel
│   └── audit/            # Journal d'audit
├── templates/            # Templates Django (dark theme)
├── static/               # CSS + JS
├── solidaricash/         # Config Django
└── manage.py
```

---

## Flux Admin

1. Connexion → Dashboard
2. Créer un cycle → Ouvrir les contributions
3. Ajouter des membres avec leurs têtes
4. Valider les paiements
5. Générer la rotation automatique
6. Traiter les urgences
7. Effectuer les distributions
8. Générer les rapports PDF/Excel
9. Clôturer le cycle

## Flux Membre

1. Connexion → Dashboard
2. Voir ses contributions → Soumettre paiement
3. Attendre validation admin
4. Voir position dans la rotation
5. Soumettre urgence si nécessaire
6. Recevoir distribution → Télécharger reçu PDF

---

## API REST

Préfixe : `/api/`

| Ressource | Endpoint |
|-----------|----------|
| Auth JWT | `/api/auth/token/` |
| Membres | `/api/members/` |
| Cycles | `/api/cycles/` |
| Contributions | `/api/contributions/` |
| Rotation | `/api/rotation/` |
| Distributions | `/api/distributions/` |
| Urgences | `/api/emergencies/` |
| Notifications | `/api/notifications/` |

---

## Règles métier clés

- Commission admin : **2%** (configurable via `.env`)
- Montant distribuable = Total collecté − Commission
- Une tête = une contribution par cycle
- Deux têtes du même membre ne peuvent pas être consécutives
- Un membre suspendu ne peut pas recevoir de distribution
- Les urgences sont limitées à **une fois par cycle**
- Tous les historiques sont **immuables** (non supprimables)

---

## Production (PostgreSQL + Gunicorn + Nginx)

```env
# .env
DEBUG=False
DB_ENGINE=django.db.backends.postgresql
DB_NAME=solidaricash_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

```bash
python manage.py collectstatic
gunicorn solidaricash.wsgi:application --bind 0.0.0.0:8000
```
