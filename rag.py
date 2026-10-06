import asyncio
import os
from pathlib import Path
from typing import Any, List

from dotenv import load_dotenv
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_google_genai import ChatGoogleGenerativeAI
from pinecone import Pinecone
from pydantic import BaseModel, ConfigDict, Field

from ingesta import DocumentProcessor, load_documents


load_dotenv()


INDEX_NAME = os.getenv("INDEX_NAME", "rag-ia-cloud")
NAMESPACE = "rag-ia"
TOP_K = 5


class RAGResponse(BaseModel):
    answer: str = Field(
        description="Respuesta basada exclusivamente en el contexto."
    )
    references: List[str] = Field(
        description="Nombres de los documentos utilizados como referencia."
    )


class PineconeSemanticRetriever(BaseRetriever):
    """Retriever semántico sobre un índice Pinecone con embedding integrado."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    index: Any = Field(exclude=True)
    namespace: str = NAMESPACE
    k: int = TOP_K

    def _get_relevant_documents(
        self,
        query: str,
    ) -> List[Document]:
        """Busca documentos semánticamente en Pinecone."""

        results = self.index.search(
            namespace=self.namespace,
            query={
                "inputs": {
                    "text": query,
                },
                "top_k": self.k,
            },
            fields=[
                "chunk_text",
                "source",
                "chunk_index",
                "tokens",
            ],
        )

        if hasattr(results, "result"):
            hits = results.result.hits
        else:
            hits = results["result"]["hits"]

        documents = []

        for hit in hits:
            if hasattr(hit, "fields"):
                fields = hit.fields
            else:
                fields = hit["fields"]

            source = fields["source"]
            chunk_index = int(fields["chunk_index"])

            chunk_id = (
                f"{Path(source).stem}"
                f"_chunk_{chunk_index:03d}"
            )

            documents.append(
                Document(
                    page_content=fields["chunk_text"],
                    metadata={
                        "chunk_id": chunk_id,
                        "source": source,
                        "chunk_index": chunk_index,
                        "tokens": int(fields["tokens"]),
                    },
                )
            )

        return documents


class RAGSystem:
    """Sistema RAG híbrido con BM25 + búsqueda semántica en Pinecone."""

    def __init__(
        self,
        index_name: str = INDEX_NAME,
        namespace: str = NAMESPACE,
        weights: List[float] | None = None,
    ):
        pinecone_api_key = os.getenv("PINECONE_API_KEY")

        if not pinecone_api_key:
            raise RuntimeError(
                "No se encontró PINECONE_API_KEY en el archivo .env."
            )

        if not index_name:
            raise RuntimeError(
                "No se encontró INDEX_NAME en el archivo .env."
            )

        self.index_name = index_name
        self.namespace = namespace

        pinecone = Pinecone(
            api_key=pinecone_api_key
        )

        self.index = pinecone.Index(index_name)

        processor = DocumentProcessor()
        raw_documents = load_documents(processor)

        if not raw_documents:
            raise RuntimeError(
                "No se encontraron documentos en la carpeta data."
            )

        bm25_documents = [
            Document(
                page_content=item["document"],
                metadata={
                    **item["metadata"],
                    "chunk_id": item["id"],
                },
            )
            for item in raw_documents
        ]

        self.bm25_retriever = BM25Retriever.from_documents(
            bm25_documents
        )

        self.bm25_retriever.k = TOP_K

        self.semantic_retriever = PineconeSemanticRetriever(
            index=self.index,
            namespace=self.namespace,
            k=TOP_K,
        )

        self.ensemble_retriever = EnsembleRetriever(
            retrievers=[
                self.bm25_retriever,
                self.semantic_retriever,
            ],
            weights=weights or [0.4, 0.6],
            id_key="chunk_id",
        )

    async def retrieve_documents(
        self,
        query: str,
        k: int = TOP_K,
    ) -> List[Document]:
        """Recupera los mejores documentos mediante EnsembleRetriever."""

        documents = await self.ensemble_retriever.ainvoke(
            query
        )

        return documents[:k]


async def get_rag_response(
    query: str,
    rag_system: RAGSystem,
) -> RAGResponse:
    documents = await rag_system.retrieve_documents(
        query,
        k=TOP_K,
    )

    context_parts = []

    for document in documents:
        context_parts.append(
            f"FUENTE: {document.metadata['source']}\n"
            f"CONTENIDO:\n{document.page_content}"
        )

    context = "\n\n---\n\n".join(context_parts)

    parser = PydanticOutputParser(
        pydantic_object=RAGResponse
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """Eres un asistente técnico especializado en sistemas RAG.

Responde exclusivamente utilizando la información disponible en el CONTEXTO.

Si la respuesta no está presente en el contexto, responde exactamente:
"No lo sé con la información disponible."

No inventes información ni utilices conocimiento externo.

Incluye en 'references' únicamente los nombres de los documentos que realmente utilizaste.

{format_instructions}

CONTEXTO:
{context}
"""
        ),
        (
            "human",
            "Pregunta del usuario: {query}"
        ),
    ])

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        temperature=0,
    )

    chain = prompt | llm | parser

    response = await chain.ainvoke({
        "context": context,
        "query": query,
        "format_instructions": (
            parser.get_format_instructions()
        ),
    })

    response.references = list(
        dict.fromkeys(
            document.metadata["source"]
            for document in documents
        )
    )

    return response


async def main():
    query = input("Pregunta: ")

    try:
        rag_system = RAGSystem()

        response = await get_rag_response(
            query,
            rag_system,
        )

        print("\nRESPUESTA:")
        print(response.answer)

        print("\nREFERENCIAS:")

        for reference in response.references:
            print(f"- {reference}")

    except Exception as e:
        print(
            f"\nError durante la ejecución del RAG: {e}"
        )


if __name__ == "__main__":
    asyncio.run(main())