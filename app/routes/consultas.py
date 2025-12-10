from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Consulta, Paciente, Usuario, LogAcesso
from app.schemas import ConsultaCreate, ConsultaUpdate, ConsultaResponse
from app.auth import obter_usuario_atual

router = APIRouter(prefix="/consultas", tags=["Consultas"])

@router.post("/", response_model=ConsultaResponse, status_code=status.HTTP_201_CREATED)
def criar_consulta(
    consulta: ConsultaCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Cria uma nova consulta (admin ou médico)"""
    
    if usuario_atual.tipo not in ["admin", "medico"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas admins e médicos podem agendar consultas"
        )
    
    # Verifica se paciente existe
    paciente = db.query(Paciente).filter(Paciente.id == consulta.paciente_id).first()
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    
    nova_consulta = Consulta(**consulta.model_dump())
    db.add(nova_consulta)
    db.commit()
    db.refresh(nova_consulta)
    
    # Registra log
    log = LogAcesso(
        usuario_id=usuario_atual.id,
        acao="CRIAR_CONSULTA",
        detalhes=f"Nova consulta criada - ID: {nova_consulta.id}"
    )
    db.add(log)
    db.commit()
    
    return nova_consulta

@router.get("/", response_model=List[ConsultaResponse])
def listar_consultas(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Lista todas as consultas"""
    
    if usuario_atual.tipo in ["admin", "medico"]:
        # Admin e médicos veem todas
        consultas = db.query(Consulta).all()
    elif usuario_atual.tipo == "paciente":
        # Pacientes veem apenas suas consultas
        paciente = db.query(Paciente).filter(Paciente.usuario_id == usuario_atual.id).first()
        if not paciente:
            return []
        consultas = db.query(Consulta).filter(Consulta.paciente_id == paciente.id).all()
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    return consultas

@router.get("/{consulta_id}", response_model=ConsultaResponse)
def obter_consulta(
    consulta_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Obtém detalhes de uma consulta específica"""
    
    consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
    if not consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consulta não encontrada"
        )
    
    # Verifica permissões
    if usuario_atual.tipo == "paciente":
        paciente = db.query(Paciente).filter(Paciente.usuario_id == usuario_atual.id).first()
        if not paciente or consulta.paciente_id != paciente.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode acessar suas próprias consultas"
            )
    
    return consulta

@router.put("/{consulta_id}", response_model=ConsultaResponse)
def atualizar_consulta(
    consulta_id: int,
    consulta_update: ConsultaUpdate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Atualiza status de uma consulta"""
    
    if usuario_atual.tipo not in ["admin", "medico"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas admins e médicos podem atualizar consultas"
        )
    
    consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
    if not consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consulta não encontrada"
        )
    
    # Atualiza campos
    update_data = consulta_update.model_dump(exclude_unset=True)
    for campo, valor in update_data.items():
        setattr(consulta, campo, valor)
    
    db.commit()
    db.refresh(consulta)
    
    # Registra log
    log = LogAcesso(
        usuario_id=usuario_atual.id,
        acao="ATUALIZAR_CONSULTA",
        detalhes=f"Consulta ID {consulta_id} atualizada"
    )
    db.add(log)
    db.commit()
    
    return consulta

@router.delete("/{consulta_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_consulta(
    consulta_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    """Deleta uma consulta"""
    
    if usuario_atual.tipo not in ["admin", "medico"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas admins e médicos podem deletar consultas"
        )
    
    consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
    if not consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consulta não encontrada"
        )
    
    # Registra log
    log = LogAcesso(
        usuario_id=usuario_atual.id,
        acao="DELETAR_CONSULTA",
        detalhes=f"Consulta ID {consulta_id} foi deletada"
    )
    db.add(log)
    
    db.delete(consulta)
    db.commit()
    
    return None