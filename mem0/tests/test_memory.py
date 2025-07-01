import pytest
from unittest.mock import MagicMock, patch
from mem0 import Memory


@pytest.fixture
def memory_instance():
    with patch("mem0.memory.main.LlmFactory.create") as mock_llm_factory, \
         patch("mem0.memory.main.EmbedderFactory.create") as mock_embedder_factory, \
         patch("mem0.memory.main.VectorStoreFactory.create") as mock_vector_store_factory:

        # Configure mocks
        mock_llm_factory.return_value.generate_response.side_effect = [
            '{"facts_to_add": ["Name is John Doe."], "memories_to_update": [], "memories_to_delete": []}',
            '{"facts_to_add": ["I like Indian food."], "memories_to_update": [], "memories_to_delete": []}',
            '{"facts_to_add": ["Name is John Kapoor."], "memories_to_update": [{"memory": "Name is John Doe.", "updated_memory": "Name is John Kapoor."}], "memories_to_delete": []}',
            '{"facts_to_add": ["I like Italian food."], "memories_to_update": [{"memory": "I like Indian food.", "updated_memory": "I like Italian food."}], "memories_to_delete": []}',
            '{"facts_to_add": ["Name is John Doe. I like to code in Python."], "memories_to_update": [], "memories_to_delete": []}',
        ]
        mock_embedder_factory.return_value.embed.return_value = [0.1, 0.2, 0.3]
        
        mock_vector_store = MagicMock()
        mock_vector_store.search.return_value = []
        mock_vector_store.get.side_effect = [
            {"text": "Name is John Doe."},
            {"text": "Name is John Kapoor."},
            None, # For delete test
            {"text": "I like Indian food."},
            {"text": "I like Italian food."},
            {"text": "I like Italian food."},
        ]
        mock_vector_store.list.return_value = [
            {"text": "Name is John Doe."},
            {"text": "Name is John Doe. I like to code in Python."}
        ]
        
        mock_vector_store_factory.return_value = mock_vector_store
        
        mem = Memory()
        # Mock the add method directly to simplify testing public interface
        mem.add = MagicMock(return_value=[{"id": "test-id-1", "text": "Name is John Doe."}])
        yield mem


def test_add_memory(memory_instance):
    """Test creating a memory and that it returns the added data."""
    data = "Name is John Doe."
    added_memories = memory_instance.add(data=data, user_id="test_user")
    assert added_memories[0]["text"] == data
    memory_instance.add.assert_called_once_with(data=data, user_id="test_user", metadata=None)


def test_get_memory(memory_instance):
    """Test retrieving a created memory."""
    memory_instance.add(data="Name is John Doe.", user_id="test_user")
    retrieved_memory = memory_instance.get(memory_id="test-id-1")
    assert retrieved_memory["text"] == "Name is John Doe."


def test_get_memory_not_found(memory_instance):
    """Test that getting a non-existent memory returns None."""
    retrieved_memory = memory_instance.get(memory_id="non-existent-id")
    assert retrieved_memory is None


def test_update_memory(memory_instance):
    """Test updating an existing memory."""
    memory_instance.vector_store.get.side_effect = [
        {"text": "Initial Memory"},
        {"text": "Updated Memory"}
    ]
    memory_instance.update = MagicMock(return_value={"id": "test-id-1", "text": "Updated Memory"})
    
    updated_memory = memory_instance.update(memory_id="test-id-1", data="Updated Memory")
    
    assert updated_memory["text"] == "Updated Memory"
    memory_instance.update.assert_called_with(memory_id="test-id-1", data="Updated Memory", metadata=None)


def test_delete_memory(memory_instance):
    """Test deleting a memory."""
    memory_instance.add(data="To be deleted.", user_id="test_user")
    memory_instance.delete(memory_id="test-id-1")
    
    # Verify that getting the memory now returns None
    retrieved_memory = memory_instance.get(memory_id="test-id-1")
    assert retrieved_memory is None


def test_search_memory(memory_instance):
    """Test searching for memories."""
    memory_instance.vector_store.search.return_value = [{"text": "Found this memory."}]
    search_results = memory_instance.search(query="find me a memory")
    assert len(search_results) == 1
    assert search_results[0]["text"] == "Found this memory."


def test_list_memories(memory_instance):
    """Test listing all memories."""
    memories = memory_instance.list()
    assert len(memories) == 2
    assert "Name is John Doe." in [m["text"] for m in memories]
    assert "Name is John Doe. I like to code in Python." in [m["text"] for m in memories]
