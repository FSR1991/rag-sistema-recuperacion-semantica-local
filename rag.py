import asyncio
import os
from typing import List

import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field


load_dotenv()


VECTORSTORE_DIR = "vectorstore"
COLLECTION_NAME = "rag_ia"


class RAGResponse(BaseModel):
    answer: str = Field(description="Respuesta basada exclusivamente en el contexto.")
    references: List[str] = Field(
        description="Nombres de los documentos utilizados como referencia."
    )


def get_collection():
    client = chromadb.PersistentClient(
        path=VECTORSTORE_DIR
    )

    embedding_function = embedding_functions.DefaultEmbeddingFunction()

    collection = client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function,
    )

    return collection


def retrieve_documents(query: str, n_results: int = 3):
    collection = get_collection()

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    return documents, metadatas


async def get_rag_response(query: str) -> RAGResponse:
    documents, metadatas = retrieve_documents(query, n_results=3)

    context_parts = []

    for document, metadata in zip(documents, metadatas):
        context_parts.append(
            f"FUENTE: {metadata['source']}\n"
            f"CONTENIDO:\n{document}"
        )

    context = "\n\n---\n\n".join(context_parts)

    parser = PydanticOutputParser(pydantic_object=RAGResponse)

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
        "format_instructions": parser.get_format_instructions(),
    })

    response.references = list(dict.fromkeys(
        metadata["source"] for metadata in metadatas
    ))

    return response


async def main():
    query = input("Pregunta: ")

    try:
        response = await get_rag_response(query)

        print("\nRESPUESTA:")
        print(response.answer)

        print("\nREFERENCIAS:")
        for reference in response.references:
            print(f"- {reference}")

    except Exception as e:
        print(f"\nError durante la ejecución del RAG: {e}")


if __name__ == "__main__":
    asyncio.run(main())