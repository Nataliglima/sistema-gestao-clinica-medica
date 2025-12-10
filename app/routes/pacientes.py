from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Paciente, Usuario, LogAcesso
from app.schemas import PacienteResponse, PacienteUpdate
from app.auth import obter_usuario_atual

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])

@router.get("/", response_model=List[PacienteResponse])
def listar_pacientes(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Lista todos os pacientes (apenas admin e médicos)"""
    
    if usuario_atual.tipo not in ["admin", "medico"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    pacientes = db.query(Paciente).all()
    
    # Registra log
    log = LogAcesso(
        usuario_id=usuario_atual.id,
        acao="LISTAR_PACIENTES",
        detalhes=f"Listagem de {len(pacientes)} pacientes"
    )
    db.add(log)
    db.commit()
    
    return pacientes

@router.get("/me", response_model=PacienteResponse)
def obter_meu_perfil(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obtém perfil do paciente logado"""
    
    if usuario_atual.tipo != "paciente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas pacientes podem acessar este endpoint"
        )
    
    paciente = db.query(Paciente).filter(Paciente.usuario_id == usuario_atual.id).first()
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de paciente não encontrado"
        )
    
    return paciente

@router.get("/{paciente_id}", response_model=PacienteResponse)
def obter_paciente(
    paciente_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obtém dados de um paciente específico"""
    
    # Verifica permissões
    if usuario_atual.tipo == "paciente":
        paciente_usuario = db.query(Paciente).filter(Paciente.usuario_id == usuario_atual.id).first()
        if not paciente_usuario or paciente_usuario.id != paciente_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode acessar seus próprios dados"
            )
    
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    
    # Registra log (LGPD)
    log = LogAcesso(
        usuario_id=usuario_atual.id,
        acao="ACESSAR_DADOS_PACIENTE",
        detalhes=f"Acesso aos dados do paciente ID: {paciente_id}"
    )
    db.add(log)
    db.commit()
    
    return paciente

@router.put("/{paciente_id}", response_model=PacienteResponse)
def atualizar_paciente(
    paciente_id: int,
    paciente_update: PacienteUpdate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Atualiza dados de um paciente"""
    
    # Verifica permissões
    if usuario_atual.tipo == "paciente":
        paciente_usuario = db.query(Paciente).filter(Paciente.usuario_id == usuario_atual.id).first()
        if not paciente_usuario or paciente_usuario.id != paciente_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode editar seus próprios dados"
            )
    
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    
    # Atualiza campos
    update_data = paciente_update.model_dump(exclude_unset=True)
    for campo, valor in update_data.items():
        setattr(paciente, campo, valor)
    
    db.commit()
    db.refresh(paciente)
    
    # Registra log
    log = LogAcesso(
        usuario_id=usuario_atual.id,
        acao="ATUALIZAR_PACIENTE",
        detalhes=f"Dados do paciente ID {paciente_id} foram atualizados"
    )
    db.add(log)
    db.commit()
    
    return paciente

@router.delete("/{paciente_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_paciente(
    paciente_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Deleta um paciente (LGPD - direito ao esquecimento)"""
    
    if usuario_atual.tipo not in ["admin", "paciente"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    
    # Se for paciente, só pode deletar seus próprios dados
    if usuario_atual.tipo == "paciente":
        if paciente.usuario_id != usuario_atual.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode deletar seus próprios dados"
            )
    
    # Registra log antes de deletar
    log = LogAcesso(
        usuario_id=usuario_atual.id,
        acao="DELETAR_PACIENTE",
        detalhes=f"Paciente ID {paciente_id} foi deletado (LGPD)"
    )
    db.add(log)
    
    # Deleta paciente e usuário associado
    usuario = db.query(Usuario).filter(Usuario.id == paciente.usuario_id).first()
    db.delete(paciente)
    if usuario:
        db.delete(usuario)
    
    db.commit()
    
    return None