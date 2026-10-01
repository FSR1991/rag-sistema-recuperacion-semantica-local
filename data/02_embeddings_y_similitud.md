# Embeddings y similitud semántica

## Concepto de embedding

Un embedding es una representación numérica de un objeto, como un fragmento de texto, mediante un vector de números. En aplicaciones de inteligencia artificial, los embeddings permiten representar información textual dentro de un espacio matemático donde los contenidos semánticamente relacionados pueden ubicarse cerca.

Esta representación permite que una aplicación compare conceptos aunque las palabras utilizadas sean diferentes.

Por ejemplo, las frases "limitar el tráfico de red" y "restringir el ancho de banda disponible" utilizan vocabulario diferente, pero pueden representar una intención similar. Un sistema basado únicamente en palabras clave podría no identificar correctamente esta relación, mientras que una búsqueda semántica puede encontrarla mediante embeddings.

## Representación vectorial

Un texto puede convertirse en un vector formado por numerosos valores numéricos. Cada dimensión participa en la representación aprendida por el modelo de embeddings.

No es necesario interpretar individualmente cada número del vector. Lo importante es utilizar el vector completo para realizar operaciones matemáticas y comparar diferentes textos.

Cuando dos textos representan conceptos relacionados, sus vectores pueden presentar una orientación similar dentro del espacio vectorial.

## Similitud coseno

La similitud coseno es una de las métricas más utilizadas para comparar embeddings de texto. Mide el ángulo existente entre dos vectores y se concentra principalmente en su dirección.

La fórmula conceptual es:

similitud = producto_punto(A, B) / (norma(A) * norma(B))

Un resultado cercano a 1 representa una alta similitud entre las direcciones de los vectores. Un resultado bajo representa una menor relación según el espacio vectorial utilizado.

Una ventaja de la similitud coseno es que la longitud absoluta del vector tiene menos influencia que su orientación. Esto resulta útil cuando se comparan fragmentos de texto de diferentes longitudes.

## Distancia euclídea

La distancia euclídea mide la separación entre dos puntos en el espacio vectorial. Es una distancia geométrica directa y puede utilizarse para comparar embeddings.

Sin embargo, cuando los vectores tienen magnitudes diferentes, la distancia euclídea puede verse afectada por esa diferencia. Por esta razón, la métrica elegida debe ser coherente con el modelo de embeddings y con la forma en que se almacenan los vectores.

## Producto punto

El producto punto combina la orientación de dos vectores con sus magnitudes. Puede ser útil en sistemas donde la magnitud contiene información relevante.

En sistemas de recuperación semántica es importante elegir una métrica adecuada y utilizarla de forma consistente durante la indexación y la consulta.

## Modelos de embeddings

Existen diferentes familias de modelos para generar embeddings. Algunos modelos son generales y otros están especializados en dominios concretos.

Una regla fundamental es no mezclar embeddings producidos por modelos diferentes dentro de una misma colección vectorial. Cada modelo puede utilizar una dimensionalidad y un espacio vectorial diferente.

Si los documentos fueron indexados utilizando un determinado modelo, las consultas deben convertirse en embeddings utilizando ese mismo modelo para que la comparación tenga sentido.

## Búsqueda semántica

La búsqueda semántica transforma la consulta del usuario en un embedding y compara ese vector con los vectores almacenados en una base de datos.

Por ejemplo, una colección podría contener estos fragmentos:

- "La aplicación permite limitar el ancho de banda por usuario."
- "El sistema registra conexiones rechazadas por el firewall."
- "El servidor utiliza almacenamiento SSD."

Si el usuario pregunta "¿cómo se puede restringir el tráfico?", el primer fragmento debería resultar más relevante porque su significado está relacionado con la consulta.

El sistema no necesita encontrar exactamente las palabras "restringir" y "tráfico". La representación vectorial permite buscar relaciones semánticas.

## Embeddings en RAG

En una arquitectura RAG, los embeddings cumplen una función fundamental durante la recuperación.

Primero se procesan los documentos y se dividen en chunks. Cada chunk se transforma en un embedding y se almacena junto con el texto y sus metadatos.

Cuando llega una consulta, la pregunta también se convierte en un embedding. La base vectorial compara la consulta con los embeddings almacenados y devuelve los fragmentos más similares.

Estos fragmentos recuperados forman posteriormente el contexto que se entrega al modelo de lenguaje.

## Importancia de los metadatos

Los embeddings no deberían almacenarse aislados. Es recomendable asociarlos con metadatos que permitan identificar el origen de cada fragmento.

Un registro puede incluir información como:

- nombre del archivo;
- sección del documento;
- versión;
- fecha;
- categoría;
- identificador del chunk.

Los metadatos permiten aplicar filtros y facilitan la trazabilidad de las fuentes utilizadas durante una respuesta.

## Limitaciones de los embeddings

Los embeddings no representan una comprensión lógica perfecta. Son representaciones estadísticas aprendidas a partir de grandes cantidades de datos.

Esto significa que dos frases relacionadas con un mismo tema pueden aparecer cercanas aunque una contenga una negación o una afirmación diferente.

Por ejemplo:

"El servidor tiene espacio disponible."

"No hay espacio disponible en el servidor."

Las dos frases tratan sobre almacenamiento y pueden producir vectores relativamente cercanos, aunque transmiten información diferente.

Por esta razón, una arquitectura RAG no debe depender exclusivamente de la similitud vectorial. También debe utilizar contexto, instrucciones de generación, validación y pruebas.

## Aplicaciones

Los embeddings pueden utilizarse para búsqueda semántica, sistemas de recomendación, clasificación, agrupación de documentos y detección de contenido relacionado.

En sistemas de soporte técnico, por ejemplo, pueden utilizarse para identificar tickets que describen problemas similares aunque los usuarios empleen expresiones diferentes.

También pueden utilizarse para encontrar documentación técnica relacionada con una pregunta, localizar procedimientos internos o recuperar fragmentos relevantes para un asistente basado en RAG.

## Conclusión

Los embeddings convierten información textual en representaciones vectoriales que pueden compararse matemáticamente. La similitud coseno es una métrica habitual para medir la cercanía semántica entre estos vectores.

En una arquitectura RAG, los embeddings permiten conectar la pregunta del usuario con los fragmentos de conocimiento almacenados en una base vectorial.

Para obtener resultados confiables es necesario utilizar el mismo modelo de embeddings durante la indexación y durante las consultas, mantener una estrategia coherente de recuperación y considerar las limitaciones de la representación semántica.