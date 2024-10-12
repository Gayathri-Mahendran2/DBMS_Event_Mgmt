
from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# MySQL Connection Configuration
db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='fidelity',
    port='3306',
    database='Event_Mgmt'
)

cursor = db.cursor()


def generate_next_client_id():
    cursor.execute("SELECT client_id FROM clients ORDER BY client_id DESC LIMIT 1")
    last_id = cursor.fetchone()
    if last_id:
        # Extract the numeric part from the client ID (C1, C2...)
        last_num = int(last_id[0][1:])  # Remove 'C' and convert the rest to int
        new_id = f"C{last_num + 1}"
    else:
        new_id = "C1"
    return new_id

# Function to generate next event ID
def generate_next_event_id():
    cursor.execute("SELECT event_id FROM events ORDER BY event_id DESC LIMIT 1")
    last_id = cursor.fetchone()
    if last_id:
        # Extract the numeric part from the event ID (E1, E2...)
        last_num = int(last_id[0][1:])  # Remove 'E' and convert the rest to int
        new_id = f"E{last_num + 1}"
    else:
        new_id = "E1"
    return new_id


@app.route('/')
def index():
    cursor.execute("SELECT * FROM clients limit 10")
    clients = cursor.fetchall()
    cursor.execute("SELECT events.event_id, events.date, clients.name FROM events JOIN clients ON events.client_id = clients.client_id limit 10")
    events = cursor.fetchall()
    return render_template('index.html', clients=clients, events=events)

# Add New Client
@app.route('/add_client', methods=['POST'])
def add_client():
    client_id = generate_next_client_id()
    name = request.form['name']
    contact = request.form['contact']
    
    sql = "INSERT INTO clients (client_id, name, contact) VALUES (%s, %s, %s)"
    val = (client_id, name, contact)
    cursor.execute(sql, val)
    db.commit()
    
    return redirect('/')

# Add New Event
@app.route('/add_event', methods=['POST'])
def add_event():
    event_id = generate_next_event_id()
    date = request.form['date']
    clientid = request.form['clientid']
    
    sql = "INSERT INTO events (event_id, date, client_id) VALUES (%s, %s, %s)"
    val = (event_id, date, clientid)
    cursor.execute(sql, val)
    db.commit()
    
    return redirect('/')

# Delete Client
@app.route('/delete_client', methods=['POST'])
def delete_client():
    clientid = request.form['client_id']
    
    cursor.execute("DELETE FROM events WHERE client_id = %s", (clientid,))
    cursor.execute("DELETE FROM clients WHERE client_id = %s", (clientid,))
    db.commit()
    
    return redirect('/')

# Delete Event
@app.route('/delete_event', methods=['POST'])
def delete_event():
    eventid = request.form['event_id']
    
    cursor.execute("DELETE FROM events WHERE event_id = %s", (eventid,))
    db.commit()
    
    return redirect('/')

@app.route('/update_client/<client_id>', methods=['GET'])
def update_client_form(client_id):
    # Fetch client details to pre-fill the form
    cursor.execute("SELECT * FROM clients WHERE client_id = %s", (client_id,))
    client = cursor.fetchone()
    return render_template('update_client.html', client=client)

# Update Client Logic
@app.route('/update_client/<client_id>', methods=['POST'])
def update_client(client_id):
    name = request.form['name']
    contact = request.form['contact']

    sql = "UPDATE clients SET name = %s, contact = %s WHERE client_id = %s"
    val = (name, contact, client_id)
    cursor.execute(sql, val)
    db.commit()

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
 

