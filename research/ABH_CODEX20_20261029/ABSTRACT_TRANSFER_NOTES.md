# Transferencia abstracta, con limites

No se afirma entrenamiento persistente del modelo ni descubrimiento metodologico. Estas distinciones explican decisiones observadas durante la campana:

| Apariencia | Propiedad que falta | Ejemplo observado | Falsador util |
| --- | --- | --- | --- |
| Identificador de version valido | Implementacion de esa version | C01 aceptaba v999 con formulas v1 | Solicitar version no implementada |
| Timestamp parseable | Dia calendario real y conocimiento historico | C03 normalizaba 30 de febrero; C06 separa fechas | Fecha imposible y fuente publicada despues del corte |
| Filas completas | Unidad de observacion y exposicion correcta | C07-C09 separan roster, display, sala y cluster | No respondedor o cambio de sala |
| Resultado numerico exacto | Identificacion del estimando sustantivo | C10 limita retencion, no efecto sobre outcome | Dos mundos con mismos agregados y diferentes efectos |
| Archivo y hash consistentes | Autenticidad, derechos o primera publicacion | C14-C15 comprueban integridad local | Misma cadena de bytes con procedencia o permiso distintos |
| Muchas pruebas verdes | Cobertura del codigo realmente integrado | C16 descubre tests fuera del glob anterior | Introducir fallo en un test de src y observar descubrimiento |

La estrategia transferible es identificar primero la propiedad que se pretende concluir, buscar un contraejemplo que conserve la apariencia pero rompa esa propiedad, y limitar la conclusion a lo que el control distingue. Los ejemplos sinteticos sirven para comprobar software; no confirman conductas humanas ni superioridad de AB.
