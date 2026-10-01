# Fundamentos de RAG

## ¿Qué es RAG?

RAG, o Retrieval-Augmented Generation, es una arquitectura que combina la recuperación de información con la generación de texto mediante un modelo de lenguaje. Su objetivo principal es permitir que un sistema de inteligencia artificial responda utilizando información externa proporcionada en el momento de la consulta.

En lugar de depender exclusivamente del conocimiento aprendido durante el entrenamiento del modelo, un sistema RAG puede consultar una colección de documentos y utilizar los fragmentos relevantes como contexto para generar la respuesta.

El flujo básico de RAG puede dividirse en varias etapas: ingesta de documentos, procesamiento y fragmentación, generación de embeddings, almacenamiento vectorial, recuperación de información y generación de la respuesta.

## Ingesta de documentos

La ingesta es el proceso mediante el cual los documentos originales se incorporan al sistema. Los documentos pueden proceder de archivos de texto, documentos Markdown, manuales técnicos, páginas web u otras fuentes.

Antes de almacenar la información es necesario realizar un procesamiento previo. Los documentos pueden contener saltos de línea innecesarios, encabezados repetidos, espacios duplicados o información que no aporta valor semántico.

Una vez limpiado el contenido, se divide en fragmentos denominados chunks. La fragmentación permite trabajar con unidades de información más pequeñas y facilita que el sistema encuentre exactamente la parte del documento relacionada con una consulta.

## Chunking

El chunking consiste en dividir un documento grande en fragmentos más pequeños. Esta etapa es importante porque los modelos de embeddings y los modelos de lenguaje tienen límites de contexto.

Una estrategia habitual es Recursive Character Splitting. Este método intenta conservar la estructura natural del texto utilizando diferentes separadores. Primero intenta dividir por párrafos, después por saltos de línea, posteriormente por espacios y finalmente por caracteres individuales si es necesario.

También puede utilizarse overlap o solapamiento. El overlap permite que una parte del contenido del final de un chunk aparezca nuevamente al comienzo del siguiente. Esto ayuda a conservar información cuando una idea importante se encuentra cerca del límite entre dos fragmentos.

Un chunk demasiado pequeño puede perder contexto. Un chunk demasiado grande puede contener información irrelevante y dificultar la recuperación precisa. Por este motivo, el tamaño debe elegirse buscando un equilibrio entre granularidad y contexto.

## Embeddings

Después de fragmentar los documentos, cada chunk puede transformarse en un embedding. Un embedding es una representación numérica de un texto mediante un vector.

Los embeddings permiten comparar textos utilizando operaciones matemáticas. Dos fragmentos que expresan conceptos relacionados pueden encontrarse próximos dentro del espacio vectorial aunque utilicen palabras diferentes.

Por ejemplo, una consulta como "¿cómo se recupera información relevante?" podría relacionarse semánticamente con un documento que explique mecanismos de búsqueda vectorial aunque no utilice exactamente las mismas palabras.

Para que la comparación sea válida, los documentos y las consultas deben utilizar el mismo modelo de embeddings. Mezclar embeddings generados por modelos diferentes puede producir resultados incorrectos porque los vectores pertenecen a espacios diferentes.

## Recuperación de información

Durante una consulta, el texto introducido por el usuario también se transforma en un embedding. El sistema compara ese vector con los embeddings almacenados en la base vectorial.

La similitud coseno es una métrica habitual para comparar vectores de texto. La búsqueda devuelve los fragmentos que presentan mayor similitud con la consulta.

El número de resultados recuperados debe mantenerse controlado. Recuperar demasiados fragmentos puede introducir información irrelevante y aumentar innecesariamente la cantidad de tokens enviados al modelo de lenguaje.

En un sistema RAG básico, un valor de top_k entre 3 y 5 resultados puede ser suficiente para construir un contexto reducido y relevante.

## Generación aumentada

Una vez recuperados los fragmentos, estos se incorporan al prompt que recibe el modelo de lenguaje. El modelo utiliza el contexto proporcionado para elaborar la respuesta.

Una característica importante de una arquitectura RAG es el grounding. El modelo debe recibir instrucciones explícitas para utilizar únicamente la información disponible en el contexto.

Una instrucción habitual consiste en indicar al asistente que responda basándose exclusivamente en los documentos recuperados y que indique que no conoce la respuesta cuando la información solicitada no aparece en ellos.

Esta estrategia ayuda a reducir las alucinaciones, aunque no garantiza por sí sola que todas las respuestas sean correctas.

## Flujo general

El proceso completo puede resumirse de la siguiente manera:

1. Se reciben los documentos.
2. Se limpia el contenido.
3. Se divide cada documento en chunks.
4. Se generan embeddings para los chunks.
5. Los embeddings y sus documentos se almacenan en una base vectorial.
6. El usuario realiza una consulta.
7. La consulta se transforma en un embedding.
8. Se recuperan los chunks más similares.
9. Los fragmentos recuperados se incorporan al contexto.
10. El modelo de lenguaje genera una respuesta basada en ese contexto.

## Ventajas de RAG

Una arquitectura RAG permite trabajar con información específica que puede actualizarse sin volver a entrenar un modelo de lenguaje completo.

También facilita la incorporación de documentación propia de una organización. Por ejemplo, una empresa puede utilizar RAG para consultar manuales internos, procedimientos, documentación técnica o políticas operativas.

Otra ventaja es la posibilidad de rastrear el origen de la información recuperada. Si cada fragmento contiene metadatos como nombre del archivo, sección o versión del documento, el sistema puede conservar referencias que posteriormente permitan identificar las fuentes utilizadas.

## Limitaciones

RAG no elimina todos los problemas de los modelos de lenguaje. Una recuperación incorrecta puede proporcionar un contexto inadecuado y provocar una respuesta incorrecta.

La calidad del sistema depende de varias etapas: limpieza de documentos, estrategia de chunking, modelo de embeddings, búsqueda vectorial, selección de resultados y prompt utilizado para la generación.

Por esta razón, construir un sistema RAG requiere evaluar el flujo completo y no únicamente el modelo de lenguaje.

## Ejemplo conceptual

Supongamos que una colección contiene documentación sobre sistemas de inteligencia artificial. El usuario pregunta:

"¿Qué función cumple el chunking en un sistema RAG?"

El sistema convierte la pregunta en un embedding y busca los fragmentos más cercanos. Si uno de los documentos explica que el chunking divide documentos grandes en unidades semánticamente coherentes para mejorar la recuperación, ese fragmento se incorpora al contexto.

El modelo recibe entonces la pregunta junto con el contexto recuperado y genera una respuesta utilizando esa información.

Si el usuario pregunta por un tema que no aparece en ninguno de los documentos recuperados, el sistema debe evitar inventar información y responder que no encuentra esa información en el contexto disponible.

## Conclusión

RAG permite conectar modelos de lenguaje con fuentes externas mediante un proceso de recuperación de información. La calidad de este proceso depende de la preparación de los documentos, la fragmentación, los embeddings y la búsqueda vectorial.

Una implementación correctamente diseñada debe recuperar información relevante, proporcionar un contexto limitado y coherente al modelo y exigir que la respuesta permanezca fundamentada en los documentos recuperados.