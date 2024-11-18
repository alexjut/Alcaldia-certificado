import uuid
from sqlalchemy import create_engine, Column, String, Integer, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./test.db"  # Puedes cambiar esto a la URL de tu base de datos

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String)
    cedula = Column(String, unique=True)
    CPS = Column(String)
    sitio_expedicion = Column(String)
    objeto = Column(String)
    vr_inicial_contrato = Column(Integer)
    valor_mensual_honorarios = Column(Integer)
    fecha_suscripcion = Column(Date)
    fecha_inicio = Column(Date)
    fecha_terminacion = Column(Date)
    tiempo_ejecucion_dia = Column(Integer)
    obligaciones = Column(String)

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)