# BR20K · fuente oficial parlamentaria: endpoint de roster observable

Fecha de revisión: 26/10/2026. No se integra ninguna persona individual ni se extraen biografías.

El [portal público de diputados del Congreso](https://www.congreso.es/gl/opendata/diputados) enlaza ficheros CSV, JSON y XML de legislaturas y miembros activos.

**Comprobación de lectura:** el enlace oficial de *Diputados en activo* JSON \(https://www.congreso.es/webpublica/opendata/diputados/DiputadosActivos__20260725050010.json\) fue legible mediante el lector web en esta campaña. Se observaron nombres de campos `NOMBRE`, `CIRCUNSCRIPCION`, `FORMACIONELECTORAL`, `FECHACONDICIONPLENA`, `FECHAALTA`, `GRUPOPARLAMENTARIO`, `FECHAALTAENGRUPOPARLAMENTARIO`. El enlace a *Todos los diputados de todas las legislaturas* de julio 2026 devolvió cache miss.

**Importante:** el nombre del fichero y los campos visibles **no certifican** que el enlace sea la versión más reciente el 26/10/2026, ni su población exacta, filas, validez jurídica de cada afiliación, cambios posteriores, licencia de redistribución o fecha histórica de primera publicación. Los bytes completos originales no se depositaron ni hashearon en el proyecto. No se creó un historial persona-semana ni se habilitó scoring. No insertar perfiles biográficos personales de fuente sin necesidad y revisión legal.

**Control adversarial:** `FECHAALTAENGRUPOPARLAMENTARIO` es fecha de alta en un grupo, no necesariamente la fecha de salida; una instantánea vigente no permite reconstruir cambios de grupo durante una legislatura sin fuentes de baja y versiones.

**Siguiente paso:** recuperar el JSON mediante un mecanismo que almacene bytes y SHA-256, registrar licencia y capture timestamp, seleccionar únicamente campos públicos necesarios para rol e identidad, validar IDs frente a otro roster histórico y registrar conflictos en vez de colapsarlos por nombre.

El Registro de Partidos del Ministerio, por su parte, sigue anunciado como [aplicación de consulta con exportación PDF](https://datos.gob.es/es/aplicaciones/consulta-del-registro-de-partidos-politicos), sin fichero completo capturado; no equivale a un censo descargado.

**AB-J:** fuente identificada, formato observable, **STOP_R5** para pipeline de campo hasta disponer de originales con procedencia comprobable.
