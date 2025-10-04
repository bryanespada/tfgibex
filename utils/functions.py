# General libraries
from datetime import datetime, date
from django.conf import settings # import the settings file
from django.contrib.auth.models import Group

from datetime import datetime, timedelta

# Libraries to send mails
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib, ssl
import uuid
import requests
from django.shortcuts import get_object_or_404
from appmodels.models import GeneralConfig


# Function to save logs on real time
def write_in_log_file(message):
    with open("stderr.log", "a") as logfile:
        logfile.write(f"[{datetime.now()}] ---> {message}\n")


def sendmail(message_data):
    
    config = get_object_or_404(GeneralConfig, id=1)
    
    # Crear sesión SMTP
    s = smtplib.SMTP(config.smtp_server, config.smtp_port)

    # Iniciar TLS para seguridad
    context = ssl.create_default_context()
    s.starttls(context=context)

    # Autenticación
    s.login(config.smtp_email_account, config.smtp_password)

    # Crear el mensaje
    message = MIMEMultipart()
    message["From"] = config.smtp_email_account
    message["To"] = message_data['receivers']
    message["Subject"] = message_data['subject']

    # Cuerpo del mensaje
    body = message_data['message']
    message.attach(MIMEText(body, "plain"))

    # Enviar el mensaje
    s.send_message(message)

    # Terminar la sesión SMTP
    s.quit()



def is_admin(user):
    """
    Check if some user is in group "Administration".
    """
    try:
        administration_group = Group.objects.get(name="Administration")
        return administration_group in user.groups.all()
    except Group.DoesNotExist:
        return False


def get_client_geolocation(request):
    """
    Obtiene la dirección IP del cliente desde la solicitud.
    """
    # Intentar obtener la IP del cliente
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        ip = xff.split(',')[0].strip()  # Get first IP and remove spaces
    else:
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')

    # Valores por defecto
    default_data = {
        "ip": ip,
        "continent": "No-data",
        "country": "No-data",
        "region": "No-data",
        "city": "No-data",
        "postal": "No-data",
        "lat": "No-data",
        "lng": "No-data"
    }

    # Si es una IP local, devolver localhost como país
    if ip in ['127.0.0.1', 'localhost', '::1']:
        default_data['country'] = 'Localhost'
        default_data['city'] = 'Desarrollo'
        return default_data

    # Intentar obtener geolocalización
    try:
        response = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5)

        if response.status_code == 200:
            data = response.json()

            # Verificar si hay error en la respuesta
            if 'error' in data and data.get('error') == True:
                write_in_log_file(f"Error en geolocalización para IP {ip}: {data.get('reason', 'Unknown')}")
                return default_data

            return {
                "ip": ip,
                "continent": data.get('continent_code', 'No-data'),
                "country": data.get('country_name', 'No-data'),  # Usar country_name en vez de country
                "region": data.get('region', 'No-data'),
                "city": data.get('city', 'No-data'),
                "postal": data.get('postal', 'No-data'),
                "lat": str(data.get('latitude', 'No-data')),
                "lng": str(data.get('longitude', 'No-data'))
            }
        else:
            write_in_log_file(f"Error HTTP {response.status_code} al obtener geolocalización para IP {ip}")

    except requests.exceptions.Timeout:
        write_in_log_file(f"Timeout al obtener geolocalización para IP {ip}")
    except requests.exceptions.RequestException as e:
        write_in_log_file(f"Error al obtener geolocalización para IP {ip}: {str(e)}")
    except Exception as e:
        write_in_log_file(f"Error inesperado en geolocalización para IP {ip}: {str(e)}")

    return default_data


def get_dates_from_date(start_date):
    """
    Generate a list of dates from start_date to today
    """
    # In both cases it has to be set ona day before
    if isinstance(start_date, str): # Cast to datetime if it is a string
        start_date = (datetime.strptime(start_date, '%Y-%m-%d').date())  - timedelta(days=1)
    else:
        start_date = start_date - timedelta(days=1)

    today = datetime.now().date() # Set today
    date_list = [start_date + timedelta(days=i) for i in range((today - start_date).days + 1)] # Generate a list with dates between then and today

    return date_list

