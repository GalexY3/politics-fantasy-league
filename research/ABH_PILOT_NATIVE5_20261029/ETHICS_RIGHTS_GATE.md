# PFL · Dictamen de requisitos previos de piloto humano (29/10/2026)
**Estado: documentación y verificación de fuentes oficiales. NO constituye dictamen jurídico, informe de comité, aprobación institucional ni tratamiento autorizado. No se han reclutado personas.**

## Fuentes institucionales consultadas

- [Comité de Ética de la Investigación, Universidad de Salamanca](https://investigacion.usal.es/es/comite-bioetica): portal de CEI, acceso a procedimientos y contacto `ceinves@usal.es`. El portal indica que los estudios con humanos deben proteger dignidad, derechos, bienestar y datos personales; para determinar si este estudio concreto requiere informe o exención, **consultar CEI** antes de invitar participantes.
- [AEPD: forma del consentimiento](https://www.aepd.es/preguntas-frecuentes/2-tus-obligaciones-como-responsable-del-tratamiento/5-bases-legitimadoras-del-tratamiento/FAQ-0211-segun-el-rgpd-como-debe-solicitarse-el-consentimiento-de-los-interesados-para-tratar-sus-datos-personales): inequívoco, acción afirmativa, libre, informado y revocable; exige poder demostrarlo. No sirven casillas premarcadas ni inacción.
- [AEPD: bases de licitud](https://www.aepd.es/preguntas-frecuentes/2-tus-obligaciones-como-responsable-del-tratamiento/5-bases-legitimadoras-del-tratamiento/FAQ-0214-cuales-son-las-bases-de-legitimacion-para-el-tratamiento-de-datos): identificar y documentar base jurídica pertinente para cada tratamiento. **No asumir** que publicar una encuesta de respuestas ficticias exime de protección de datos.
- [AEPD: datos anónimos](https://www.aepd.es/preguntas-frecuentes/0-conceptos-basicos/FAQ-0005-sobre-los-datos-anonimizados): anonimización efectiva exige que no sea razonablemente posible reidentificar; la mera omisión de nombres o emails no es suficiente.
- [Manual/protocolo PFL ya aprobado como esquema técnico, NO como estudio humano](STUDY_PROTOCOL_PLACEHOLDER): remitirse al protocolo real de la campaña antecesora `../ABH_PROSPECTIVE_PILOT5_20261029/STUDY_PROTOCOL_DRAFT.md`. Sigue en **BORRADOR NO APROBADO**.

## Puertas requeridas antes de un estudio real

1. Presentar al CEI o tutor institucional el protocolo, cuatro condiciones T×L, materiales ficticios, plan de reclutamiento y daños potenciales; determinar informe/dispensa aplicable y conservar respuesta oficial. **PENDIENTE**.
2. Identificar responsable de tratamiento, finalidad, base jurídica concreta, conservación, seguridad y gestión de derechos con asesoramiento apropiado (p. ej. delegado de protección de datos institucional). **PENDIENTE**.
3. Presentar información inteligible al participante adulto y un mecanismo real de consentimiento, preferiblemente desacoplado de outcomes cuando la trazabilidad de retirada sea factible. **PENDIENTE**.
4. Completar preregistro científico: número de participantes y justificación de potencia/sensibilidad, reglas de exclusión, desenlace primario real, desenlaces secundarios, incertidumbre estadística, pérdidas y aleatorización oculta. **PENDIENTE**.
5. Hacer pilotaje cognitivo de los ítems, paridad de longitud/tiempo y accesibilidad de los cuatro tutoriales, y evaluación de posible inducción a decisiones políticas. **PENDIENTE**.
6. Construir infraestructura de sesión/autorización **diferente de los mocks**; versiones actualizadas deben rechazar todas las claves heredadas o Symbol, pero no basta eso. En este bloque hay **solo un servidor GET/HEAD en 127.0.0.1**, sin endpoint de recogida. **NINGUNA PUERTA SUPERADA**.

## Riesgos comprobados y mitigaciones locales

**Evidencia adversarial nueva:** en las cinco funciones/experimentos de la campaña previa se detectó que algunos validadores JavaScript basados únicamente en `Object.keys` aceptaban campos heredados y `Symbol` (metadatos de preferencia política simulados). Se endurecieron tres funciones para exigir objeto plano, claves propias estrictas y propiedades de datos. Las 84 verificaciones nativas anteriores siguen pasando en el código actualizado. **No se ha corregido ni pretendido corregir el carácter falsificable del objeto `approval` mock**: el único servidor accesible no lo expone y no hay recogida de humanos.

**Aviso de alcance:** el nuevo código de interfaz permite cambiar manualmente las cuatro vistas, por lo que **no es una asignación aleatoria experimental**. Una persona podría abrir la demo local, pero sus acciones no se transmiten ni se analizan. La interfaz no prueba efectos, no valida el cuestionario y **no constituye un estudio piloto con humanos**.

**Decisión R5:** pausar toda recogida humana, cualquier despliegue remoto, scores políticos y claims de validación hasta obtener los elementos externos enumerados arriba. Seguir únicamente con QA técnica diferenciable, no rellenar ciclos con simulaciones.
