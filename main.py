# https://www.youtube.com/watch?v=g_j6ILT-X0k

# Borras las contrasenas del sistema windows 
# en esta ruta busca la cuenta poner la ruta
# en el explorador de archivos 
# Panel de control\Cuentas de usuario\Administrador de credenciales

# acceder al sitio para habilitar contrasena para apps
# https://myaccount.google.com/u/3/apppasswords

import os
import json
import keyring
import smtplib
import configparser
import tkinter as tk
from email import encoders
from PIL import Image, ImageTk
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from cryptography.fernet import Fernet
from keyring.errors import PasswordDeleteError
from email.mime.multipart import MIMEMultipart
from tkinter import ttk, filedialog, messagebox, simpledialog


# Función para generar una clave de cifrado
def generate_key():
    """Genera una clave de cifrado y la guarda en un archivo 'secret.key'."""
    key = Fernet.generate_key()
    with open('secret.key', 'wb') as key_file:
        key_file.write(key)

# Función para cargar la clave de cifrado
def load_key():
    """Carga la clave de cifrado desde el archivo 'secret.key'."""
    return open('secret.key', 'rb').read()

# Función para cifrar la contraseña
def encrypt_password(password):
    """Cifra la contraseña usando la clave de cifrado.

    Args:
        password (str): La contraseña en texto plano.

    Returns:
        bytes: La contraseña cifrada.
    """
    key = load_key()
    fernet = Fernet(key)
    return fernet.encrypt(password.encode())

# Función para desencriptar la contraseña
def decrypt_password(encrypted_password):
    """Desencripta la contraseña usando la clave de cifrado.

    Args:
        encrypted_password (bytes): La contraseña cifrada.

    Returns:
        str: La contraseña en texto plano.
    """
    key = load_key()
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_password).decode()

# Función para cargar configuraciones desde default.ini
def load_config():
    """Carga las configuraciones desde el archivo 'default.ini' y actualiza la interfaz."""
    config = configparser.ConfigParser()
    config.read('default.ini')
    if 'SETTINGS' in config:
        plantilla = config['SETTINGS'].get('plantilla', '')
        nombre_archivo.set(plantilla)
        json_path = config['SETTINGS'].get('json_path', 'name.json')
        json_data = load_json(json_path)
        update_ui_with_json(json_data)

# Función para guardar configuraciones en default.ini
def save_config():
    """Guarda las configuraciones actuales en el archivo 'default.ini'."""
    config = configparser.ConfigParser()
    config.read('default.ini')
    if 'SETTINGS' not in config:
        config['SETTINGS'] = {}
    
    if json_path.get():
        config['SETTINGS']['json_path'] = json_path.get()

    with open('default.ini', 'w') as configfile:
        config.write(configfile)

# Función para cargar datos del archivo JSON
def load_json(file_path):
    """Carga datos desde un archivo JSON.

    Args:
        file_path (str): Ruta del archivo JSON.

    Returns:
        dict: Datos cargados desde el archivo JSON.
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar el archivo JSON: {e}")
        return None

# Función para actualizar los combobox y listbox con los datos del JSON
def update_ui_with_json(data):
    """Actualiza los widgets de la interfaz con los datos del JSON.

    Args:
        data (dict): Datos del archivo JSON.
    """
    if data:
        remitentes_combobox['values'] = list(data['Remitente'][0].values())
        remitentes_combobox.current(0)

        asuntos_combobox['values'] = list(data['Asunto'][0].values())
        asuntos_combobox.current(0)

        correo_contenedor.delete(0, tk.END)

        for destinatario in data['Destinatario'][0].values():
            correo_contenedor.insert(tk.END, destinatario)

# Función para importar un nuevo archivo de configuración JSON
def import_new_config():
    """Importa un nuevo archivo de configuración JSON y actualiza la interfaz."""
    filepath = filedialog.askopenfilename(title="Seleccionar archivo de configuración", filetypes=(("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")))
    if filepath:
        json_path.set(filepath)
        new_data = load_json(filepath)
        if new_data:
            update_ui_with_json(new_data)
            save_config()

# Variable global para almacenar la ruta completa del archivo
full_file_path = ""

# Función para buscar archivo de plantilla
def search_file():
    """Abre un cuadro de diálogo para seleccionar un archivo de plantilla y guarda la ruta."""
    global full_file_path
    filepath = filedialog.askopenfilename(title="Seleccionar archivo de plantilla")
    if filepath:
        file = os.path.basename(filepath)
        nombre_archivo.set(file)
        full_file_path = filepath  # Guarda la ruta completa del archivo

# Función para enviar el correo
def SendEmail(sender_email, password, subject, recipients, body, attachment_path):
    """Envía un correo electrónico con los detalles proporcionados.

    Args:
        sender_email (str): Dirección de correo del remitente.
        password (str): Contraseña del remitente.
        subject (str): Asunto del correo.
        recipients (list): Lista de direcciones de correo de los destinatarios.
        body (str): Cuerpo del correo.
        attachment_path (str): Ruta del archivo adjunto.

    Returns:
        bool: True si el correo se envió con éxito, False en caso contrario.
    """
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    # Crear el mensaje
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = ", ".join(recipients)
    message['Subject'] = subject

    # Cuerpo del correo
    message.attach(MIMEText(body, 'plain'))

    if attachment_path:
        # Adjuntar un archivo
        attachment = open(attachment_path, 'rb')

        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        attachment.close()
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(attachment_path)}')
        message.attach(part)

    # Enviar el correo
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(message)
        messagebox.showinfo("Success", "Correo enviado con éxito")
        return True
    except Exception as e:
        messagebox.showerror("Error", "Contraseña Incorrecta")
        return False
    finally:
        server.quit()

# Función para manejar el evento de enviar correo desde la interfaz
def handle_send_mail():
    """Maneja el evento de enviar correo desde la interfaz gráfica."""
    sender_email = remitentes_combobox.get()
    subject = asuntos_combobox.get()
    recipients = list(correo_contenedor.get(0, tk.END))
    attachment_path = full_file_path  # Usa la ruta completa del archivo

    # Verificar si la contraseña está almacenada en keyring
    password = keyring.get_password("email_sender", sender_email)

    if password is None:
        password = simpledialog.askstring("Password", f"Introduce la contraseña para {sender_email}", show='*')

    if password:
        # Crear un cuerpo del mensaje personalizado basado en el remitente
        sender_name = sender_email.split('@')[0].capitalize()
        body = f'Atte: {sender_name}'

        if SendEmail(sender_email, password, subject, recipients, body, attachment_path):
            # Guardar la contraseña en keyring solo si el envío es exitoso
            keyring.set_password("email_sender", sender_email, password)
        else:
            # Eliminar la contraseña de keyring si es incorrecta
            try:
                keyring.delete_password("email_sender", sender_email)
            except PasswordDeleteError:
                pass  # Manejar el caso en que no exista la contraseña a eliminar

# Crear la ventana principal
root = tk.Tk()
root.title('Correo')
root.geometry('530x330')

# Crear el menú
menu = tk.Menu(root)
opciones_menu = tk.Menu(menu, tearoff=0)
opciones_menu.add_command(label="Importar Configuración", command=import_new_config)
opciones_menu.add_command(label="Salir", command=root.quit)
menu.add_cascade(label="Opciones", menu=opciones_menu)
root.config(menu=menu)

# Crear el frame para los botones
frame_botones = tk.Frame(root)

# Crear y colocar los widgets de la interfaz de usuario
tk.Label(root, text='Remitente', width=10).grid(row=0, column=0)
remitentes_combobox = ttk.Combobox(root, width=31)
remitentes_combobox.grid(row=0, column=1, pady=5)

tk.Label(root, text='Asunto', width=10).grid(row=1, column=0)
asuntos_combobox = ttk.Combobox(root, width=31)
asuntos_combobox.grid(row=1, column=1, pady=5)

tk.Label(root, text='Correos', width=10).grid(row=2, column=0)
correo_contenedor = tk.Listbox(root, height=7, width=33)
correo_contenedor.grid(row=2, column=1)

tk.Label(root, text="Archivo").grid(row=3, column=0)
nombre_archivo = tk.StringVar()
tk.Entry(root, width=33, textvariable=nombre_archivo).grid(row=3, column=1, pady=10)

boton1 = tk.Button(frame_botones, text="Upload File", width=10, command=search_file)
boton2 = tk.Button(frame_botones, text="Send Mail", width=10, command=handle_send_mail)

boton1.pack(pady=10, side=tk.LEFT, padx=5)
boton2.pack(pady=10, side=tk.LEFT, padx=5)
frame_botones.grid(row=8, column=1)

json_path = tk.StringVar()

# Cargar la imagen
image_path = "GTO.png"
img = Image.open(image_path)
img = img.resize((200, 240))
img = ImageTk.PhotoImage(img)

# Crear y colocar el widget de la imagen
image_label = tk.Label(root, image=img)
image_label.grid(row=0, column=2, rowspan=4, padx=10, pady=10)

# Generar la clave si no existe
if not os.path.exists('secret.key'):
    generate_key()

# Cargar la configuración inicial
load_config()

# Iniciar el loop principal de la interfaz
root.mainloop()
