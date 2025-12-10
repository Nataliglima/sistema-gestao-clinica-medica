from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import engine, get_db, Base
from app.routes import auth_routes, pacientes, consultas
from app.models import Usuario, LogAcesso

# Criar tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Criar aplicação FastAPI
app = FastAPI(
    title="HealthAPI - Sistema de Gestão de Clínica",
    description="API REST para gerenciamento de pacientes e consultas médicas",
    version="1.0.0"
)

# Configurar CORS (permite requisições de qualquer origem)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(auth_routes.router)
app.include_router(pacientes.router)
app.include_router(consultas.router)

# Rota raiz
@app.get("/")
def raiz():
    """Endpoint raiz da API"""
    return {
        "mensagem": "Bem-vindo à HealthAPI",
        "versao": "1.0.0",
        "documentacao": "/docs"
    }

# Rota de health check
@app.get("/health")
def health_check():
    """Verifica se a API está funcionando"""
    return {"status": "ok", "servico": "HealthAPI"}

# Rota para listar logs (LGPD)
@app.get("/logs")
def listar_logs(db: Session = Depends(get_db)):
    """Lista logs de acesso (apenas para fins de auditoria LGPD)"""
    logs = db.query(LogAcesso).order_by(LogAcesso.criado_em.desc()).limit(100).all()
    return {
        "total": len(logs),
        "logs": [
            {
                "id": log.id,
                "usuario_id": log.usuario_id,
                "acao": log.acao,
                "detalhes": log.detalhes,
                "criado_em": log.criado_em
            }
            for log in logs
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)