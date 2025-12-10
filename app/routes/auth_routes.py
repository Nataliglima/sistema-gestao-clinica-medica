from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models import Usuario, Paciente, LogAcesso
from app.schemas import UsuarioCreate, UsuarioLogin, Token, UsuarioResponse
from app.auth import (
    gerar_hash_senha, 
    autenticar_usuario, 
    criar_token_acesso, 
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["Autenticação"])

@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """Registra um novo usuário no sistema"""
    
    # Verifica se email já existe
    db_usuario = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if db_usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Se for paciente, valida campos obrigatórios
    if usuario.tipo == "paciente":
        if not usuario.cpf:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF é obrigatório para pacientes"
            )
        if not usuario.telefone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Telefone é obrigatório para pacientes"
            )
        if not usuario.data_nascimento:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data de nascimento é obrigatória para pacientes"
            )
        
        # Verifica se CPF já existe
        db_paciente = db.query(Paciente).filter(Paciente.cpf == usuario.cpf).first()
        if db_paciente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado"
            )
    
    # Cria novo usuário
    novo_usuario = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=gerar_hash_senha(usuario.senha),
        tipo=usuario.tipo
    )
    
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    
    # Se for paciente, cria registro de paciente
    if usuario.tipo == "paciente":
        novo_paciente = Paciente(
            usuario_id=novo_usuario.id,
            cpf=usuario.cpf,
            telefone=usuario.telefone,
            data_nascimento=usuario.data_nascimento,
            endereco=usuario.endereco,
            historico_medico=usuario.historico_medico
        )
        db.add(novo_paciente)
        db.commit()
    
    # Registra log
    log = LogAcesso(
        usuario_id=novo_usuario.id,
        acao="REGISTRO",
        detalhes=f"Novo usuário registrado: {usuario.email}"
    )
    db.add(log)
    db.commit()
    
    return novo_usuario

@router.post("/login", response_model=Token)
def login(usuario: UsuarioLogin, db: Session = Depends(get_db)):
    """Realiza login e retorna token JWT"""
    
    # Autentica usuário
    db_usuario = autenticar_usuario(db, usuario.email, usuario.senha)
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Cria token de acesso
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = criar_token_acesso(
        data={"sub": db_usuario.email},  # ✅ Passando dicionário correto
        expires_delta=access_token_expires
    )
    
    # Registra log
    log = LogAcesso(
        usuario_id=db_usuario.id,
        acao="LOGIN",
        detalhes=f"Login realizado: {usuario.email}"
    )
    db.add(log)
    db.commit()
    
    # ✅ Retorna "token" para consistência com Token schema
    return {"token": access_token, "token_type": "bearer"}