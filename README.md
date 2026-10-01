# Sistema de Recuperación Semántica Local (RAG)

Sistema RAG (Retrieval-Augmented Generation) desarrollado en Python. El proyecto implementa un flujo completo de ingesta, fragmentación, persistencia vectorial, recuperación semántica y generación de respuestas fundamentadas exclusivamente en el contexto recuperado.

## Tecnologías utilizadas

- Python 3.12
- LangChain
- LCEL
- ChromaDB
- Google Gemini
- Pydantic
- python-dotenv
- RecursiveCharacterTextSplitter
- tiktoken

## Estructura del proyecto

```text
RAG Sistema Recuperacion Semantica Local/
│
├── data/
│   ├── 01_fundamentos_rag.md
│   ├── 02_embeddings_y_similitud.md
│   ├── 03_chunking_y_preprocesamiento.md
│   └── 04_chromadb_y_recuperacion.md
│
├── ingesta.py
├── rag.py
├── README.md
├── .env
├── .gitignore
└── vectorstore/