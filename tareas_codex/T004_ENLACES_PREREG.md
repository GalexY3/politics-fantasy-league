# T004 · Reparación técnica preregistrada: enlaces BOE

La revisión T004 encontró dos enlaces cuyo atributo `href` se escapa como HTML pero acepta esquemas no seguros si se manipulan los datos locales. No se ha demostrado explotación y no se presupone exposición a Internet.

Antes de modificar el código se fija este contraste: ejecutar los renderizadores reales con datos ficticios de enlaces `javascript:`, `data:`, HTTP, usuario embebido y dominio engañoso; no deben generar enlaces navegables para estos valores. Un enlace HTTPS del BOE debe seguir disponible. Limitar los enlaces de estos dos paneles BOE a `https:` y hosts exactos `boe.es` / `www.boe.es`, sin usuario, contraseña ni puerto no estándar; usar texto no enlazado cuando no cumplan. Conservar el fallo inicial del test y repetir las suites relacionadas. No cambia el contenido científico, la procedencia ni los gates. Es reparación técnica de la tarea T004, no ciclo AB autónomo.
