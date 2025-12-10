from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    tipo = Column(String(20), nullable=False)  # admin, medico, paciente
    criado_em = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    paciente = relationship("Paciente", back_populates="usuario", uselist=False)
    logs = relationship("LogAcesso", back_populates="usuario")

class Paciente(Base):
    __tablename__ = "pacientes"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True)
    cpf = Column(String(11), unique=True, index=True, nullable=False)
    telefone = Column(String(15))
    data_nascimento = Column(String(10))
    endereco = Column(String(255))
    historico_medico = Column(Text)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="paciente")
    consultas = relationship("Consulta", back_populates="paciente")

class Consulta(Base):
    __tablename__ = "consultas"
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    medico_nome = Column(String(100), nullable=False)
    data_hora = Column(DateTime, nullable=False)
    tipo = Column(String(20), default="presencial")  # presencial, online
    status = Column(String(20), default="agendada")  # agendada, realizada, cancelada
    observacoes = Column(Text)
    criado_em = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    paciente = relationship("Paciente", back_populates="consultas")

class LogAcesso(Base):
    __tablename__ = "logs_acesso"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    acao = Column(String(100), nullable=False)
    detalhes = Column(Text)
    ip_address = Column(String(45))
    criado_em = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="logs")