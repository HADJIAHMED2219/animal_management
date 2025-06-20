import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

# Connexion Google Sheets
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds_json = os.environ['GOOGLE_CREDENTIALS']
creds_dict = json.loads(creds_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

sheet_file = client.open("Animaux ESP32")

# Connexion aux 3 feuilles
animal_sheet = sheet_file.worksheet("animal")
users_sheet = sheet_file.worksheet("users")
requests_sheet = sheet_file.worksheet("registration_requests")

def get_users():
    return users_sheet.get_all_records()

def add_user(username, password, role, email, eleveur_id):
    users_sheet.append_row([eleveur_id, username, password, role, email])

def get_registration_requests():
    return requests_sheet.get_all_records()

from datetime import datetime

def add_registration_request(name, first_name, email, card_number, status="en attente"):
    # Récupérer toutes les demandes existantes
    existing_requests = requests_sheet.get_all_records()
    
    # Calculer le prochain ID automatiquement
    next_id = len(existing_requests) + 1

    # Ajouter la nouvelle demande dans le bon ordre des colonnes
    requests_sheet.append_row([
        next_id,               # Colonne A : ID
        name,                  # Colonne B : Name
        first_name,            # Colonne C : First_name
        email,                 # Colonne D : Email
        card_number,           # Colonne E : Card_number
        status,                # Colonne F : Status
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Colonne G : Request_date
    ])

def get_animals_for_eleveur(eleveur_id):
    animals = animal_sheet.get_all_records()
    return [animal for animal in animals if str(animal['Eleveur_ID']) == str(eleveur_id)]

def get_next_user_id():
    users = get_users()
    if not users:
        return 1
    return max(int(user['Eleveur_ID']) for user in users) + 1
