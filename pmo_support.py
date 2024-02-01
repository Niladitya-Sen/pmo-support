from flask import Flask, render_template, request, jsonify, session
import pyodbc
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)


db_connection_string = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=103.145.51.250;"
    "Database=PMO360_DB;"
    "UID=PMOlogbook_Usr;"
    "PWD=PMO_log360!x4;"
)

# Email credentials
sender_email = "dev@waysaheadglobal.com"
password = "Singapore@2022"

temp_otps = {}
user_sessions = {}

app.secret_key = "Skio_Idea"


# Function to generate OTP
def generate_otp():
    return str(random.randint(1000, 9999))


# Function to send OTP via email
def send_otp(email, otp):
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = email
    message["Subject"] = "OTP Verification"
    body = f"Your OTP: {otp}"
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.office365.com", 587) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, email, message.as_string())


def check_email_in_database(email):
    connection = pyodbc.connect(db_connection_string)
    cursor = connection.cursor()

    query = f"SELECT * FROM [User] WHERE Email=?"
    result = cursor.execute(query, email).fetchone()

    connection.close()

    return result is not None


def fetch_ticket_status(Error_ticket):
    connection = pyodbc.connect(db_connection_string)
    cursor = connection.cursor()

    query = "SELECT Status,Comment,StatusId,UpdatedDate,CreatedDate,Impact,PriorityId FROM Logbook WHERE LogbookId = ?"
    result = cursor.execute(query, (Error_ticket)).fetchall()

    connection.close()
    return result[0] if result else "Ticket not found"


def get_issupport(email):
    connection = pyodbc.connect(db_connection_string)
    cursor = connection.cursor()
    query = f"SELECT IsSupport from [User] WHERE Email=?"
    result = cursor.execute(query, email).fetchone()
    connection.close()

    if result:
        return result[0]
    else:
        return False


@app.route("/support")
def index():
    return render_template("index.html")


@app.route("/support/api/chatbot", methods=["POST"])
def chatbot_api():
    data = request.get_json()
    email = data.get("email")
    otp = data.get("otp")
    message = data.get("message")
    check = get_issupport(email)
    if otp is None and message is None:
        if check_email_in_database(email) and check:
            otp = generate_otp()
            temp_otps[email] = otp
            send_otp(email, otp)
            return jsonify(
                {
                    "status": "success",
                    "message": "Please enter the OTP sent to your email.",
                }
            )
        else:
            return jsonify({"status": "error", "message": "Invalid email id."})

    elif message is None:
        if otp == temp_otps.get(email):
            del temp_otps[email]
            return jsonify(
                {
                    "status": "success",
                    "message": "OTP verified. Please enter your ticket number",
                }
            )
        else:
            return jsonify(
                {
                    "status": "error",
                    "message": "Incorrect OTP. Please enter the correct OTP.",
                }
            )

    elif message is not None:
        ticket_status = fetch_ticket_status(message)
        return jsonify(
            {
                "status": "success",
                "message": [
                    f"Ticket Status:{ticket_status[0]}",
                    f"\tComment:{ticket_status[1]}",
                    f"\tStatusId:{ticket_status[2]}",
                    f"\t UpdatedDate:{ticket_status[3]}",
                    f"\tCreatedDate:{ticket_status[4]}",
                    f"\tImpact:{ticket_status[5]}",
                    f"\tPriorityId:{ticket_status[6]}",
                ],
            }
        )
    else:
        return jsonify({"status": "error", "message": "Invalid step."})


if __name__ == "__main__":
    app.run(debug=False, port=3023)
