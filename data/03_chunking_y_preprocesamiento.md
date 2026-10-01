# Chunking y preprocesamiento de documentos

## Importancia del preprocesamiento

Los documentos utilizados por un sistema RAG pueden contener información útil mezclada con ruido. Un archivo puede incluir espacios duplicados, saltos de línea innecesarios, encabezados repetidos, caracteres extraños o información de formato que no aporta significado.

Antes de generar embeddings es conveniente realizar una etapa de limpieza. El objetivo es reducir el ruido sin eliminar información relevante.

Una limpieza incorrecta también puede ser perjudicial. Si se eliminan palabras importantes, títulos o relaciones entre fragmentos, el sistema puede perder información necesaria para responder una consulta.

## Limpieza del texto

El preprocesamiento puede incluir la normalización de espacios, la eliminación de saltos de línea excesivos y la corrección de caracteres innecesarios.

Por ejemplo, un texto puede contener varios espacios consecutivos:

"El sistema     recupera     documentos."

Después de una normalización puede convertirse en:

"El sistema recupera documentos."

También pueden aparecer múltiples saltos de línea que no representan una separación real entre conceptos.

La limpieza debe conservar la estructura semántica siempre que sea posible.

## ¿Qué es el chunking?

El chunking consiste en dividir un documento grande en fragmentos más pequeños llamados chunks.

Los modelos de embeddings tienen límites de entrada y la recuperación necesita encontrar unidades de información suficientemente específicas. Por esta razón, almacenar un documento completo como un único vector puede ser poco eficiente.

Si un manual contiene cien páginas sobre diferentes temas, un solo embedding tendría que representar todos esos conceptos simultáneamente. La búsqueda podría recuperar el documento general, pero tendría dificultades para identificar exactamente la sección relacionada con una pregunta concreta.

Dividir el documento permite generar un embedding independiente para cada fragmento.

## Tamaño de los chunks

El tamaño del chunk debe buscar un equilibrio entre precisión y contexto.

Un chunk demasiado pequeño puede contener solamente una frase incompleta y perder información necesaria para comprenderla.

Un chunk demasiado grande puede incluir varios conceptos diferentes y hacer que la representación semántica sea menos específica.

En este proyecto se utiliza como referencia un tamaño mínimo de aproximadamente 500 tokens para los fragmentos, junto con un solapamiento de 50 tokens.

El tamaño debe medirse utilizando tokens cuando la consigna o el modelo lo requieran, porque caracteres y tokens no representan exactamente la misma unidad.

## Recursive Character Splitting

Recursive Character Splitting es una estrategia habitual para dividir documentos.

El algoritmo intenta utilizar separadores en una jerarquía. Primero busca separaciones naturales entre párrafos, después saltos de línea, posteriormente espacios y finalmente caracteres individuales como último recurso.

Esta estrategia permite conservar mejor la estructura del contenido que una división rígida cada determinada cantidad de caracteres.

El objetivo es evitar cortar conceptos importantes cuando existe una separación semánticamente más apropiada.

## Overlap

El overlap o solapamiento permite repetir una parte del contenido entre dos chunks consecutivos.

Por ejemplo, si un fragmento termina explicando una idea y el siguiente continúa desarrollándola, un pequeño solapamiento permite que ambos mantengan parte del contexto.

En este proyecto se utiliza un overlap de referencia de 50 tokens.

El solapamiento aumenta ligeramente la cantidad total de texto almacenado, pero puede mejorar la recuperación cuando una información importante se encuentra cerca del límite entre dos fragmentos.

## Tokens y caracteres

Un error común consiste en asumir que un número fijo de caracteres equivale a un número fijo de tokens.

Los tokens dependen del tokenizador utilizado por el modelo. Una palabra puede representar uno o varios tokens y la cantidad puede variar según el idioma y los caracteres utilizados.

Por este motivo, cuando se necesita controlar el tamaño real de los fragmentos, es recomendable utilizar un tokenizador compatible con el modelo correspondiente.

Herramientas como tiktoken permiten contar tokens antes de almacenar los chunks.

## Chunking y recuperación

La estrategia de chunking influye directamente en la calidad de la búsqueda vectorial.

Supongamos que un documento explica cómo configurar un sistema RAG y contiene varias secciones sobre embeddings, chunking, bases vectoriales y generación.

Si todo el documento se almacena como un único vector, una consulta específica sobre embeddings puede recuperar el documento completo.

Si el documento está dividido correctamente, el sistema puede recuperar solamente el fragmento que explica los embeddings.

Esto permite entregar al modelo de lenguaje un contexto más pequeño y relevante.

## Metadatos de los chunks

Cada fragmento puede almacenarse junto con metadatos.

Un chunk podría tener los siguientes datos:

- source: nombre del archivo original;
- chunk_id: identificador del fragmento;
- section: sección del documento;
- version: versión del contenido.

Los metadatos permiten conocer de dónde procede cada fragmento recuperado.

Esta información resulta especialmente útil cuando una aplicación RAG necesita mostrar referencias o justificar de qué documento provino una respuesta.

## Errores frecuentes

Uno de los errores más comunes es utilizar chunks demasiado pequeños. Esto puede provocar que las respuestas recuperadas carezcan de contexto.

Otro problema es utilizar chunks excesivamente grandes. En ese caso, un fragmento puede contener información de varios temas y dificultar la recuperación precisa.

También es un error ignorar el overlap. Si una explicación importante queda dividida exactamente entre dos fragmentos, puede perderse parte del contexto durante una búsqueda.

Finalmente, no limpiar los documentos antes de generar embeddings puede introducir ruido y reducir la calidad de la recuperación.

## Evaluación del chunking

Una estrategia de chunking debe evaluarse utilizando consultas reales.

Si las consultas recuperan fragmentos irrelevantes, puede ser necesario modificar el tamaño de los chunks, el overlap o la estrategia de separación.

También puede evaluarse cuántos tokens tiene cada fragmento y qué proporción de las consultas recupera correctamente la información necesaria.

No existe un único tamaño perfecto para todos los documentos. La estrategia debe adaptarse al tipo de contenido y al objetivo de recuperación.

## Conclusión

El chunking transforma documentos grandes en unidades de información adecuadas para embeddings y recuperación semántica.

Una buena estrategia combina limpieza, tamaño controlado, separación respetando la estructura del texto y overlap suficiente para conservar el contexto.

En un sistema RAG, esta etapa es fundamental porque la calidad de los fragmentos recuperados condiciona directamente la información que recibirá el modelo de lenguaje.