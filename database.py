from sqlalchemy import create_engine, Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
import uuid

# Asegúrate de reemplazar 'usuario' y 'localhost' con tus valores correctos
DATABASE_URL = "postgresql://alexjut:alexjut1030@localhost:5432/certificado"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String)
    cedula = Column(String, unique=True)
    CPS = Column(String)  # Mantener CPS en mayúsculas
    sitio_expedicion = Column(String)
    objeto = Column(String)
    obligaciones = Column(String)
    vr_inicial_contrato = Column(Integer)
    valor_mensual_honorarios = Column(Integer)
    fecha_suscripcion = Column(Date)
    fecha_inicio = Column(Date)
    fecha_terminacion = Column(Date)
    tiempo_ejecucion_dia = Column(Integer)
    año_contrato = Column(Integer)
    radicado = Column(String)  # Asegúrate de tener este campo
    radicados = relationship("Radicado", back_populates="usuario")  # Relación inversa

class Radicado(Base):
    __tablename__ = "radicados"
    id = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(String, unique=True)
    usuario_id = Column(String, ForeignKey('usuarios.id'))
    usuario = relationship("Usuario", back_populates="radicados")

# Crear todas las tablas
Base.metadata.create_all(bind=engine)

print("Tablas creadas exitosamente.")