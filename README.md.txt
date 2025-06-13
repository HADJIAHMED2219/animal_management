# Animal Management System - ESP32 + Google Sheets + Flask

## 🚀 Description
Application web de gestion d'animaux qui permet :
- 🔄 Synchronisation des animaux via ESP32 (vers Google Sheets)
- 🐑 Suivi des animaux par éleveurs
- 👤 Gestion des utilisateurs et demandes d'inscription
- 📩 Notifications email pour les administrateurs
- 🌐 Hébergement sur Render

---

## 🗂️ Structure du projet
```text
animal_management/
├── app.py                 # Application principale Flask
├── sheets.py              # Connexion Google Sheets
├── email_utils.py         # Envoi d'emails et génération de mots de passe
├── requirements.txt       # Dépendances
├── Procfile               # Fichier de déploiement Render
├── templates/             # Fichiers HTML
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── simulator.html
│   └── admin/
│       ├── dashboard.html
│       ├── requests.html
│       └── breeder_animals.html
└── static/                # (Optionnel) Fichiers CSS ou images
    └── style.css
✅ Technologies utilisées

    ESP32 (collecte des données)

    Google Sheets (base de données cloud)

    Flask (framework web Python)

    Gmail SMTP (envoi d'emails)

    Render (hébergement web)

🔧 Installation locale
git clone https://github.com/ton-utilisateur/animal_management.git
cd animal_management
pip install -r requirements.txt
python app.py
🌐 Déploiement sur Render
1️⃣ Créer un dépôt GitHub

    Upload tous les fichiers du projet.

2️⃣ Créer un Web Service sur Render

    Connecte Render à ton dépôt GitHub.

    Branche ton dépôt.

3️⃣ Configurer les variables Render

Dans Environment > Environment Variables :

GOOGLE_CREDENTIALS = {contenu compact du fichier credentials.json}

👉 Utilise un site comme https://www.freeformatter.com/json-escape.html pour convertir ton fichier credentials.json en une ligne.
4️⃣ Configuration Render

    Build Command : pip install -r requirements.txt

    Start Command : gunicorn app:app

5️⃣ Lancer le déploiement

    Render détecte automatiquement Flask via gunicorn.

    Une URL publique sera générée pour accéder à ton application.

🔑 Authentification par défaut

    Admin Username: HADJIAhmed

    Admin Password: 07No1986/

📧 Configuration email

L'application utilise :

    Gmail SMTP : smtp.gmail.com

    Adresse : ahmed.hadji2219@gmail.com

    Mot de passe spécifique : ussi gxpf jpax baxy

Assure-toi que :

    L’accès aux applications moins sécurisées est activé.

    Tu peux utiliser un mot de passe spécifique à l'application pour plus de sécurité.

🛠️ Fonctionnalités disponibles

    ✅ ESP32 ➜ Synchronisation vers Google Sheets

    ✅ Gestion des utilisateurs

    ✅ Demandes d'inscription

    ✅ Tableau de bord Admin et Éleveur

    ✅ Notification email en temps réel

    ✅ Simulateur de synchronisation

✨ Développeur

    Projet réalisé par : HADJIAhmed


---

👉 Si tu veux, je peux te générer directement le fichier `README.md` dans le dossier `.zip` et te le renvoyer.

Tu veux que je te prépare le projet avec le fichier `README.md` inclus et te l’envoie ? 😊
