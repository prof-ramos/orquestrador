# Fluxo de Trabalho de Agente Orquestrador de Subtarefas

Este projeto demonstra um padrão de orquestração onde um LLM (Orquestrador) divide uma tarefa
complexa em subtarefas menores, que são executadas em paralelo por outros LLMs (Trabalhadores), e os
resultados são finalmente sintetizados.

## Pré-requisitos

- Python 3.10 ou superior
- Uma chave de API da [Together AI](https://www.together.ai/)

## Instalação e Execução com uv

Este projeto utiliza o [uv](https://github.com/astral-sh/uv) para gerenciamento de dependências e
ambiente virtual.

1. Se você ainda não tem o `uv`, instale-o seguindo as
   [instruções oficiais](https://github.com/astral-sh/uv).

2. Sincronize as dependências:

```bash
uv sync
```

## Configuração

Você deve configurar sua chave de API da Together AI como uma variável de ambiente:

```bash
export TOGETHER_API_KEY='sua_chave_aqui'
```

## Como Executar

Para iniciar o script utilizando o ambiente gerenciado pelo `uv`, execute:

```bash
uv run parallel_subtask_agent_workflow.py
```

O script realizará as seguintes etapas:

1. **Orquestração**: Analisará a tarefa principal e criará um plano com 2-3 subtarefas
   (Planejamento, Resolução e Testes).
2. **Execução Paralela**: Enviará as subtarefas para modelos trabalhadores em paralelo.
3. **Síntese**: Combinará todos os resultados em uma resposta final coerente.

## Exemplo de Tarefa

Por padrão, o script está configurado para resolver a tarefa:

> "Escreva um programa que imprima os próximos 20 anos bissextos."

Você pode modificar a tarefa no final do arquivo `parallel_subtask_agent_workflow.py`, dentro da
função `main()`.
