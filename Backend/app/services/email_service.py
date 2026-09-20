# backend/app/services/email_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Use environment variables in production. Hardcoded here for prototype testing.
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "abhisharma508844@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "kuchbhia nbhi ahi")

def send_recovery_email(to_email: str, customer_name: str, product_name: str, product_price: float, image_url: str, token: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "You left something in your cart!"
    msg["From"] = SMTP_USERNAME
    msg["To"] = to_email

    # Secure links using JWT
    checkout_url = f"http://127.0.0.1:5500/Frontend/cart.html?recovery_token={token}"
    help_url = f"http://127.0.0.1:5500/Frontend/ai-support.html?recovery_token={token}"

    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: auto;">
        <h2>Hi {customer_name} 👋</h2>
        <p>You left this product in your cart:</p>
        <div style="border: 1px solid #eee; padding: 15px; text-align: center; border-radius: 8px;">
            <img src="{image_url}" alt="{product_name}" style="max-width: 150px;">
            <h3>{product_name}</h3>
            <p style="font-size: 18px; color: #27ae60;"><b>₹{product_price}</b></p>
        </div>
        <br>
        <a href="{checkout_url}" style="background-color: #3498db; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Continue Checkout</a>
        <br><br>
        <p>Need help deciding?</p>
        <a href="{help_url}" style="color: #e67e22; text-decoration: none; font-weight: bold;">Get AI Product Help</a>
      </body>
    </html>
    """
    
    msg.attach(MIMEText(html, "html"))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Email failed: {e}")
        return False