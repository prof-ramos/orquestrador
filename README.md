<!-- markdownlint-disable MD033 MD041 -->

<a name="readme-top"></a>

<!-- PROJECT SHIELDS -->

[![Contributors][contributors-shield]][contributors-url] [![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url] [![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h3 align="center">Orquestrador de Agentes IA</h3>

  <p align="center">
    Um fluxo de trabalho assíncrono e resiliente para orquestração de subtarefas usando LLMs.
    <br />
    <a href="#como-usar"><strong>Explore a documentação »</strong></a>
    <br />
    <br />
    <a href="https://github.com/prof-ramos/orquestrador/issues">Reportar Bug</a>
    ·
    <a href="https://github.com/prof-ramos/orquestrador/issues">Solicitar Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Índice</summary>
  <ol>
    <li>
      <a href="#sobre-o-projeto">Sobre o Projeto</a>
      <ul>
        <li><a href="#construído-com">Construído Com</a></li>
      </ul>
    </li>
    <li>
      <a href="#começando">Começando</a>
      <ul>
        <li><a href="#pré-requisitos">Pré-requisitos</a></li>
        <li><a href="#instalação">Instalação</a></li>
      </ul>
    </li>
    <li><a href="#como-usar">Como Usar</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#testes">Testes</a></li>
    <li><a href="#licença">Licença</a></li>
    <li><a href="#contato">Contato</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## Sobre o Projeto

Este projeto implementa um **Orquestrador de Agentes** capaz de decompor tarefas complexas em
subtarefas menores, executá-las em paralelo utilizando Modelos de Linguagem (LLMs) e sintetizar os
resultados em uma resposta coesa.

O fluxo foi desenhado para ser resiliente, assíncrono e fácil de estender, utilizando as melhores
práticas de desenvolvimento Python moderno (`python-pro`).

### Construído Com

- [![Python][Python.org]][Python-url] - Core Language
- [![Together AI][Together.ai]][Together-url] - LLM Provider
- [![Pydantic][Pydantic.dev]][Pydantic-url] - Data Validation
- [![UV][Astral.sh]][Uv-url] - Package Management

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

<!-- GETTING STARTED -->

## Começando

Para rodar uma cópia local, siga os passos abaixo.

### Pré-requisitos

Este projeto utiliza o `uv` para gerenciamento de dependências e ambientes virtuais. Certifique-se
de tê-lo instalado:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Instalação

1. Clone o repositório

   ```sh
   git clone https://github.com/prof-ramos/orquestrador.git
   ```

2. Instale as dependências

   ```sh
   uv sync
   ```

3. Configure sua chave de API

   - Crie um arquivo `.env` na raiz do projeto:

     ```sh
     cp .env.example .env
     ```

   - Adicione sua chave da Together AI:

     ```env
     TOGETHER_API_KEY="sua-chave-aqui"
     ```

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

<!-- USAGE EXAMPLES -->

## Como Usar

Para executar o orquestrador com a tarefa padrão:

```sh
uv run parallel_subtask_agent_workflow.py
```

O sistema irá:

1. Analisar a tarefa complexa.
2. Gerar um plano de ação (Task Decomposition).
3. Executar subtarefas em paralelo.
4. Sintetizar a resposta final.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

## Testes

Para garantir a estabilidade do orquestrador, execute a suíte de testes unitários:

```sh
PYTHONPATH=. uv run pytest
```

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

<!-- ROADMAP -->

## Roadmap

- [x] Implementação da Arquitetura Base
- [x] Suporte a Execução Paralela
- [x] Validação com Pydantic
- [x] Migração para SDK v2.0
- [ ] Interface Web (Streamlit/FastAPI)
- [ ] Suporte a múltiplos provedores de LLM

Veja as [issues abertas](https://github.com/prof-ramos/orquestrador/issues) para uma lista completa
de funcionalidades propostas.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

<!-- LICENSE -->

## Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

<!-- CONTACT -->

## Contato

Gabriel Ramos - [@prof-ramos](https://github.com/prof-ramos)

Link do Projeto:
[https://github.com/prof-ramos/orquestrador](https://github.com/prof-ramos/orquestrador)

<p align="right">(<a href="#readme-top">voltar ao topo</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->

[contributors-shield]:
  https://img.shields.io/github/contributors/prof-ramos/orquestrador.svg?style=for-the-badge
[contributors-url]: https://github.com/prof-ramos/orquestrador/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/prof-ramos/orquestrador.svg?style=for-the-badge
[forks-url]: https://github.com/prof-ramos/orquestrador/network/members
[stars-shield]: https://img.shields.io/github/stars/prof-ramos/orquestrador.svg?style=for-the-badge
[stars-url]: https://github.com/prof-ramos/orquestrador/stargazers
[issues-shield]:
  https://img.shields.io/github/issues/prof-ramos/orquestrador.svg?style=for-the-badge
[issues-url]: https://github.com/prof-ramos/orquestrador/issues
[license-shield]:
  https://img.shields.io/github/license/prof-ramos/orquestrador.svg?style=for-the-badge
[license-url]: https://github.com/prof-ramos/orquestrador/blob/main/LICENSE
[Python.org]:
  https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://python.org
[Together.ai]:
  https://img.shields.io/badge/Together%20AI-000000?style=for-the-badge&logo=ai&logoColor=white
[Together-url]: https://together.ai
[Pydantic.dev]:
  https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white
[Pydantic-url]: https://docs.pydantic.dev/
[Astral.sh]: https://img.shields.io/badge/UV-Astral-purple?style=for-the-badge
[Uv-url]: https://astral.sh/uv
