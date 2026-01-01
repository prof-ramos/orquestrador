# -*- coding: utf-8 -*-
"""Parallel_Subtask_Agent_Workflow.py

Traduzido e adaptado de:
https://colab.research.google.com/github/togethercomputer/together-cookbook/blob/main/Agents/Parallel_Subtask_Agent_Workflow.ipynb

# Fluxo de Trabalho de Agente Orquestrador de Subtarefas
Autor Original: [Zain Hasan](https://x.com/ZainHasan6)

## Introdução

Neste script, demonstraremos como você pode criar um fluxo de trabalho de agente que dividirá tarefas originais em várias subtarefas.
Essas subtarefas são então concluídas usando chamadas paralelas de LLM, e as respostas são fornecidas diretamente como saída ou sintetizadas em uma resposta única.

Esta estratégia é semelhante à execução paralela de LLMs proposta no artigo [Mixture of Agents](https://arxiv.org/abs/2406.04692);
no entanto, nesta configuração, temos um LLM orquestrador dedicado que divide uma tarefa em subtarefas menores.
Cada LLM trabalhador paralelo executa um aspecto diferente da tarefa principal - o prompt enviado para os LLMs trabalhadores pode ser diferente,
e os próprios LLMs também podem ser diferentes para cada subtarefa.

## Fluxo de Trabalho de Orquestrador de Subtarefas

Neste fluxo de trabalho paralelo, demonstramos como você pode criar um sistema de agentes que decompõe inteligentemente tarefas complexas em componentes menores e especializados.

O fluxo começa com um LLM orquestrador que analisa a tarefa principal e a divide estrategicamente em subtarefas distintas, que são então executadas simultaneamente por diferentes LLMs trabalhadores.

Diferente das abordagens tradicionais de LLMs paralelos, onde vários modelos trabalham na mesma tarefa, este sistema atribui a cada LLM trabalhador um aspecto único do problema geral, com prompts personalizados e potencialmente diferentes arquiteturas de modelos adequadas à sua subtarefa específica.

1. O LLM orquestrador analisa a tarefa principal e a divide em subtarefas distintas e paralelas.
2. Cada subtarefa é atribuída a um LLM trabalhador apropriado com prompts especializados.
3. Os resultados são apresentados individualmente ou sintetizados em uma resposta unificada.
"""

import json
import asyncio
import together
import os
from together import AsyncTogether, Together

from typing import Optional, List, Literal
from pydantic import Field, BaseModel, ValidationError

# Configure sua chave de API aqui ou use a variável de ambiente TOGETHER_API_KEY
TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY", "--Sua Chave de API Aqui--")

client = Together(api_key=TOGETHER_API_KEY)
async_client = AsyncTogether(api_key=TOGETHER_API_KEY)

# Função auxiliar simples para chamada de LLM
def run_llm(user_prompt: str, model: str, system_prompt: Optional[str] = None):
    """Executa o modelo de linguagem com o prompt de usuário e o prompt de sistema fornecidos."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    messages.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        max_tokens=4000,
    )

    return response.choices[0].message.content

# Função auxiliar simples para chamada de LLM em modo JSON
def JSON_llm(user_prompt: str, schema: BaseModel, system_prompt: Optional[str] = None):
    """Executa um modelo de linguagem com prompts de usuário e sistema, retornando um objeto JSON estruturado."""
    try:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": user_prompt})

        extract = client.chat.completions.create(
            messages=messages,
            model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
            response_format={
                "type": "json_object",
                "schema": schema.model_json_schema(),
            },
        )

        response = json.loads(extract.choices[0].message.content)
        return response

    except ValidationError as e:
        raise ValueError(f"Falha na validação do esquema: {str(e)}")

# Função para chamar os LLMs de referência em paralelo
async def run_llm_parallel(user_prompt: str, model: str, system_prompt: str = None):
    """Executa uma chamada paralela de LLM com um modelo de referência."""
    response = None
    for sleep_time in [1, 2, 4]:
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": user_prompt})

            response = await async_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
            )
            break
        except together.error.RateLimitError as e:
            print(f"Erro de limite de taxa: {e}. Tentando novamente em {sleep_time}s...")
            await asyncio.sleep(sleep_time)
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
            break

    if response:
        return response.choices[0].message.content
    return "Erro ao processar subtarefa."

# Prompts do Orquestrador e Trabalhador
ORCHESTRATOR_PROMPT = """
Analise esta tarefa e divida-a em 2-3 abordagens distintas:

Tarefa: {task}

Forneça uma Análise:
Explique seu entendimento da tarefa e quais variações seriam valiosas.
Concentre-se em como cada abordagem atende a diferentes aspectos da tarefa.

Junto com a análise, forneça 2-3 abordagens para lidar com a tarefa, cada uma com uma breve descrição:
Planning (Planejamento): Escreva um plano detalhado para executar a tarefa sem resolvê-la de fato.
Solving (Resolução): Escreva uma solução técnica para a tarefa fornecida.
Tests (Testes): Escreva um plano de teste potencial para uma solução da tarefa fornecida, não resolva a tarefa.

Retorne apenas a saída JSON.
"""

WORKER_PROMPT = """
Gere conteúdo baseado em:
Tarefa: {original_task}
Estilo: {task_type}
Diretrizes: {task_description}

Retorne apenas sua resposta:
[Seu conteúdo aqui, mantendo a tarefa especificada e abordando totalmente os requisitos.]
"""

SYNTHESIZER_PROMPT = """Dada a tarefa: {task} e as respostas abaixo, onde cada uma aborda diferentes aspectos da
tarefa, sintetize uma resposta final.

{worker_responses}
"""

class Task(BaseModel):
    type: Literal["plan", "code/solve", "test"]
    description: str

class TaskList(BaseModel):
    analysis: str
    tasks: List[Task] = Field(..., default_factory=list)

async def orchestrator_workflow(task: str, orchestrator_prompt: str, worker_prompt: str):
    """Usa um modelo orquestrador para dividir uma tarefa em subtarefas e depois usa modelos trabalhadores para gerar e retornar respostas."""

    # Usa o modelo orquestrador para dividir a tarefa em subtarefas
    orchestrator_response = JSON_llm(orchestrator_prompt.format(task=task), schema=TaskList)

    # Analisa a resposta do orquestrador
    analysis = orchestrator_response["analysis"]
    tasks = orchestrator_response["tasks"]

    print("\n=== SAÍDA DO ORQUESTRADOR ===")
    print(f"\nANÁLISE:\n{analysis}")
    print(f"\nTAREFAS:\n{json.dumps(tasks, indent=2, ensure_ascii=False)}")

    worker_model = ["Qwen/Qwen2.5-Coder-32B-Instruct"] * len(tasks)

    # Coleta respostas intermediárias dos modelos trabalhadores
    worker_responses = await asyncio.gather(*[
        run_llm_parallel(
            user_prompt=worker_prompt.format(
                original_task=task,
                task_type=task_info['type'],
                task_description=task_info['description']
            ),
            model=model
        )
        for task_info, model in zip(tasks, worker_model)
    ])

    return tasks, worker_responses

async def main():
    task = "Escreva um programa que imprima os próximos 20 anos bissextos."

    print(f"Iniciando tarefa: {task}")

    tasks, worker_resp = await orchestrator_workflow(task, orchestrator_prompt=ORCHESTRATOR_PROMPT, worker_prompt=WORKER_PROMPT)

    for task_info, response in zip(tasks, worker_resp):
        print(f"\n=== RESULTADO DO TRABALHADOR ({task_info['type']}) ===\n{response}\n")

    print("\n=== SINTETIZANDO RESPOSTA FINAL ===")

    concatenated_responses = " ".join([
        f"\n=== RESULTADO DO TRABALHADOR ({task_info['type']}) ===\n{response}\n"
        for task_info, response in zip(tasks, worker_resp)
    ])

    final_answer = run_llm(
        SYNTHESIZER_PROMPT.format(task=task, worker_responses=concatenated_responses),
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo"
    )

    print("\n=== RESPOSTA FINAL ===\n")
    print(final_answer)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Erro fatal: {e}")
