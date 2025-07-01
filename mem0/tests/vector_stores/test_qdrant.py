import unittest
import uuid
from unittest.mock import MagicMock, patch
import pytest

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointIdsList, PointStruct, VectorParams

from mem0.vector_stores.qdrant import Qdrant


class TestQdrant(unittest.TestCase):
    def setUp(self):
        self.client_mock = MagicMock(spec=QdrantClient)
        self.qdrant = Qdrant(
            collection_name="test_collection",
            embedding_model_dims=128,
            client=self.client_mock,
            path="test_path",
            on_disk=True,
        )

    def test_create_col(self):
        self.client_mock.get_collections.return_value = MagicMock(collections=[])

        self.qdrant.create_col(vector_size=128, on_disk=True)

        expected_config = VectorParams(size=128, distance=Distance.COSINE, on_disk=True)

        self.client_mock.create_collection.assert_called_with(
            collection_name="test_collection", vectors_config=expected_config
        )

    def test_insert(self):
        vectors = [[0.1, 0.2], [0.3, 0.4]]
        payloads = [{"key": "value1"}, {"key": "value2"}]
        ids = [str(uuid.uuid4()), str(uuid.uuid4())]

        self.qdrant.insert(vectors=vectors, payloads=payloads, ids=ids)

        self.client_mock.upsert.assert_called_once()
        points = self.client_mock.upsert.call_args[1]["points"]

        self.assertEqual(len(points), 2)
        for point in points:
            self.assertIsInstance(point, PointStruct)

        self.assertEqual(points[0].payload, payloads[0])

    def test_search(self):
        vectors = [[0.1, 0.2]]
        mock_point = MagicMock(id=str(uuid.uuid4()), score=0.95, payload={"key": "value"})
        self.client_mock.query_points.return_value = MagicMock(points=[mock_point])

        results = self.qdrant.search(query="", vectors=vectors, limit=1)

        self.client_mock.query_points.assert_called_once_with(
            collection_name="test_collection",
            query=vectors,
            query_filter=None,
            limit=1,
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].payload, {"key": "value"})
        self.assertEqual(results[0].score, 0.95)

    def test_delete(self):
        vector_id = str(uuid.uuid4())
        self.qdrant.delete(vector_id=vector_id)

        self.client_mock.delete.assert_called_once_with(
            collection_name="test_collection",
            points_selector=PointIdsList(points=[vector_id]),
        )

    def test_update(self):
        vector_id = str(uuid.uuid4())
        updated_vector = [0.2, 0.3]
        updated_payload = {"key": "updated_value"}

        self.qdrant.update(vector_id=vector_id, vector=updated_vector, payload=updated_payload)

        self.client_mock.upsert.assert_called_once()
        point = self.client_mock.upsert.call_args[1]["points"][0]
        self.assertEqual(point.id, vector_id)
        self.assertEqual(point.vector, updated_vector)
        self.assertEqual(point.payload, updated_payload)

    def test_get(self):
        vector_id = str(uuid.uuid4())
        self.client_mock.retrieve.return_value = [{"id": vector_id, "payload": {"key": "value"}}]

        result = self.qdrant.get(vector_id=vector_id)

        self.client_mock.retrieve.assert_called_once_with(
            collection_name="test_collection", ids=[vector_id], with_payload=True
        )
        self.assertEqual(result["id"], vector_id)
        self.assertEqual(result["payload"], {"key": "value"})

    def test_list_cols(self):
        self.client_mock.get_collections.return_value = MagicMock(collections=[{"name": "test_collection"}])
        result = self.qdrant.list_cols()
        self.assertEqual(result.collections[0]["name"], "test_collection")

    def test_delete_col(self):
        self.qdrant.delete_col()
        self.client_mock.delete_collection.assert_called_once_with(collection_name="test_collection")

    def test_col_info(self):
        self.qdrant.col_info()
        self.client_mock.get_collection.assert_called_once_with(collection_name="test_collection")

    def tearDown(self):
        del self.qdrant


@pytest.fixture
def qdrant_store():
    with patch('mem0.vector_stores.qdrant.qdrant_client') as mock_qdrant_client:
        store = Qdrant()
        store.client = mock_qdrant_client.QdrantClient.return_value
        store.collection_name = "test_collection"
        yield store


def test_search(qdrant_store):
    """Test the search method."""
    query_embedding = [0.1, 0.2, 0.3]
    limit = 5
    filters = {"user_id": "123"}
    
    # Mock the response from the qdrant client's search method
    mock_search_result = [MagicMock(payload={"text": "result1", "metadata": filters}, score=0.9)]
    qdrant_store.client.search.return_value = mock_search_result
    
    results = qdrant_store.search(embedding=query_embedding, limit=limit, filters=filters)
    
    qdrant_store.client.search.assert_called_once()
    _, kwargs = qdrant_store.client.search.call_args
    assert kwargs['collection_name'] == "test_collection"
    assert kwargs['query_vector'] == query_embedding
    assert kwargs['limit'] == limit
    
    assert len(results) == 1
    assert results[0]['text'] == "result1"
    assert results[0]['score'] == 0.9


def test_insert(qdrant_store):
    """Test the insert method."""
    points = [{"id": "1", "embedding": [0.4, 0.5, 0.6], "metadata": {"text": "point1"}}]
    
    qdrant_store.insert(points)
    
    qdrant_store.client.upsert.assert_called_once()
    _, kwargs = qdrant_store.client.upsert.call_args
    assert kwargs['collection_name'] == "test_collection"
    assert len(kwargs['points']) == 1


def test_delete(qdrant_store):
    """Test the delete method."""
    filters = {"user_id": "123"}
    
    qdrant_store.delete(filters=filters)
    
    qdrant_store.client.delete.assert_called_once()
    _, kwargs = qdrant_store.client.delete.call_args
    assert kwargs['collection_name'] == "test_collection"
    assert "must_be" in str(kwargs['points_selector'])


def test_get(qdrant_store):
    """Test the get method."""
    memory_id = "test_id"
    mock_retrieved_points = [MagicMock(payload={"text": "retrieved_point"})]
    qdrant_store.client.retrieve.return_value = mock_retrieved_points
    
    result = qdrant_store.get(id=memory_id)
    
    qdrant_store.client.retrieve.assert_called_once_with(
        collection_name="test_collection",
        ids=[memory_id],
        with_payload=True
    )
    assert result['text'] == 'retrieved_point'


def test_list(qdrant_store):
    """Test the list method."""
    filters = {"user_id": "123"}
    mock_scroll_result = ([MagicMock(payload={"text": "item1"})], "next_page_token")
    qdrant_store.client.scroll.return_value = mock_scroll_result

    results = qdrant_store.list(filters=filters)

    qdrant_store.client.scroll.assert_called_once()
    assert len(results) == 1
    assert results[0]['text'] == "item1"
