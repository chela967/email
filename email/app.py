import smtplib
import random
import re  # Import regex for email validation
import time  # For tracking code expiration
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

# Email SMTP Settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "chelangatandrew404@gmail.com"  # Replace with your Gmail
SENDER_PASSWORD = "huwt vzxw hrby ssdt"  # Replace with your App Password

# Store generated codes and timestamps
email_codes = {}
email_sent_time = {}
RESEND_LIMIT = 180  # 3 minutes (in seconds) to request a new code
CODE_EXPIRATION_TIME = 120  # 2 minutes (in seconds) for code expiration

def send_verification_email(user_email):
    """Generate and send a verification code."""
    code = random.randint(100000, 999999)  # 6-digit code
    email_codes[user_email] = code  # Store the code
    email_sent_time[user_email] = time.time()  # Store the current time for expiration check

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()  # Secure the connection
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        message = f"Subject: KUGSA Email Verification\n\nYour verification code for KUGSA is {code}."
        server.sendmail(SENDER_EMAIL, user_email, message)

@app.route("/", methods=["GET", "POST"])
def verify_email():
    """Handles email verification."""
    if request.method == "POST":
        email = request.form["email"]
        print(f"Email entered: {email}")  # Debug statement

        # Ensure the email contains 'gf' before '@kab.ac.ug'
        if re.match(r"^\d+[a-zA-Z0-9]*gf@kab\.ac\.ug$", email):  
            print("Email is valid. Proceeding to send verification code.")  # Debug statement
            # Check if the code was recently sent or expired
            if email in email_sent_time:
                time_diff = time.time() - email_sent_time[email]
                if time_diff < RESEND_LIMIT:
                    message = "❌ You can request the code again after 3 minutes."
                    print(message)  # Debug statement
                    return render_template("index.html", message=message)
                else:
                    send_verification_email(email)
            else:
                send_verification_email(email)

            return redirect(url_for("verify_code", email=email))
        else:
            message = "❌ Invalid email. Only emails containing 'gf@kab.ac.ug' can vote."
            print(message)  # Debug statement
            return render_template("index.html", message=message)

    return render_template("index.html")

@app.route("/verify", methods=["GET", "POST"])
def verify_code():
    """Verify the user's code."""
    email = request.args.get("email")  # Get email from URL
    print(f"Email in verify_code: {email}")  # Debug statement

    if request.method == "POST":
        user_code = request.form["code"]
        print(f"Code entered: {user_code}")  # Debug statement

        # Check if the code has expired (e.g., 2 minutes)
        if email in email_codes:
            time_diff = time.time() - email_sent_time[email]
            if time_diff > CODE_EXPIRATION_TIME:  # 2 minutes expiration
                message = "❌ The code has expired. Please request a new one."
                print(message)  # Debug statement
                return render_template("verify.html", message=message, email=email)

            if int(user_code) == email_codes[email]:
                # Redirect to the hidden Google Form route
                return redirect(url_for("redirect_to_form"))
            else:
                message = "❌ Incorrect code. Try again."
                print(message)  # Debug statement
                return render_template("verify.html", message=message, email=email)
        else:
            message = "❌ No verification code found. Please request a new one."
            print(message)  # Debug statement
            return render_template("verify.html", message=message, email=email)

    # Pass the email to the template so it is displayed
    return render_template("verify.html", email=email)

@app.route("/resend_code", methods=["POST"])
def resend_code():
    """Allow users to request a new code."""
    email = request.form["email"]

    if email in email_sent_time:
        time_diff = time.time() - email_sent_time[email]
        if time_diff < RESEND_LIMIT:
            message = "❌ You can request the code again after 3 minutes."
            print(message)  # Debug statement
            return render_template("index.html", message=message)
        else:
            send_verification_email(email)
            message = "✅ A new verification code has been sent to your email."
            print(message)  # Debug statement
            return render_template("index.html", message=message)
    else:
        message = "❌ No verification code found. Please request a new one."
        print(message)  # Debug statement
        return render_template("index.html", message=message)

# Hidden route to redirect user to the Google Form
@app.route("/redirect_to_form")
def redirect_to_form():
    # This will redirect to your Google Form while keeping the actual link hidden
    return redirect("https://forms.gle/mnp2uM2juePZesfW6")

# Error handlers
@app.errorhandler(500)
def internal_error(error):
    return "500 Internal Server Error: Something went wrong!"

@app.errorhandler(404)
def not_found_error(error):
    return "404 Not Found: The requested URL was not found."

if __name__ == "__main__":
    app.run(debug=True)
