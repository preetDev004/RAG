import os
from uuid import uuid4
from services.logger import logger
from qdrant_client import AsyncQdrantClient
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from qdrant_client.http.models import (
    VectorParams,
    Distance,
    Filter,
    FieldCondition,
    MatchValue,
)


class DocumentIndexer:
    def __init__(self):
        # If not hosted, use local Qdrant with Docker
        self.qdrant_endpoint = os.getenv("QDRANT_ENDPOINT_URL")
        self.api_key = os.getenv("QDRANT_API_KEY")

        # Initialize the Qdrant client with proper authentication
        self.client = AsyncQdrantClient(
            url=self.qdrant_endpoint,
            api_key=self.api_key,
            timeout=10.0,  # Increase timeout for better reliability
        )

        self.vectors = None

        self.embedding_function = OpenAIEmbeddings()
        self.collection_name = "rag_bot"

    async def index_into_qdrant(self, extracted_text, file_name, doc_type, chunk_size):
        """
        Index document content into the Qdrant vector database.
        """
        try:
            # Create a document object
            doc = Document(
                page_content=extracted_text,
                metadata={"file_name": file_name, "doc_type": doc_type},
            )

            # Determine optimal chunk size based on text length
            if chunk_size is None:
                text_length = len(extracted_text)
                chunk_size = self._get_optimal_chunk_size(text_length)
                logger.info(f"Using dynamic chunk size: {chunk_size}")

            # Split the document into chunks
            chunks = self._split_document(doc, chunk_size)
            
            # Generate UUIDs for all chunks
            uuids = [f"{str(uuid4())}" for _ in range(len(chunks))]
            
            # Ensure collection exists with correct dimensions
            await self._ensure_collection_exists()
            
            # Store the chunks in Qdrant
            logger.info(f"Adding {len(chunks)} document chunks to Qdrant")
            try:
                await self._add_chunks_to_qdrant(chunks, uuids)
            except Exception as e:
                logger.error(f"Error adding chunks to Qdrant: {e}")
                raise e

            logger.info(f"Successfully indexed document {file_name} in QdrantDB")
            return True

        except Exception as e:
            logger.error(f"Error indexing into Qdrant: {e}")
            raise e
            
    def _get_optimal_chunk_size(self, text_length):
        """Determine optimal chunk size based on text length"""
        if text_length < 10000:
            return 800
        elif text_length < 50000:
            return 1500
        else:
            return 2000
    
    def _split_document(self, doc, chunk_size):
        """Split document into chunks with proper metadata handling"""
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", ",", " "],
            chunk_size=chunk_size,
            chunk_overlap=200,
        )
        chunks = text_splitter.split_documents([doc])
        
        # Ensure all chunks have file_name in metadata
        for chunk in chunks:
            if "file_name" not in chunk.metadata:
                chunk.metadata["file_name"] = doc.metadata.get("file_name", "unknown")
                
        return chunks
        
    async def _ensure_collection_exists(self):
        """Ensure the collection exists with proper configuration"""
        try:
            # Check if collection exists
            collections = await self.client.get_collections()
            collection_exists = self.collection_name in [
                collection.name for collection in collections.collections
            ]
            
            if not collection_exists:
                # Create collection if it doesn't exist
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
                )
                logger.info(f"Created new collection {self.collection_name}")
        except Exception as e:
            logger.warning(f"Error checking/creating collection: {e}")
            # We'll continue and let potential errors be caught later
            
    async def _add_chunks_to_qdrant(self, chunks, uuids):
        """Add document chunks to Qdrant with their embeddings"""
        # Generate embeddings for all documents
        texts = [doc.page_content for doc in chunks]
        metadatas = [doc.metadata for doc in chunks]
        
        # Get embeddings
        embeddings_list = await self.embedding_function.aembed_documents(texts)
        
        # Prepare points for Qdrant
        points = []
        for i, (text, metadata, embedding_vector, id) in enumerate(
            zip(texts, metadatas, embeddings_list, uuids)
        ):
            points.append({
                "id": id,
                "vector": embedding_vector,
                "payload": {"page_content": text, "metadata": metadata},
            })
        
        # Add points to Qdrant
        await self.client.upsert(
            collection_name=self.collection_name, 
            points=points,
            wait=True  # Ensure operation completes before returning
        )
        return True

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
                logger.info("Initializing vector store for retriever")
                
                # Get collection info to validate before initializing QdrantVectorStore
                try:
                    # Make sure to await the coroutine
                    collection_info = await self.client.get_collection(collection_name=self.collection_name)
                    logger.info(f"Retrieved collection info for {self.collection_name}")
                except Exception as e:
                    logger.error(f"Error getting collection info: {e}")
                    raise e
                
                # error if it doesn't exist
                if not collection_info:
                    raise ValueError(f"Collection {self.collection_name} does not exist")
                
                # Create a new QdrantVectorStore instance with only the required parameters
                # to avoid validation issues with async client
                from langchain_qdrant import QdrantVectorStore
                from langchain.vectorstores.utils import DistanceStrategy
                
                self.vectors = QdrantVectorStore(
                    client=self.client,
                    collection_name=self.collection_name,
                    embedding=self.embedding_function,
                    content_payload_key="page_content",
                    metadata_payload_key="metadata",
                    distance_strategy=DistanceStrategy.COSINE
                )
                
                logger.info(f"Initialized vector store from collection {self.collection_name}")

            # Create and return the retriever with the specified search parameters
            retriever = self.vectors.as_retriever(
                search_type="similarity", search_kwargs={"k": top_k}
            )

            logger.info(f"Created retriever with top_k={top_k}")
            return retriever

        except Exception as e:
            logger.error(f"Error creating retriever: {e}")
            raise e
