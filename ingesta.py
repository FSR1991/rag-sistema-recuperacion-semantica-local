import os
import re
from pathlib import Path
from typing import List

import tiktoken
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone


load_dotenv()


DATA_DIR = Path("data")
INDEX_NAME = os.getenv("INDEX_NAME", "rag-ia-cloud")
NAMESPACE = "rag-ia"


class DocumentProcessor:
    def __init__(self, model_encoding: str = "cl100k_base"):
        self.tokenizer = tiktoken.get_encoding(model_encoding)

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=lambda text: len(self.tokenizer.encode(text)),
            separators=["\n\n", "\n", " ", ""],
        )

    def clean_text(self, text: str) -> str:
        """Limpia espacios y saltos de línea innecesarios."""

        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n[ \t]+", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    def calculate_tokens(self, text: str) -> int:
        """Calcula la cantidad de tokens del texto."""

        return len(self.tokenizer.encode(text))

    def process_document(self, raw_text: str) -> List[str]:
        """Limpieza y fragmentación del documento."""

        cleaned_text = self.clean_text(raw_text)
        chunks = self.splitter.split_text(cleaned_text)

        return chunks


def load_documents(processor: DocumentProcessor):
    """Lee todos los documentos Markdown de la carpeta data."""

    documents = []

    for file_path in sorted(DATA_DIR.glob("*.md")):
        raw_text = file_path.read_text(encoding="utf-8")
        chunks = processor.process_document(raw_text)

        for index, chunk in enumerate(chunks):
            documents.append({
                "id": f"{file_path.stem}_chunk_{index:03d}",
                "document": chunk,
                "metadata": {
                    "source": file_path.name,
                    "chunk_index": index,
                    "tokens": processor.calculate_tokens(chunk),
                },
            })

    return documents


def main():
    print("Iniciando ingesta en Pinecone Cloud...")

    pinecone_api_key = os.getenv("PINECONE_API_KEY")

    if not pinecone_api_key:
        raise RuntimeError(
            "No se encontró PINECONE_API_KEY en el archivo .env."
        )

    if not INDEX_NAME:
        raise RuntimeError(
            "No se encontró INDEX_NAME en el archivo .env."
        )

    processor = DocumentProcessor()
    documents = load_documents(processor)

    if not documents:
        print("No se encontraron documentos en la carpeta data.")
        return

    pinecone = Pinecone(api_key=pinecone_api_key)
    index = pinecone.Index(INDEX_NAME)

    records = [
        {
            "_id": item["id"],
            "chunk_text": item["document"],
            "source": item["metadata"]["source"],
            "chunk_index": item["metadata"]["chunk_index"],
            "tokens": item["metadata"]["tokens"],
        }
        for item in documents
    ]

    batch_size = 96

    for start in range(0, len(records), batch_size):
        batch = records[start:start + batch_size]

        index.upsert_records(
            NAMESPACE,
            batch,
        )

        print(
            f"Batch enviado: {start + 1}-"
            f"{min(start + batch_size, len(records))} "
            f"de {len(records)} chunks."
        )

    print(f"Ingesta completada: {len(documents)} chunks almacenados.")
    print(f"Índice Pinecone: {INDEX_NAME}")
    print(f"Namespace: {NAMESPACE}")


if __name__ == "__main__":
    main()