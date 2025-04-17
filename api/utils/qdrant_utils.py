import os
from uuid import uuid4
from services.logger import logger
from qdrant_client import AsyncQdrantClient
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from qdrant_client.http.models import (
    VectorParams,
    Distance,
    Filter,
    FieldCondition,
    MatchValue,
)

QDRANT_ENDPOINT = os.getenv("QDRANT_ENDPOINT_URL")

class DocumentIndexer:
    def __init__(self, qdrant_endpoint: str):
        self.qdrant_endpoint = qdrant_endpoint
        self.client = AsyncQdrantClient(self.qdrant_endpoint)
        self.vectors = None
        self.embedding_function = OpenAIEmbeddings(model="text-embedding-3-large")
        self.collection_name = "rag_bot"

    async def index_into_qdrant(self, extracted_text, file_name, doc_type, chunk_size):
        try:
            # Create a document object
            doc = Document(
                page_content=extracted_text,
                metadata={"file_name": file_name, "doc_type": doc_type},
            )

            # Use default chunk size if not provided
            if chunk_size is None:
                text_length = len(extracted_text)
                if text_length < 10000:
                    chunk_size = 800
                elif text_length < 50000:
                    chunk_size = 1500
                else:
                    chunk_size = 2000
                logger.info(f"Using dynamic chunk size: {chunk_size}")

            # Split the document into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                separator=["\n\n", "\n", ",", " "],
                chunk_size=chunk_size,
                chunk_overlap=200,
            )
            chunks = text_splitter.split_documents([doc])

            # Ensure all chunks have file_name in metadata
            for chunk in chunks:
                if "file_name" not in chunk.metadata:
                    chunk.metadata["file_name"] = file_name

            # Generate UUIDs for all chunks
            uuids = [f"{str(uuid4())}" for _ in range(len(chunks))]

            collections = await self.client.get_collections()

            if self.collection_name in [
                collection_name.name for collection_name in collections.collections
            ]:
                logger.info(
                    f"Collection {self.collection_name} already exists in QdrantDB"
                )
            else:
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
                )

            self.vectors = QdrantVectorStore.from_existing_collection(
                collection_name=self.collection_name,
                embedding=self.embedding_function,
                url=self.qdrant_endpoint,
            )

            # Store the file_name in the payload for each chunk
            await self.vectors.aadd_documents(documents=chunks, ids=uuids)

            logger.info(f"Successfully indexed document {file_name} in QdrantDB")
            return True

        except Exception as e:
            logger.error(f"Error indexing into Qdrant: {e}")
            raise e

    async def delete_chunks_by_file_name(self, file_name):
        """
        Delete all chunks associated with a specific file_name
        """
        try:
            # Create a filter to find documents with the matching file_name
            file_filter = Filter(
                must=[
                    FieldCondition(
                        key="metadata.file_name", match=MatchValue(value=file_name)
                    )
                ]
            )

            # Delete the matching documents
            result = await self.client.delete(
                collection_name=self.collection_name, points_selector=file_filter
            )

            deleted_count = result.deleted
            logger.info(
                f"Successfully deleted {deleted_count} chunks for file {file_name}"
            )
            return deleted_count

        except Exception as e:
            logger.error(f"Error deleting chunks for file {file_name}: {e}")
            raise e

    async def get_retriever(self, top_k=3):
        """
        Returns a retriever for searching documents in the Qdrant vector store.
        """
        try:
            # Initialize the vector store if not already initialized
            if not self.vectors:
                self.vectors = QdrantVectorStore.from_existing_collection(
                    collection_name=self.collection_name,
                    embedding=self.embedding_function,
                    url=self.qdrant_endpoint,
                )
                logger.info(
                    f"Initialized vector store from collection {self.collection_name}"
                )

            # Create and return the retriever with the specified search parameters
            retriever = self.vectors.as_retriever(
                search_type="similarity", search_kwargs={"k": top_k}
            )

            logger.info(f"Created retriever with top_k={top_k}")
            return retriever

        except Exception as e:
            logger.error(f"Error creating retriever: {e}")
            raise e
