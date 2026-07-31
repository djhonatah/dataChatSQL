"""
API de Integração para n8n (FastAPI)
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
import os

# Ajusta path para importar o backend
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend import process_question

app = FastAPI(title="DataChat SQL API")

class ChatRequest(BaseModel):
    pergunta: str
    historico: str = ""

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    """
    Endpoint para integração com n8n.
    Recebe uma pergunta em linguagem natural e retorna o resultado da consulta SQL, 
    uma explicação e o próprio SQL gerado.
    """
    try:
        resultado = process_question(request.pergunta, request.historico)
        
        if resultado.get("erro"):
            raise HTTPException(status_code=400, detail=resultado["erro"])
            
        # Converte DataFrame em dicionário para serialização JSON
        df = resultado.get("resultado")
        dados = df.to_dict(orient="records") if (df is not None and not df.empty) else []
        
        return {
            "pergunta": request.pergunta,
            "sql": resultado.get("sql"),
            "explicacao": resultado.get("explicacao", ""),
            "dados": dados
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
