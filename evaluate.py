import asyncio
from dataclasses import dataclass
from typing import List

from ingesta import DocumentProcessor, load_documents
from rag import RAGSystem


TOP_K = 5


@dataclass
class BenchmarkCase:
    question: str
    relevant_source: str


BENCHMARK = [
    BenchmarkCase(
        question="¿Qué es un sistema RAG y cuál es su objetivo principal?",
        relevant_source="01_fundamentos_rag.md",
    ),
    BenchmarkCase(
        question="¿Qué son los embeddings y para qué se utilizan en un sistema RAG?",
        relevant_source="02_embeddings_y_similitud.md",
    ),
    BenchmarkCase(
        question="¿Qué es el chunking y qué función cumple en el procesamiento de documentos?",
        relevant_source="03_chunking_y_preprocesamiento.md",
    ),
    BenchmarkCase(
        question="¿Qué ventajas ofrece una base de datos vectorial para la recuperación de información?",
        relevant_source="04_chromadb_y_recuperacion.md",
    ),
    BenchmarkCase(
        question="¿Cómo se relacionan los embeddings con la búsqueda por similitud semántica?",
        relevant_source="02_embeddings_y_similitud.md",
    ),
]


def build_relevant_chunk_ids():
    """Construye el conjunto de chunks relevantes por documento."""

    processor = DocumentProcessor()
    documents = load_documents(processor)

    relevant_chunks = {}

    for document in documents:
        source = document["metadata"]["source"]
        chunk_id = document["id"]

        relevant_chunks.setdefault(source, set()).add(chunk_id)

    return relevant_chunks


def calculate_metrics(
    retrieved_chunk_ids: List[str],
    relevant_chunk_ids: set[str],
) -> tuple[float, float, int]:
    """Calcula Precision@5 y Recall@5 a nivel de chunk."""

    retrieved = retrieved_chunk_ids[:TOP_K]
    retrieved_set = set(retrieved)

    true_positives = len(
        retrieved_set.intersection(relevant_chunk_ids)
    )

    precision = true_positives / TOP_K

    recall = (
        true_positives / len(relevant_chunk_ids)
        if relevant_chunk_ids
        else 0.0
    )

    return precision, recall, true_positives


async def evaluate_case(
    rag_system: RAGSystem,
    case: BenchmarkCase,
    relevant_chunks: dict[str, set[str]],
):
    """Evalúa una pregunta del benchmark."""

    documents = await rag_system.retrieve_documents(
        case.question,
        k=TOP_K,
    )

    retrieved_chunk_ids = [
        document.metadata["chunk_id"]
        for document in documents
    ]

    relevant_chunk_ids = relevant_chunks[
        case.relevant_source
    ]

    precision, recall, true_positives = calculate_metrics(
        retrieved_chunk_ids,
        relevant_chunk_ids,
    )

    print("\n" + "=" * 70)
    print(f"PREGUNTA: {case.question}")
    print(f"FUENTE RELEVANTE: {case.relevant_source}")
    print(
        f"CHUNKS RELEVANTES EN EL DOCUMENTO: "
        f"{len(relevant_chunk_ids)}"
    )

    print("\nCHUNKS RECUPERADOS:")

    for position, document in enumerate(
        documents,
        start=1,
    ):
        chunk_id = document.metadata["chunk_id"]
        source = document.metadata["source"]

        relevant = (
            chunk_id in relevant_chunk_ids
        )

        marker = "RELEVANTE" if relevant else "NO RELEVANTE"

        print(
            f"  {position}. "
            f"{chunk_id} | "
            f"{source} | "
            f"{marker}"
        )

    print(f"\nTRUE POSITIVES: {true_positives}")
    print(f"PRECISION@5: {precision:.2%}")
    print(f"RECALL@5: {recall:.2%}")

    return precision, recall


async def main():
    print("Iniciando benchmark de recuperación RAG...")
    print(f"Consultas: {len(BENCHMARK)}")
    print(f"Top-K: {TOP_K}")
    print("Unidad de evaluación: chunks")

    relevant_chunks = build_relevant_chunk_ids()

    rag_system = RAGSystem()

    results = []

    for case in BENCHMARK:
        result = await evaluate_case(
            rag_system,
            case,
            relevant_chunks,
        )

        results.append(result)

    precision_values = [
        result[0]
        for result in results
    ]

    recall_values = [
        result[1]
        for result in results
    ]

    mean_precision = (
        sum(precision_values)
        / len(precision_values)
    )

    mean_recall = (
        sum(recall_values)
        / len(recall_values)
    )

    print("\n" + "=" * 70)
    print("RESUMEN DEL BENCHMARK")
    print("=" * 70)
    print(f"Preguntas evaluadas: {len(BENCHMARK)}")
    print(f"Precision@5 promedio: {mean_precision:.2%}")
    print(f"Recall@5 promedio: {mean_recall:.2%}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())