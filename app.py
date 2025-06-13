from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random

from sheets import *
from email_utils import send_email, generate_password

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']  # Correction ici
        password = request.form['password']  # Correction ici

        users = get_users()
        user = next((u for u in users if u['Username'] == username), None)

        if user:
            if (user['Password'].startswith('pbkdf2:') and 
                check_password_hash(user['Password'], password)) or user['Password'] == password:

                session['user_id'] = user['Eleveur_ID']
                session['username'] = user['Username']
                session['role'] = user['Role']

                if user['Role'] == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('eleveur_dashboard'))

        flash('Invalid username or password', 'danger')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/register_request', methods=['GET', 'POST'])
def register_request():
    if request.method == 'POST':
        name = request.form['name']
        first_name = request.form['first_name']
        email = request.form['email']
        card_number = request.form['card_number']

        add_registration_request(name, first_name, email, card_number)

        admin_emails = [user['Email'] for user in get_users() if user['Role'] == 'admin']

        subject = "New Registration Request"
        body = f"""A new registration request has been submitted:

Name: {name} {first_name}
Email: {email}
Card Number: {card_number}"""

        for admin_email in admin_emails:
            send_email(admin_email, subject, body)

        flash('Your registration request has been submitted.', 'success')
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    users = get_users()
    animals = animal_sheet.get_all_records()

    eleveurs = []
    for user in users:
        if user['Role'] == 'éleveur':
            eleveur_id = user['Eleveur_ID']
            animal_count = sum(1 for animal in animals if str(animal['Eleveur_ID']) == str(eleveur_id))
            eleveur_animals = [animal for animal in animals if str(animal['Eleveur_ID']) == str(eleveur_id)]
            last_sync = max((animal['Last_sync'] for animal in eleveur_animals if animal['Last_sync']), default='N/A')

            eleveurs.append({
                'Eleveur_ID': eleveur_id,
                'Username': user['Username'],
                'Email': user['Email'],
                'animal_count': animal_count,
                'last_sync': last_sync
            })

    return render_template('admin/dashboard.html', eleveurs=eleveurs)

@app.route('/admin/requests')
def admin_requests():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    all_requests = get_registration_requests()
    requests = [req for req in all_requests if req.get('Status', '').lower() == 'en attente']

    return render_template('admin/requests.html', requests=requests)

@app.route('/admin/process_request/<int:request_id>/<action>')
def process_request(request_id, action):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    requests = get_registration_requests()
    users = get_users()

    if request_id > len(requests) or request_id <= 0:
        flash('Request not found', 'danger')
        return redirect(url_for('admin_requests'))

    req = requests[request_id - 1]
    sheet_row = request_id + 1

    if action == 'accept':
        username_base = req['First_name'][0].lower() + req['Name'].lower()
        username = username_base
        password = generate_password()

        existing_usernames = [user['Username'] for user in users]
        counter = 1
        while username in existing_usernames:
            username = f"{username_base}{counter}"
            counter += 1

        new_eleveur_id = get_next_user_id()
        hashed_password = generate_password_hash(password)
        add_user(username, hashed_password, 'éleveur', req['Email'], new_eleveur_id)

        requests_sheet.update_cell(sheet_row, 5, 'accepté')

        subject = "Your Registration Has Been Approved"
        body = f"""Dear {req['First_name']} {req['Name']},

Your registration request has been approved. Here are your login credentials:

Username: {username}
Password: {password}

Best regards."""

        send_email(req['Email'], subject, body)
        flash('Request approved and user created', 'success')

    elif action == 'reject':
        requests_sheet.update_cell(sheet_row, 5, 'refusé')

        subject = "Your Registration Has Been Rejected"
        body = f"""Dear {req['First_name']} {req['Name']},

We regret to inform you that your registration request has been rejected.

Best regards."""

        send_email(req['Email'], subject, body)
        flash('Request rejected', 'info')

    return redirect(url_for('admin_requests'))

@app.route('/eleveur/dashboard')
def eleveur_dashboard():
    if 'user_id' not in session or session['role'] != 'éleveur':
        return redirect(url_for('login'))

    animals = animal_sheet.get_all_records()
    user_animals = [animal for animal in animals if str(animal['Eleveur_ID']) == str(session['user_id'])]

    return render_template('eleveur/dashboard.html', animals=user_animals)

@app.route('/sync_animals', methods=['POST'])
def sync_animals():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Not authenticated'}), 401

    data = request.json
    eleveur_id = session['user_id']

    if not data or 'animals' not in data:
        return jsonify({'status': 'error', 'message': 'Invalid data format'}), 400

    try:
        all_animals = animal_sheet.get_all_records()
        existing_animals = [animal for animal in all_animals if str(animal['Eleveur_ID']) == str(eleveur_id)]
        before_count = len(existing_animals)
        other_animals = [animal for animal in all_animals if str(animal['Eleveur_ID']) != str(eleveur_id)]

        new_animals = []
        for animal in data['animals']:
            new_animals.append([
                animal['rfid_tag'],
                animal['category'],
                animal['gender'],
                animal['birth_date'],
                animal['vaccines'],
                eleveur_id,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ])

        final_animals = []
        for animal in other_animals:
            final_animals.append([
                animal['RFID_tag'],
                animal['Category'],
                animal['Gender'],
                animal['Birth_date'],
                animal['Vaccines'],
                animal['Eleveur_ID'],
                animal['Last_sync']
            ])

        final_animals.extend(new_animals)

        animal_sheet.clear()
        animal_sheet.append_row(['RFID_tag', 'Category', 'Gender', 'Birth_date', 'Vaccines', 'Eleveur_ID', 'Last_sync'])
        animal_sheet.append_rows(final_animals)

        after_count = len(new_animals)

        action = "Full database replacement"
        if before_count == 0 and after_count > 0:
            action = "Initial population"
        elif after_count > before_count:
            action = f"Added {after_count - before_count} animals"
        elif after_count < before_count:
            action = f"Removed {before_count - after_count} animals"

        notify_admin_on_change(eleveur_id, action)

        return jsonify({'status': 'success', 'message': f'Animals synchronized successfully. {action}'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/admin/breeder_animals/<int:breeder_id>')
def breeder_animals(breeder_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    users = get_users()
    animals = animal_sheet.get_all_records()

    breeder = next((user for user in users if str(user['Eleveur_ID']) == str(breeder_id)), None)
    breeder_animals = [animal for animal in animals if str(animal['Eleveur_ID']) == str(breeder_id)]

    return render_template('admin/breeder_animals.html', animals=breeder_animals, breeder=breeder)

def notify_admin_on_change(breeder_id, action):
    try:
        users = get_users()
        admin_emails = [user['Email'] for user in users if user['Role'] == 'admin']
        breeder = next((user for user in users if str(user['Eleveur_ID']) == str(breeder_id)), None)

        if not admin_emails:
            return False

        subject = "Animal Database Modification Alert"
        body = f"""Breeder data modification detected:

- Breeder ID: {breeder_id}
- Breeder Name: {breeder['Username'] if breeder else 'Unknown'}
- Action: {action}
- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please review the changes in the admin dashboard."""

        for email in admin_emails:
            send_email(email, subject, body)

        return True
    except Exception as e:
        print(f"Failed to send admin notification: {e}")
        return False

@app.route('/simulator')
def simulator():
    return render_template('simulator.html')

@app.route('/simulate_sync', methods=['POST'])
def simulate_sync():
    if 'user_id' not in session or session['role'] != 'éleveur':
        return jsonify({'status': 'error', 'message': 'Not authenticated or not an eleveur'}), 401

    test_animals = [
        {'rfid_tag': f"RFID{random.randint(1000, 9999)}", 'category': 'Bovin', 'gender': random.choice(['Male', 'Female']), 'birth_date': f"202{random.randint(0, 3)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}", 'vaccines': 'Vaccine A, Vaccine B'},
        {'rfid_tag': f"RFID{random.randint(1000, 9999)}", 'category': 'Ovin', 'gender': random.choice(['Male', 'Female']), 'birth_date': f"202{random.randint(0, 3)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}", 'vaccines': 'Vaccine C'}
    ]

    response = app.test_client().post('/sync_animals', json={'animals': test_animals}, headers={'Content-Type': 'application/json'})
    return response

def send_monthly_notifications():
    with app.app_context():
        users = get_users()
        eleveurs = [user for user in users if user['Role'] == 'éleveur']

        subject = "Monthly Reminder: Synchronize Your Animals"
        body = "Dear Eleveur,\n\nThis is a monthly reminder to synchronize your animal data with the central database.\n\nPlease ensure all your animals' information is up to date.\n\nBest regards."

        for eleveur in eleveurs:
            send_email(eleveur['Email'], subject, body)

if __name__ == '__main__':
    app.run(debug=True)
