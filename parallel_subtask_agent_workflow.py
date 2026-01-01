# -*- coding: utf-8 -*-
"""
Parallel Subtask Agent Workflow (Refatoração Profissional)

Este módulo implementa um sistema de orquestração de agentes onde uma tarefa complexa
é decomposta em subtarefas paralelas e depois sintetizada.
"""

import json
import asyncio
import os
import functools
import logging
from typing import Optional, List, Literal, Dict, Any, Callable, TypeVar, Awaitable
from datetime import datetime

import together
from together import AsyncTogether, Together
from pydantic import Field, BaseModel, ValidationError
from dotenv import load_dotenv

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Orchestrator")

# Carregar variáveis de ambiente
load_dotenv()

# Tipos genéricos para o decorador de retry
T = TypeVar("T")

# --- Exceções Customizadas ---

class OrchestratorError(Exception):
    """Exceção base para erros no fluxo do orquestrador."""
    pass

class LLMCallError(OrchestratorError):
    """Erro ao realizar chamadas para o modelo de linguagem."""
    pass

class ValidationError(OrchestratorError):
    """Erro na validação de dados ou esquemas JSON."""
    pass

# --- Decoradores ---

def retry_on_rate_limit(max_retries: int = 3, base_delay: float = 1.0):
    """
    Decorador para realizar retentativas em caso de erro de limite de taxa (Rate Limit).

    Args:
        max_retries: Número máximo de tentativas.
        base_delay: Atraso base exponencial entre tentativas.
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except together.error.RateLimitError as e:
                    last_exception = e
                    delay = base_delay * (2 ** attempt)
                    logger.warning(
                        f"Limite de taxa atingido. Tentativa {attempt + 1}/{max_retries}. "
                        f"Aguardando {delay}s..."
                    )
                    await asyncio.sleep(delay)
                except Exception as e:
                    logger.error(f"Erro inesperado na chamada LLM: {e}")
                    raise LLMCallError(f"Falha na chamada LLM: {e}") from e

            raise LLMCallError(f"Máximo de retentativas atingido: {last_exception}")
        return wrapper
    return decorator

# --- Modelos de Dados ---

class SubTask(BaseModel):
    """Representa uma subtarefa individual gerada pelo orquestrador."""
    type: Literal["plan", "code/solve", "test"]
    description: str

class TaskDecomposition(BaseModel):
    """Esquema para a análise inicial e lista de tarefas do orquestrador."""
    analysis: str
    tasks: List[SubTask] = Field(..., default_factory=list)

# --- Classes de Negócio ---

class LLMClient:
    """Cliente wrapper para interações com a API Together AI."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("TOGETHER_API_KEY")
        if not self.api_key:
            raise OrchestratorError("TOGETHER_API_KEY não encontrada no sistema.")

        self.client = Together(api_key=self.api_key)
        self.async_client = AsyncTogether(api_key=self.api_key)

    @retry_on_rate_limit(max_retries=3)
    async def call_async(
        self,
        prompt: str,
        model: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000
    ) -> str:
        """Realiza uma chamada assíncrona ao LLM."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.async_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    def call_structured(
        self,
        prompt: str,
        schema: BaseModel,
        model: str = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
    ) -> Dict[str, Any]:
        """Realiza uma chamada síncrona que retorna dados estruturados via JSON mode."""
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model,
                response_format={
                    "type": "json_object",
                    "schema": schema.model_json_schema(),
                },
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            raise ValidationError(f"Falha ao obter resposta estruturada: {e}") from e

class AgentOrchestrator:
    """Orquestrador principal do fluxo de trabalho."""

    ORCHESTRATOR_PROMPT = """
    Analise esta tarefa e divida-a em 2-3 abordagens distintas:
    Tarefa: {task}

    Forneça uma Análise detalhada e 2-3 tipos de tarefas JSON:
    - 'plan': Plano detalhado sem resolver.
    - 'code/solve': Solução técnica.
    - 'test': Plano de testes.
    """

    WORKER_PROMPT = """
    Gere conteúdo baseado em:
    Tarefa Original: {original_task}
    Tipo de Subtarefa: {task_type}
    Diretrizes: {task_description}
    """

    SYNTHESIZER_PROMPT = """
    Dada a tarefa: {task}
    E os seguintes resultados parciais:
    {worker_responses}

    Sintetize uma resposta final completa e coerente.
    """

    def __init__(self, client: LLMClient):
        self.client = client

    async def run(self, original_task: str) -> str:
        """Executa o workflow completo do orquestrador."""
        logger.info(f"Iniciando workflow para: {original_task}")

        # 1. Decomposição (Orquestração)
        decomposition_data = self.client.call_structured(
            self.ORCHESTRATOR_PROMPT.format(task=original_task),
            schema=TaskDecomposition
        )
        decomposition = TaskDecomposition(**decomposition_data)

        logger.info("Tarefa decomposta com sucesso.")
        print(f"\n[ANÁLISE]: {decomposition.analysis}")

        # 2. Execução Paralela (Trabalhadores)
        worker_model = "Qwen/Qwen2.5-Coder-32B-Instruct"
        tasks = []
        for t in decomposition.tasks:
            prompt = self.WORKER_PROMPT.format(
                original_task=original_task,
                task_type=t.type,
                task_description=t.description
            )
            tasks.append(self.client.call_async(prompt, worker_model))

        worker_results = await asyncio.gather(*tasks)

        # 3. Síntese Final
        logger.info("Sintetizando resultados dos trabalhadores...")

        formatted_results = "\n".join([
            f"--- RESULTADO ({t.type}) ---\n{res}"
            for t, res in zip(decomposition.tasks, worker_results)
        ])

        final_answer = await self.client.call_async(
            self.SYNTHESIZER_PROMPT.format(
                task=original_task,
                worker_responses=formatted_results
            ),
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
            max_tokens=4000
        )

        return final_answer

async def main():
    try:
        client = LLMClient()
        orchestrator = AgentOrchestrator(client)

        task = "Escreva um programa que imprima os próximos 20 anos bissextos."
        result = await orchestrator.run(task)

        print("\n=== RESPOSTA FINAL ===\n")
        print(result)

    except OrchestratorError as e:
        logger.error(f"Erro no fluxo: {e}")
    except Exception as e:
        logger.critical(f"Erro inesperado: {e}")

if __name__ == "__main__":
    asyncio.run(main())
