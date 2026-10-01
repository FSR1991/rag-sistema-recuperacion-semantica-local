# ChromaDB y recuperación semántica

## ¿Qué es una base de datos vectorial?

Una base de datos vectorial permite almacenar representaciones numéricas de información y realizar búsquedas basadas en similitud.

En una arquitectura RAG, los documentos se transforman en chunks y cada chunk se convierte en un embedding. La base vectorial almacena estos embeddings junto con el contenido original y sus metadatos.

Cuando llega una consulta, el sistema genera un embedding para la pregunta y busca los vectores más cercanos.

## ChromaDB

ChromaDB es una base de datos vectorial de código abierto que puede utilizarse localmente.

Para aplicaciones de desarrollo y proyectos que no necesitan una infraestructura distribuida compleja, ChromaDB puede ejecutarse mediante un cliente persistente.

La persistencia permite que los datos sobrevivan después de cerrar el programa. Esto significa que no es necesario reconstruir toda la colección cada vez que se ejecuta la aplicación.

## Persistencia local

Una instancia persistente de ChromaDB utiliza una ruta local para almacenar la información.

Por ejemplo:

"./vectorstore"

La aplicación puede inicializar un cliente persistente apuntando a esa carpeta. Los datos almacenados permanecen disponibles para futuras ejecuciones del programa.

La persistencia es especialmente importante en sistemas RAG porque generar embeddings para muchos documentos puede consumir tiempo y recursos.

Si la aplicación vuelve a crear todos los embeddings cada vez que se ejecuta, el proceso resulta innecesariamente costoso y lento.

## Colecciones

Los documentos y sus embeddings se organizan dentro de colecciones.

Una colección puede representar un conjunto de conocimiento determinado. Por ejemplo, una aplicación podría tener una colección llamada "documentacion_ia".

Al trabajar con una colección es posible agregar documentos, consultarlos, actualizarlos y eliminarlos.

## Identificadores

Cada documento almacenado debe tener un identificador.

Los identificadores deben ser estables y deterministas siempre que sea posible.

Un identificador aleatorio puede dificultar la actualización de un documento porque la aplicación no sabrá qué ID corresponde al contenido anterior.

Una estrategia posible consiste en utilizar identificadores estructurados o derivados del contenido.

Por ejemplo:

"01_fundamentos_rag_chunk_001"

Este identificador permite relacionar el registro con el archivo y con la posición del fragmento.

## Upsert

La operación upsert permite crear un registro si no existe o actualizarlo si ya existe.

Esto resulta útil durante la ingesta porque evita problemas relacionados con IDs duplicados.

Si un documento fue modificado y mantiene el mismo identificador, la aplicación puede reemplazar su contenido y su embedding correspondiente.

Cuando el texto cambia, el embedding también debe actualizarse porque representa el contenido anterior.

## Lectura exacta

Una base vectorial puede recuperar información mediante identificadores o filtros de metadatos.

Esta operación es diferente de una búsqueda semántica.

Una lectura exacta responde a una pregunta como:

"¿Cuál es el documento cuyo ID es 01_fundamentos_rag_chunk_001?"

En este caso no es necesario calcular qué documento es semánticamente más parecido.

## Búsqueda semántica

La búsqueda semántica compara la consulta con los embeddings almacenados.

Por ejemplo, si el usuario pregunta:

"¿Por qué es necesario dividir los documentos?"

La consulta puede recuperar fragmentos que explican el chunking aunque no contengan exactamente las mismas palabras.

El resultado de una búsqueda semántica normalmente incluye los documentos más cercanos según la métrica configurada.

## Top K

El parámetro top_k determina cuántos resultados se recuperan.

Si top_k es 3, el sistema intenta recuperar los tres fragmentos más relevantes.

Utilizar un valor demasiado alto puede introducir información innecesaria en el contexto del modelo de lenguaje.

En un RAG básico, utilizar entre 3 y 5 fragmentos puede proporcionar un equilibrio razonable entre cobertura y cantidad de contexto.

El valor adecuado depende del tamaño de los chunks, del tipo de documentos y de la complejidad de las preguntas.

## Metadatos

Los metadatos proporcionan información adicional sobre cada fragmento.

Un registro podría contener:

- source: nombre del archivo;
- chunk_id: identificador del fragmento;
- category: categoría temática;
- version: versión del documento.

Los metadatos permiten filtrar información y también facilitan la trazabilidad.

Por ejemplo, después de generar una respuesta, la aplicación puede indicar que la información provino de "03_chunking_y_preprocesamiento.md".

## CRUD en una base vectorial

Las operaciones básicas pueden entenderse de la siguiente manera:

Create: agregar nuevos documentos y sus embeddings.

Read: recuperar documentos por ID, metadatos o similitud.

Update: modificar el contenido o los metadatos de un documento y actualizar su representación vectorial cuando sea necesario.

Delete: eliminar documentos que ya no deben formar parte del conocimiento disponible.

En ChromaDB, upsert resulta especialmente útil para combinar creación y actualización.

## Consistencia de embeddings

Todos los documentos de una colección deben utilizar un modelo de embeddings compatible.

La consulta también debe utilizar ese mismo modelo.

Si los documentos fueron vectorizados utilizando un modelo y la consulta se genera con otro modelo diferente, las coordenadas no representan necesariamente el mismo espacio semántico.

Esto puede producir resultados de recuperación incorrectos.

Por este motivo, la configuración del modelo de embeddings debe mantenerse estable durante la vida de una colección.

## Flujo de recuperación

Una consulta RAG basada en ChromaDB puede seguir estos pasos:

1. El usuario introduce una pregunta.
2. La pregunta se convierte en un embedding.
3. ChromaDB compara el vector de consulta con los vectores almacenados.
4. Se seleccionan los fragmentos con mayor similitud.
5. Los documentos recuperados se transforman en contexto.
6. El contexto se incorpora al prompt.
7. El modelo de lenguaje genera una respuesta fundamentada en ese contexto.
8. La aplicación puede devolver referencias de los documentos utilizados.

## Persistencia y actualización

La persistencia permite que una colección continúe disponible entre diferentes ejecuciones.

Sin embargo, persistencia no significa que los datos sean inmutables.

Cuando un documento cambia, el sistema debe detectar la modificación y actualizar el registro correspondiente.

Una estrategia de ingesta eficiente puede comprobar si una colección ya existe y procesar únicamente documentos nuevos o modificados.

Esto evita repetir trabajo innecesariamente.

## Ejemplo conceptual

Supongamos que la colección contiene los cuatro documentos utilizados en este proyecto.

El usuario pregunta:

"¿Qué es el overlap en el chunking?"

La pregunta se transforma en un embedding y ChromaDB recupera los fragmentos más relacionados con chunking.

El sistema puede recuperar información de "03_chunking_y_preprocesamiento.md".

Estos fragmentos se incorporan al contexto del modelo de lenguaje y permiten generar una respuesta basada en la documentación almacenada.

Si el usuario pregunta por un tema completamente ausente de la colección, el sistema debería reconocer que no existe información suficiente y evitar inventar una respuesta.

## Conclusión

ChromaDB proporciona una forma sencilla de persistir embeddings y realizar búsquedas semánticas localmente.

En un sistema RAG, la combinación de embeddings, chunks, metadatos y búsqueda vectorial permite recuperar información relevante antes de consultar al modelo de lenguaje.

La persistencia evita reconstruir la base en cada ejecución, mientras que las operaciones de creación, lectura, actualización y eliminación permiten mantener el conocimiento actualizado.

Una implementación correcta debe conservar la consistencia del modelo de embeddings, utilizar identificadores estables y limitar la cantidad de resultados recuperados para mantener un contexto útil.