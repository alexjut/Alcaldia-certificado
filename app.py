from flask import Flask, request, send_file, render_template, redirect, url_for
from database import SessionLocal, Usuario, Radicado
import pdfkit
import pandas as pd
import os
import csv
from datetime import datetime
from io import StringIO
from flask import Response
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'alexjut1030'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'register'

def roles_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.role not in roles:
                return redirect(url_for('unauthorized'))
            return f(*args, **kwargs)
        return decorated_function
    return wrapper

@login_manager.user_loader
def load_user(user_id):
    session = SessionLocal()
    return session.query(Usuario).get(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cedula = request.form['cedula']
        password = request.form['password']
        session = SessionLocal()
        user = session.query(Usuario).filter_by(cedula=cedula).first()
        session.close()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        cedula = request.form['cedula']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']
        new_user = Usuario(nombre=nombre, cedula=cedula, password=password, role=role)
        session = SessionLocal()
        session.add(new_user)
        session.commit()
        session.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/admin')
@login_required

def admin_dashboard():
    return render_template('admin_dashboard.html')

# Configuración de pdfkit
path_wkhtmltopdf = '/usr/bin/wkhtmltopdf'
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

def generar_certificado(nombre, cedula, CPS, sitio_expedicion, objeto, obligaciones, vr_inicial_contrato, valor_mensual_honorarios, fecha_suscripcion, fecha_inicio, fecha_terminacion, tiempo_ejecucion_dia, radicado, año_contrato):
    print(f"Generando certificado para radicado: {radicado}")  # Mensaje de depuración
    
    rendered = render_template(
        'certificado_template.html',
        nombre=nombre,
        cedula=cedula,
        CPS=CPS,
        sitio_expedicion=sitio_expedicion,
        objeto=objeto,
        obligaciones=obligaciones,
        vr_inicial_contrato=vr_inicial_contrato,
        valor_mensual_honorarios=valor_mensual_honorarios,
        fecha_suscripcion=fecha_suscripcion,
        fecha_inicio=fecha_inicio,
        fecha_terminacion=fecha_terminacion,
        tiempo_ejecucion_dia=tiempo_ejecucion_dia,
        radicado=radicado,  # Asegúrate de pasar la variable radicado
        año_contrato=año_contrato
    )
    
    print(rendered)  # Imprimir el contenido renderizado para depuración
    
    nombre_archivo = f"certificado_{cedula}.pdf"
    options = {
        'enable-local-file-access': None,
        'page-size': 'Letter'
    }
    try:
        pdfkit.from_string(rendered, nombre_archivo, configuration=config, options=options)
        numerar_paginas(nombre_archivo)
    except IOError as e:
        print(f"Error al generar PDF: {e}")
    return nombre_archivo

def numerar_paginas(nombre_archivo):
    reader = PdfReader(nombre_archivo)
    writer = PdfWriter()
    for i in range(len(reader.pages)):
        page = reader.pages[i]
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.drawString(500, 10, f"Página {i + 1}")  # Posición del número de página
        can.save()
        packet.seek(0)
        new_pdf = PdfReader(packet)
        page.merge_page(new_pdf.pages[0])
        writer.add_page(page)
    with open(nombre_archivo, "wb") as output_pdf:
        writer.write(output_pdf)

@app.route("/certificado/<cedula>", methods=["GET"])
@login_required
def obtener_certificado(cedula):
    session = SessionLocal()
    usuario = session.query(Usuario).filter(Usuario.cedula == cedula).first()
    
    if usuario:
        print(f"Usuario encontrado: {usuario.nombre}, ID: {usuario.id}")
        
        # Usar el campo radicado directamente de la tabla usuarios
        radicado = usuario.radicado
        
        if radicado:
            print(f"Radicado encontrado: {radicado}")
            archivo_pdf = generar_certificado(
                usuario.nombre,
                usuario.cedula,
                usuario.CPS,
                usuario.sitio_expedicion,
                usuario.objeto,
                usuario.obligaciones,
                usuario.vr_inicial_contrato,
                usuario.valor_mensual_honorarios,
                usuario.fecha_suscripcion,
                usuario.fecha_inicio,
                usuario.fecha_terminacion,
                usuario.tiempo_ejecucion_dia,
                radicado,  # Pasar el número de radicado directamente
                usuario.año_contrato
            )
            print(f"Certificado generado: {archivo_pdf}")
            session.close()
            return send_file(archivo_pdf, as_attachment=True)
        else:
            print("Radicado no encontrado")
            session.close()
            return {"mensaje": "Radicado no encontrado"}, 404
    else:
        print("Usuario no encontrado")
        session.close()
        return {"mensaje": "Usuario no encontrado"}, 404

@app.route("/")
@login_required
def home():
    return render_template("home.html")

@app.route("/preview/<cedula>")
@login_required
def preview_certificado(cedula):
    session = SessionLocal()
    usuario = session.query(Usuario).filter(Usuario.cedula == cedula).first()
    session.close()
    
    if usuario:
        return render_template(
            'certificado_template.html',
            nombre=usuario.nombre,
            cedula=usuario.cedula,
            CPS=usuario.CPS,
            sitio_expedicion=usuario.sitio_expedicion,
            objeto=usuario.objeto,
            obligaciones=usuario.obligaciones,
            vr_inicial_contrato=usuario.vr_inicial_contrato,
            valor_mensual_honorarios=usuario.valor_mensual_honorarios,
            fecha_suscripcion=usuario.fecha_suscripcion,
            fecha_inicio=usuario.fecha_inicio,
            fecha_terminacion=usuario.fecha_terminacion,
            tiempo_ejecucion_dia=usuario.tiempo_ejecucion_dia,
            radicado="123456",  # Ejemplo de radicado
            año_contrato=usuario.año_contrato  # Añadir año del contrato
        )
    else:
        return {"mensaje": "Usuario no encontrado"}, 404


@app.route("/crear_datos", methods=["GET", "POST"])
@login_required
@roles_required('admin', 'creator')
def crear_datos():
    if request.method == "POST":
        nombre = request.form["nombre"]
        cedula = request.form["cedula"]
        CPS = request.form["CPS"]
        sitio_expedicion = request.form["sitio_expedicion"]
        objeto = request.form["objeto"]
        obligaciones = request.form["obligaciones"]
        vr_inicial_contrato = request.form["vr_inicial_contrato"]
        valor_mensual_honorarios = request.form["valor_mensual_honorarios"]
        fecha_suscripcion = datetime.strptime(request.form["fecha_suscripcion"], '%Y-%m-%d').date()
        fecha_inicio = datetime.strptime(request.form["fecha_inicio"], '%Y-%m-%d').date()
        fecha_terminacion = datetime.strptime(request.form["fecha_terminacion"], '%Y-%m-%d').date()
        tiempo_ejecucion_dia = request.form["tiempo_ejecucion_dia"]
        año_contrato = fecha_suscripcion.year  # Obtener el año del contrato
        
        session = SessionLocal()
        usuario_existente = session.query(Usuario).filter(Usuario.cedula == cedula).first()
        
        if usuario_existente:
            session.close()
            return {"mensaje": "La cédula ya está en uso. Por favor, usa una cédula diferente."}, 400
        
        nuevo_usuario = Usuario(
            nombre=nombre,
            cedula=cedula,
            CPS=CPS,
            sitio_expedicion=sitio_expedicion,
            objeto=objeto,
            obligaciones=obligaciones,
            vr_inicial_contrato=vr_inicial_contrato,
            valor_mensual_honorarios=valor_mensual_honorarios,
            fecha_suscripcion=fecha_suscripcion,
            fecha_inicio=fecha_inicio,
            fecha_terminacion=fecha_terminacion,
            tiempo_ejecucion_dia=tiempo_ejecucion_dia,
            año_contrato=año_contrato  # Añadir año del contrato
        )
        session.add(nuevo_usuario)
        session.commit()
        session.close()
        
        return redirect(url_for("buscar_certificado"))
    
    return render_template("crear_datos.html")

@app.route('/unauthorized')
def unauthorized():
    return "No tienes permiso para acceder a esta página.", 403

@app.route("/listar_cedulas", methods=["GET"])
@login_required
def listar_cedulas():
    session = SessionLocal()
    usuarios = session.query(Usuario).all()
    session.close()
    
    datos_usuarios = [{"cedula": usuario.cedula, "nombre": usuario.nombre, "CPS": usuario.CPS, "año_contrato": usuario.año_contrato} for usuario in usuarios]
    return render_template("listar_cedulas.html", datos_usuarios=datos_usuarios)


@app.route("/editar_datos/<cedula>", methods=["GET", "POST"])
@login_required
def editar_datos(cedula):
    session = SessionLocal()
    usuario = session.query(Usuario).filter(Usuario.cedula == cedula).first()
    
    if request.method == "POST":
        usuario.nombre = request.form["nombre"]
        usuario.CPS = request.form["CPS"]
        usuario.sitio_expedicion = request.form["sitio_expedicion"]
        usuario.objeto = request.form["objeto"]
        usuario.obligaciones = request.form["obligaciones"]
        usuario.vr_inicial_contrato = request.form["vr_inicial_contrato"]
        usuario.valor_mensual_honorarios = request.form["valor_mensual_honorarios"]
        usuario.fecha_suscripcion = datetime.strptime(request.form["fecha_suscripcion"], '%Y-%m-%d').date()
        usuario.fecha_inicio = datetime.strptime(request.form["fecha_inicio"], '%Y-%m-%d').date()
        usuario.fecha_terminacion = datetime.strptime(request.form["fecha_terminacion"], '%Y-%m-%d').date()
        usuario.tiempo_ejecucion_dia = request.form["tiempo_ejecucion_dia"]
        usuario.año_contrato = usuario.fecha_suscripcion.year  # Actualizar el año del contrato
        
        # Actualizar el radicado en la tabla usuarios si es necesario
        usuario.radicado = request.form["radicado"]
        
        # Actualizar el radicado en la tabla radicados
        radicado = session.query(Radicado).filter(Radicado.usuario_id == usuario.id).first()
        if radicado:
            radicado.numero = request.form["radicado"]
        
        session.commit()
        session.close()
        return redirect(url_for("buscar_certificado"))
    
    session.close()
    return render_template("editar_datos.html", usuario=usuario)

@app.route("/eliminar_datos/<cedula>", methods=["POST"])
@login_required
def eliminar_datos(cedula):
    session = SessionLocal()
    usuario = session.query(Usuario).filter(Usuario.cedula == cedula).first()
    
    if usuario:
        session.delete(usuario)
        session.commit()
    
    session.close()
    return redirect(url_for("buscar_certificado"))

@app.route("/buscar_certificado", methods=["GET", "POST"])
@login_required
def buscar_certificado():
    if request.method == "POST":
        cedula = request.form.get("cedula")
        año = request.form.get("año")
        session = SessionLocal()
        
        query = session.query(Usuario)
        if cedula:
            query = query.filter(Usuario.cedula == cedula)
        if año:
            query = query.filter(Usuario.año_contrato == año)
        
        usuario = query.first()
        session.close()
        
        if usuario:
            return render_template("resultado_busqueda.html", usuario=usuario)
        else:
            return render_template("resultado_busqueda.html", mensaje="Usuario no encontrado. Por favor, crea un nuevo usuario.")
    
    return render_template("buscar_cert.html")

# Crear la carpeta 'uploads' si no existe
if not os.path.exists('uploads'):
    os.makedirs('uploads')

def parse_date(date_str):
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y'):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"No se pudo convertir la fecha: {date_str}")

@app.route("/cargar_csv", methods=["GET", "POST"])
@login_required
@roles_required('admin', 'creator')
def cargar_csv():
    if request.method == "POST":
        if 'file' not in request.files:
            return {"mensaje": "No se ha subido ningún archivo"}, 400
        
        file = request.files['file']
        if file.filename == '':
            return {"mensaje": "No se ha seleccionado ningún archivo"}, 400
        
        if file and file.filename.endswith('.csv'):
            filename = secure_filename(file.filename)
            filepath = os.path.join('uploads', filename)
            file.save(filepath)
            
            # Procesar el archivo CSV
            data = pd.read_csv(filepath)
            session = SessionLocal()
            for index, row in data.iterrows():
                usuario_existente = session.query(Usuario).filter(Usuario.cedula == row['cedula']).first()
                if usuario_existente:
                    # Actualizar datos del usuario existente
                    usuario_existente.nombre = row['nombre']
                    usuario_existente.CPS = row['CPS']
                    usuario_existente.sitio_expedicion = row['sitio_expedicion']
                    usuario_existente.objeto = row['objeto']
                    usuario_existente.obligaciones = row['obligaciones']
                    usuario_existente.vr_inicial_contrato = row['vr_inicial_contrato']
                    usuario_existente.valor_mensual_honorarios = row['valor_mensual_honorarios']
                    usuario_existente.fecha_suscripcion = parse_date(row['fecha_suscripcion'])
                    usuario_existente.fecha_inicio = parse_date(row['fecha_inicio'])
                    usuario_existente.fecha_terminacion = parse_date(row['fecha_terminacion'])
                    usuario_existente.tiempo_ejecucion_dia = row['tiempo_ejecucion_dia']
                    usuario_existente.año_contrato = usuario_existente.fecha_suscripcion.year  # Actualizar año del contrato
                else:
                    # Crear nuevo usuario
                    nuevo_usuario = Usuario(
                        nombre=row['nombre'],
                        cedula=row['cedula'],
                        CPS=row['CPS'],
                        sitio_expedicion=row['sitio_expedicion'],
                        objeto=row['objeto'],
                        obligaciones=row['obligaciones'],
                        vr_inicial_contrato=row['vr_inicial_contrato'],
                        valor_mensual_honorarios=row['valor_mensual_honorarios'],
                        fecha_suscripcion=parse_date(row['fecha_suscripcion']),
                        fecha_inicio=parse_date(row['fecha_inicio']),
                        fecha_terminacion=parse_date(row['fecha_terminacion']),
                        tiempo_ejecucion_dia=row['tiempo_ejecucion_dia'],
                        año_contrato=parse_date(row['fecha_suscripcion']).year  # Añadir año del contrato
                    )
                    session.add(nuevo_usuario)
            session.commit()
            session.close()
            
            return redirect(url_for("listar_cedulas"))
        else:
            return {"mensaje": "El archivo debe ser un CSV"}, 400
    
    return render_template("cargar_csv.html")

@app.route("/descargar_csv", methods=["GET"])
@login_required
@roles_required('admin', 'viewer')
def descargar_csv():
    session = SessionLocal()
    usuarios = session.query(Usuario).all()
    session.close()
    # Crear el archivo CSV en memoria
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow([
        "nombre", "cedula", "CPS", "sitio_expedicion", "objeto", "obligaciones",
        "vr_inicial_contrato", "valor_mensual_honorarios", 
        "fecha_suscripcion", "fecha_inicio", "fecha_terminacion", 
        "tiempo_ejecucion_dia", "año_contrato"  # Añadir encabezado para año del contrato
    ])  # Encabezados del CSV
    for usuario in usuarios:
        writer.writerow([
            usuario.nombre, usuario.cedula, usuario.CPS, usuario.sitio_expedicion, 
            usuario.objeto, usuario.obligaciones, usuario.vr_inicial_contrato, usuario.valor_mensual_honorarios, 
            usuario.fecha_suscripcion, usuario.fecha_inicio, usuario.fecha_terminacion, 
            usuario.tiempo_ejecucion_dia, usuario.año_contrato  # Añadir año del contrato
        ])
    output = si.getvalue()
    si.close()
    # Enviar el archivo CSV como respuesta
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=usuarios.csv"}
    )

if __name__ == "__main__":
    app.run(debug=True)
