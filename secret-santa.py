import random
import smtplib
import csv
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def read_participants_from_csv(file_path):
    participants = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) == 2:  # Ensure each row has a name and an email
                name, email = row
                participants.append((name.strip(), email.strip()))
    return participants

def secret_santa(participants, sending_email, sending_email_password, smtp_server="smtp.gmail.com", smtp_port=465):
    """
    participants: List of tuples [(name1, email1, color), (name2, email2, color), ...]
    email: Your email address for sending
    email_password: Your email password for sending
    smtp_server: SMTP server (default is Gmail)
    smtp_port: SMTP port (default is 465 for SSL)
    """
    
    # Shuffle and assign participants
    names = [p[0] for p in participants]
    emails = [p[1] for p in participants]
    colors = [p[2] for p in participants]
    secret_santa_matches = names[:]
    
    while True:
        random.shuffle(secret_santa_matches)
        # Ensure no one gets themselves
        if all(names[i] != secret_santa_matches[i] for i in range(len(names))):
            break

    # Send emails
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
        server.login(sending_email, sending_email_password)
        
        for i, participant in enumerate(participants):
            name, recipient_email = participant
            secret_santa_match = secret_santa_matches[i]
            color_of_secret_santa_match = colors[names.index(secret_santa_match)]
            
            # Prepare the email
            message = MIMEMultipart("alternative")
            message["Subject"] = "Deine Wichtelperson"
            message["From"] = sending_email
            message["To"] = recipient_email
            
            text = f"Hallo {name},\n\nDein Wichtelpartner ist: {secret_santa_match}. Bitte markiere dein Geschenk in der Farbe {color_of_secret_santa_match} \n\nFrohe Weihnachten!"
            html = f"""
            <html>
                <body>
                    <p>Hallo {name},<br><br>
                    Dein Wichtelpartner ist: <b>{secret_santa_match}</b>.<br>
                    Bitte markiere dein Geschenk in der Farbe {color_of_secret_santa_match}<br><br>
                    Frohe Weihnachten!<br>
                    </p>
                </body>
            </html>
            """
            
            # Attach text and HTML content
            message.attach(MIMEText(text, "plain"))
            message.attach(MIMEText(html, "html"))
            
            # Send the email
            try:
                server.sendmail(sending_email, recipient_email, message.as_string())
                print(f"E-Mail erfolgreich an {name} gesendet ({recipient_email})")
            except Exception as e:
                print(f"Fehler beim Senden an {name} ({recipient_email}): {e}")

# read participants from csv file:



sending_email = os.getenv("SENDING_EMAIL")
sending_email_password = os.getenv("SENDING_EMAIL_PASSWORD")
smtp_server = os.getenv("SMTP_SERVER")
smtp_port = os.getenv("SMTP_PORT")
file_path = "participants.csv"  # Replace with the path to your CSV file
participants = read_participants_from_csv(file_path)

secret_santa(participants, sending_email, sending_email_password, smtp_server, smtp_port)
