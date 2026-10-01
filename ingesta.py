import re
from pathlib import Path
from typing import List

import chromadb
from chromadb.utils import embedding_functions
import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter


DATA_DIR = Path("data")
VECTORSTORE_DIR = Path("vectorstore")
COLLECTION_NAME = "rag_ia"


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
    print("Iniciando ingesta...")

    VECTORSTORE_DIR.mkdir(exist_ok=True)

    client = chromadb.PersistentClient(
        path=str(VECTORSTORE_DIR)
    )

    embedding_function = embedding_functions.DefaultEmbeddingFunction()

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function,
    )

    # Evita volver a procesar todo si la colección ya contiene información.
    if collection.count() > 0:
        print(
            f"La colección ya contiene {collection.count()} chunks. "
            "No se realizará una nueva ingesta."
        )
        return

    processor = DocumentProcessor()
    documents = load_documents(processor)

    if not documents:
        print("No se encontraron documentos en la carpeta data.")
        return

    collection.upsert(
        ids=[item["id"] for item in documents],
        documents=[item["document"] for item in documents],
        metadatas=[item["metadata"] for item in documents],
    )

    print(f"Ingesta completada: {len(documents)} chunks almacenados.")
    print(f"Base vectorial: {VECTORSTORE_DIR}")


if __name__ == "__main__":
    main()