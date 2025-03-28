import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import logging
import os

def send_email(subject, body, attachment_path=None):
    """Sends an HTML email with a full-screen SVG background and enhanced styling."""
    sender_email = "farhadjaved95@gmail.com"
    receiver_email = "farhadjaved95@gmail.com"
    password = "zrhd lzox svep vudm"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    formatted_body = "<br>".join(body.split("\n"))

    # Enhanced HTML Email with Full-Screen SVG Background
    body_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Suspicious Activity Alert</title>
        
        <!-- Bootstrap -->
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        
        <!-- Google Fonts -->
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
        
        <!-- FontAwesome -->
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">

        <style>
            body {{
                font-family: 'Poppins', sans-serif;
                background-color: #808080;
                margin: 0;
                padding: 0;
            }}
            .email-wrapper {{
                width: 30%;
                height: 50%;
                display: flex;
                margin-left: 340px;
                background: linear-gradient(135deg, #d3d3d3, #a9a9a9);
                position: relative;
                padding: 50px;
                color: white;
            }}
            .svg-background {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: -1;
                opacity: 0.2;
            }}
            .container {{
                max-width: 600px;
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
                animation: fadeIn 1s ease-in-out;
                text-align: center;
            }}
            .header {{
                background: linear-gradient(135deg, #dc3545, #ff073a);
                color: white;
                padding: 20px;
                font-size: 22px;
                font-weight: bold;
                border-radius: 10px 10px 0 0;
            }}
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(-20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            .content {{
                padding: 20px;
                font-size: 16px;
                color: #333;
            }}
            .alert-box {{
                background: #ffeeba;
                color: #856404;
                padding: 15px;
                border-radius: 5px;
                font-weight: bold;
                text-align: center;
                margin-top: 10px;
                animation: pulse 1s infinite;
            }}
            @keyframes pulse {{
                0% {{ transform: scale(1); }}
                50% {{ transform: scale(1.05); }}
                100% {{ transform: scale(1); }}
            }}
            .cta-button {{
                display: block;
                width: 100%;
                text-align: center;
                background: linear-gradient(135deg, #28a745, #218838);
                color: white;  
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 15px;
                transition: all 0.3s ease-in-out;
            }}
            .cta-button:hover {{
                background: linear-gradient(135deg, #218838, #28a745);
                transform: scale(1.05);
            }}
            .footer {{
                text-align: center;
                font-size: 12px;
                color: #777;
                padding: 15px;
                margin-top: 20px;
                border-top: 1px solid #ddd;
            }}
            .footer a {{
                color: #007bff;
                text-decoration: none;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="email-wrapper">

            <div class="container">
                <div class="header">
                    <i class="fa-solid fa-triangle-exclamation"></i> Suspicious Activity Alert
                </div>
                <div class="content">
                    <p><strong>Attention!</strong></p>
                    <p>We've detected multiple suspicious requests from the following IP addresses:</p>

                    <div class="alert-box">
                        {formatted_body} 
                    </div>

                    <a href="http://127.0.0.1:5000/" class="cta-button">Click Here to block IPs</a>
                </div>

                <div class="footer">
                    <p>If you did not request this, please ignore this message.</p>
                    <p><a href="http://example.com/unsubscribe">Unsubscribe</a></p>
                </div>
            </div>

        </div>

    </body>
    </html>
    """

    # Attach HTML content
    message.attach(MIMEText(body_content, "html"))

    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, password)  # Log in to your email
            server.sendmail(sender_email, receiver_email, message.as_string())  # Send email
        logging.info("Email sent successfully!")
    except Exception as e:
        logging.error(f"Error sending email: {e}")
