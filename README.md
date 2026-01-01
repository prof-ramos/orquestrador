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

Você deve configurar sua chave de API da Together AI. Você pode fazer isso de duas formas:

### 1. Usando um arquivo .env (Recomendado)

Crie um arquivo chamado `.env` na raiz do projeto e adicione sua chave:

```env
TOGETHER_API_KEY='sua_chave_aqui'
```

### 2. Usando variável de ambiente direta

```bash
export TOGETHER_API_KEY='sua_chave_aqui'
```

## Como Executar

Para iniciar o script utilizando o ambiente gerenciado pelo `uv`, execute:

```bash
uv run parallel_subtask_agent_workflow.py
```

## Testes Automatizados

Este projeto inclui uma suíte de testes unitários para garantir a resiliência do fluxo. Para rodar
os testes:

```bash
PYTHONPATH=. uv run pytest
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
