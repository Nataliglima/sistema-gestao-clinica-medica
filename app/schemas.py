from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Schemas de Usuário
class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
    tipo: str  # admin, medico, paciente

class UsuarioCreate(UsuarioBase):
    senha: str
    # Campos opcionais para pacientes
    cpf: Optional[str] = None
    telefone: Optional[str] = None
    data_nascimento: Optional[str] = None
    endereco: Optional[str] = None
    historico_medico: Optional[str] = None

class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str

class UsuarioResponse(UsuarioBase):
    id: int
    criado_em: datetime
    
    class Config:
        from_attributes = True

# Schemas de Paciente
class PacienteBase(BaseModel):
    cpf: str
    telefone: Optional[str] = None
    data_nascimento: Optional[str] = None
    endereco: Optional[str] = None
    historico_medico: Optional[str] = None

class PacienteCreate(PacienteBase):
    pass

class PacienteUpdate(BaseModel):
    telefone: Optional[str] = None
    data_nascimento: Optional[str] = None
    endereco: Optional[str] = None
    historico_medico: Optional[str] = None

class PacienteResponse(PacienteBase):
    id: int
    usuario_id: int
    criado_em: datetime
    atualizado_em: datetime
    
    class Config:
        from_attributes = True

# Schemas de Consulta
class ConsultaBase(BaseModel):
    medico_nome: str
    data_hora: datetime
    tipo: str = "presencial"  # presencial, online
    observacoes: Optional[str] = None

class ConsultaCreate(ConsultaBase):
    paciente_id: int

class ConsultaUpdate(BaseModel):
    status: Optional[str] = None  # agendada, realizada, cancelada
    observacoes: Optional[str] = None

class ConsultaResponse(ConsultaBase):
    id: int
    paciente_id: int
    status: str
    criado_em: datetime
    
    class Config:
        from_attributes = True

# Schema de Token - CORRIGIDO para consistência
class Token(BaseModel):
    token: str  
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    id: Optional[int] = None
    tipo: Optional[str] = None