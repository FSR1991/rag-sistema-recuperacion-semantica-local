import os

from dotenv import load_dotenv
from pinecone import Pinecone


load_dotenv()


REQUIRED_ENV_VARS = [
    "PINECONE_API_KEY",
    "INDEX_NAME",
]

PINECONE_CLOUD = "aws"
PINECONE_REGION = "us-east-1"

EMBEDDING_MODEL = "llama-text-embed-v2"
EMBEDDING_FIELD = "chunk_text"


def validate_environment() -> dict[str, str]:
    """Valida las variables de entorno necesarias para Pinecone."""

    missing = [
        variable
        for variable in REQUIRED_ENV_VARS
        if not os.getenv(variable)
    ]

    if missing:
        raise RuntimeError(
            "Faltan variables de entorno requeridas: "
            + ", ".join(missing)
        )

    return {
        variable: os.environ[variable]
        for variable in REQUIRED_ENV_VARS
    }


def create_or_validate_index() -> None:
    """Crea o valida el índice Pinecone con inferencia integrada."""

    config = validate_environment()

    pinecone = Pinecone(
        api_key=config["PINECONE_API_KEY"]
    )

    index_name = config["INDEX_NAME"]

    if pinecone.has_index(index_name):
        print(
            f"El índice '{index_name}' ya existe."
        )
        print(
            "No se realizaron cambios sobre el índice existente."
        )
        return

    print(
        f"Creando índice Pinecone Integrated Inference: "
        f"'{index_name}'..."
    )

    pinecone.create_index_for_model(
        name=index_name,
        cloud=PINECONE_CLOUD,
        region=PINECONE_REGION,
        embed={
            "model": EMBEDDING_MODEL,
            "field_map": {
                "text": EMBEDDING_FIELD,
            },
        },
    )

    print(
        f"Índice '{index_name}' creado correctamente."
    )
    print(
        f"Modelo de embeddings: {EMBEDDING_MODEL}"
    )
    print(
        f"Campo de texto: {EMBEDDING_FIELD}"
    )
    print(
        f"Configuración: "
        f"{PINECONE_CLOUD} / {PINECONE_REGION}"
    )


if __name__ == "__main__":
    create_or_validate_index()