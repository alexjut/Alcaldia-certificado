from flask import Flask, request, send_file, render_template, redirect, url_for
from database import SessionLocal, Usuario
import pdfkit
import pandas as pd
import os
import csv
from datetime import datetime
from io import StringIO
from flask import Response
from werkzeug.utils import secure_filename

app = Flask(__name__)

def generar_certificado(nombre, cedula, CPS, sitio_expedicion, objeto, vr_inicial_contrato, valor_mensual_honorarios, fecha_suscripcion, fecha_inicio, fecha_terminacion, tiempo_ejecucion_dia):
    rendered = render_template(
        'certificado_template.html',
        nombre=nombre,
        cedula=cedula,
        CPS=CPS,
        sitio_expedicion=sitio_expedicion,
        objeto=objeto,
        vr_inicial_contrato=vr_inicial_contrato,
        valor_mensual_honorarios=valor_mensual_honorarios,
        fecha_suscripcion=fecha_suscripcion,
        fecha_inicio=fecha_inicio,
        fecha_terminacion=fecha_terminacion,
        tiempo_ejecucion_dia=tiempo_ejecucion_dia
    )
    nombre_archivo = f"certificado_{cedula}.pdf"
    pdfkit.from_string(rendered, nombre_archivo)
    return nombre_archivo

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/certificado/<cedula>", methods=["GET"])
def obtener_certificado(cedula):
    session = SessionLocal()
    usuario = session.query(Usuario).filter(Usuario.cedula == cedula).first()
    session.close()
    
    if usuario:
        archivo_pdf = generar_certificado(
            usuario.nombre,
            usuario.cedula,
            usuario.CPS,
            usuario.sitio_expedicion,
            usuario.objeto,
            usuario.vr_inicial_contrato,
            usuario.valor_mensual_honorarios,
            usuario.fecha_suscripcion,
            usuario.fecha_inicio,
            usuario.fecha_terminacion,
            usuario.tiempo_ejecucion_dia
        )
        return send_file(archivo_pdf, as_attachment=True)
    else:
        return {"mensaje": "Usuario no encontrado"}, 404


@app.route("/crear_datos", methods=["GET", "POST"])
def crear_datos():
    if request.method == "POST":
        nombre = request.form["nombre"]
        cedula = request.form["cedula"]
        CPS = request.form["CPS"]
        sitio_expedicion = request.form["sitio_expedicion"]
        objeto = request.form["objeto"]
        vr_inicial_contrato = request.form["vr_inicial_contrato"]
        valor_mensual_honorarios = request.form["valor_mensual_honorarios"]
        fecha_suscripcion = datetime.strptime(request.form["fecha_suscripcion"], '%Y-%m-%d').date()
        fecha_inicio = datetime.strptime(request.form["fecha_inicio"], '%Y-%m-%d').date()
        fecha_terminacion = datetime.strptime(request.form["fecha_terminacion"], '%Y-%m-%d').date()
        tiempo_ejecucion_dia = request.form["tiempo_ejecucion_dia"]
        
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
            vr_inicial_contrato=vr_inicial_contrato,
            valor_mensual_honorarios=valor_mensual_honorarios,
            fecha_suscripcion=fecha_suscripcion,
            fecha_inicio=fecha_inicio,
            fecha_terminacion=fecha_terminacion,
            tiempo_ejecucion_dia=tiempo_ejecucion_dia
        )
        session.add(nuevo_usuario)
        session.commit()
        session.close()
        
        return redirect(url_for("buscar_certificado"))
    
    return render_template("crear_datos.html")

@app.route("/listar_cedulas", methods=["GET"])
def listar_cedulas():
    session = SessionLocal()
    usuarios = session.query(Usuario).all()
    session.close()
    
    datos_usuarios = [{"cedula": usuario.cedula, "nombre": usuario.nombre, "CPS": usuario.CPS} for usuario in usuarios]
    return render_template("listar_cedulas.html", datos_usuarios=datos_usuarios)

#editar datos

@app.route("/editar_datos/<cedula>", methods=["GET", "POST"])
def editar_datos(cedula):
    session = SessionLocal()
    usuario = session.query(Usuario).filter(Usuario.cedula == cedula).first()
    
    if request.method == "POST":
        usuario.nombre = request.form["nombre"]
        usuario.CPS = request.form["CPS"]
        usuario.sitio_expedicion = request.form["sitio_expedicion"]
        usuario.objeto = request.form["objeto"]
        usuario.vr_inicial_contrato = request.form["vr_inicial_contrato"]
        usuario.valor_mensual_honorarios = request.form["valor_mensual_honorarios"]
        usuario.fecha_suscripcion = datetime.strptime(request.form["fecha_suscripcion"], '%Y-%m-%d').date()
        usuario.fecha_inicio = datetime.strptime(request.form["fecha_inicio"], '%Y-%m-%d').date()
        usuario.fecha_terminacion = datetime.strptime(request.form["fecha_terminacion"], '%Y-%m-%d').date()
        usuario.tiempo_ejecucion_dia = request.form["tiempo_ejecucion_dia"]
        
        session.commit()
        session.close()
        return redirect(url_for("buscar_certificado"))
    
    session.close()
    return render_template("editar_datos.html", usuario=usuario)



@app.route("/eliminar_datos/<cedula>", methods=["POST"])
def eliminar_datos(cedula):
    session = SessionLocal()
    usuario = session.query(Usuario).filter(Usuario.cedula == cedula).first()
    
    if usuario:
        session.delete(usuario)
        session.commit()
    
    session.close()
    return redirect(url_for("buscar_certificado"))

@app.route("/buscar_certificado", methods=["GET", "POST"])
def buscar_certificado():
    if request.method == "POST":
        cedula = request.form["cedula"]
        session = SessionLocal()
        usuario = session.query(Usuario).filter(Usuario.cedula == cedula).first()
        session.close()
        
        if usuario:
            return render_template("resultado_busqueda.html", usuario=usuario)
        else:
            return render_template("resultado_busqueda.html", mensaje="Usuario no encontrado. Por favor, crea un nuevo usuario.")
    
    return render_template("buscar_cert.html")


# Crear la carpeta 'uploads' si no existe
if not os.path.exists('uploads'):
    os.makedirs('uploads')
from datetime import datetime

from datetime import datetime

def parse_date(date_str):
    for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"No se pudo convertir la fecha: {date_str}")

@app.route("/cargar_csv", methods=["GET", "POST"])
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
                    usuario_existente.vr_inicial_contrato = row['vr_inicial_contrato']
                    usuario_existente.valor_mensual_honorarios = row['valor_mensual_honorarios']
                    usuario_existente.fecha_suscripcion = parse_date(row['fecha_suscripcion'])
                    usuario_existente.fecha_inicio = parse_date(row['fecha_inicio'])
                    usuario_existente.fecha_terminacion = parse_date(row['fecha_terminacion'])
                    usuario_existente.tiempo_ejecucion_dia = row['tiempo_ejecucion_dia']
                else:
                    # Crear nuevo usuario
                    nuevo_usuario = Usuario(
                        nombre=row['nombre'],
                        cedula=row['cedula'],
                        CPS=row['CPS'],
                        sitio_expedicion=row['sitio_expedicion'],
                        objeto=row['objeto'],
                        vr_inicial_contrato=row['vr_inicial_contrato'],
                        valor_mensual_honorarios=row['valor_mensual_honorarios'],
                        fecha_suscripcion=parse_date(row['fecha_suscripcion']),
                        fecha_inicio=parse_date(row['fecha_inicio']),
                        fecha_terminacion=parse_date(row['fecha_terminacion']),
                        tiempo_ejecucion_dia=row['tiempo_ejecucion_dia']
                    )
                    session.add(nuevo_usuario)
            session.commit()
            session.close()
            
            return redirect(url_for("listar_cedulas"))
        else:
            return {"mensaje": "El archivo debe ser un CSV"}, 400
    
    return render_template("cargar_csv.html")


@app.route("/descargar_csv", methods=["GET"])
def descargar_csv():
    session = SessionLocal()
    usuarios = session.query(Usuario).all()
    session.close()

    # Crear el archivo CSV en memoria
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow([
        "nombre", "cedula", "CPS", "sitio_expedicion", "objeto", 
        "vr_inicial_contrato", "valor_mensual_honorarios", 
        "fecha_suscripcion", "fecha_inicio", "fecha_terminacion", 
        "tiempo_ejecucion_dia"
    ])  # Encabezados del CSV
    for usuario in usuarios:
        writer.writerow([
            usuario.nombre, usuario.cedula, usuario.CPS, usuario.sitio_expedicion, 
            usuario.objeto, usuario.vr_inicial_contrato, usuario.valor_mensual_honorarios, 
            usuario.fecha_suscripcion, usuario.fecha_inicio, usuario.fecha_terminacion, 
            usuario.tiempo_ejecucion_dia
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
