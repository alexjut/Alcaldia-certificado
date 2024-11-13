from flask import Flask, request, send_file, render_template, redirect, url_for
from database import SessionLocal, Usuario
import pdfkit
import pandas as pd
import os
import csv
from io import StringIO
from flask import Response
from werkzeug.utils import secure_filename

app = Flask(__name__)

def generar_certificado(nombre, cedula, info_adicional):
    rendered = render_template('certificado_template.html', nombre=nombre, cedula=cedula, info_adicional=info_adicional)
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
        archivo_pdf = generar_certificado(usuario.nombre, usuario.cedula, usuario.info_adicional)
        return send_file(archivo_pdf, as_attachment=True)
    else:
        return {"mensaje": "Usuario no encontrado"}, 404

@app.route("/crear_datos", methods=["GET", "POST"])
def crear_datos():
    if request.method == "POST":
        nombre = request.form["nombre"]
        cedula = request.form["cedula"]
        info_adicional = request.form["info_adicional"]
        
        session = SessionLocal()
        usuario_existente = session.query(Usuario).filter(Usuario.cedula == cedula).first()
        
        if usuario_existente:
            session.close()
            return {"mensaje": "La cédula ya está en uso. Por favor, usa una cédula diferente."}, 400
        
        nuevo_usuario = Usuario(nombre=nombre, cedula=cedula, info_adicional=info_adicional)
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
    
    cedulas = [usuario.cedula for usuario in usuarios]
    return render_template("listar_cedulas.html", cedulas=cedulas)


@app.route("/editar_datos/<cedula>", methods=["GET", "POST"])
def editar_datos(cedula):
    session = SessionLocal()
    usuario = session.query(Usuario).filter(Usuario.cedula == cedula).first()
    
    if request.method == "POST":
        usuario.nombre = request.form["nombre"]
        usuario.info_adicional = request.form["info_adicional"]
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
#  ruta para cargar y procesar archivos CSV
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
                if not usuario_existente:
                    nuevo_usuario = Usuario(
                        nombre=row['nombre'],
                        cedula=row['cedula'],
                        info_adicional=row['info_adicional']
                    )
                    session.add(nuevo_usuario)
            session.commit()
            session.close()
            
            return redirect(url_for("listar_cedulas"))
        else:
            return {"mensaje": "El archivo debe ser un CSV"}, 400
    
    return render_template("cargar_csv.html")

# Descargar cvs
@app.route("/descargar_csv", methods=["GET"])
def descargar_csv():
    session = SessionLocal()
    usuarios = session.query(Usuario).all()
    session.close()

    # Crear el archivo CSV en memoria
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["nombre", "cedula", "info_adicional"])  # Encabezados del CSV
    for usuario in usuarios:
        writer.writerow([usuario.nombre, usuario.cedula, usuario.info_adicional])

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
