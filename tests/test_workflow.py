import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from parallel_subtask_agent_workflow import (
    LLMClient,
    AgentOrchestrator,
    TaskDecomposition,
    SubTask,
    OrchestratorError
)

@pytest.fixture
def mock_llm_client():
    client = MagicMock(spec=LLMClient)
    return client

@pytest.fixture
def agent_orchestrator(mock_llm_client):
    return AgentOrchestrator(mock_llm_client)

@pytest.mark.asyncio
async def test_orchestrator_run_success(agent_orchestrator, mock_llm_client):
    # Configurar mock para decomposição estruturada
    decomposition = TaskDecomposition(
        analysis="Teste de análise",
        tasks=[
            SubTask(type="plan", description="Descrição do plano"),
            SubTask(type="code/solve", description="Descrição da solução")
        ]
    )
    mock_llm_client.call_structured.return_value = decomposition.model_dump()

    # Configurar mock para chamadas assíncronas dos trabalhadores e síntese
    mock_llm_client.call_async.side_effect = [
        "Resposta do plano",
        "Resposta do código",
        "Resposta final sintetizada"
    ]

    result = await agent_orchestrator.run("Tarefa de teste")

    assert result == "Resposta final sintetizada"
    assert mock_llm_client.call_structured.called
    assert mock_llm_client.call_async.call_count == 3

@pytest.mark.asyncio
async def test_llm_client_initialization_failure():
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(OrchestratorError, match="TOGETHER_API_KEY não encontrada"):
            LLMClient(api_key=None)

def test_task_decomposition_validation():
    # Testar se o Pydantic valida corretamente dados incorretos
    with pytest.raises(Exception):
        TaskDecomposition(analysis="Teste", tasks=[{"type": "invalid", "description": "xxx"}])
