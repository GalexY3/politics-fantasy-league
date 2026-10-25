# Capa de datos de campo CSV — v0.5, reproducción offline

**Estado**: herramienta de ingeniería con 30 contratos, evaluada sobre datos *sintéticos*. No es un análisis probado de las 726.564 filas nominales anunciadas por Congreso Abierto ni una certificación de sus recuentos. Está diseñada para facilitar esa transición **sin** inventar pertenencias, ausencia o fecha de publicación.

## Fuente y adquisición

- Congreso de los Diputados: [votaciones oficiales](https://www.congreso.es/es/opendata/votaciones).
- [Congreso Abierto](https://congresoabierto.org/datos/): página de exportación CSV de *Votaciones* y *Votos de cada diputado*. Su página documenta columnas con nombres fijos y una licencia CC BY 4.0, con atribución: «Congreso Abierto (congresoabierto.org), a partir de datos oficiales del Congreso de los Diputados». Revisión de condiciones vigente y origen real por archivo siguen siendo obligatorios.
- [Metodología secundaria](https://congresoabierto.org/metodologia/): los temas se derivan por palabras del título, no son categorías originales del Congreso. La documentación señala excepciones como votaciones secretas o por llamamiento, y usa grupo parlamentario publicado para esa fecha. Esto **no** demuestra que el CSV local sea íntegro o correcto.
- No se recopila automáticamente nada. Descarga desde tu navegador legítimamente, guarda **ambos CSV crudos**, registra zona horaria y timestamp *real de adquisición* y conserva una copia inmutable. No conviertas la `fecha` de evento en fecha original de publicación.

## Uso, desde la raíz de este proyecto

En Windows PowerShell con instalación editable (`python -m pip install -e .`):

```powershell
python -m politics_fantasy.field_cli --individual .\data\local_field\votos_diputados.csv --aggregate .\data\local_field\votaciones.csv --acquired-at 2026-10-25T08:00:00+01:00 --out .\data\local_field\report.json
```

El timestamp de arriba es **solo un ejemplo**, sustitúyelo por la hora real registrada durante la descarga. Sin instalación editable, desde Linux/macOS: `PYTHONPATH=src python -m politics_fantasy.field_cli ...`.

La utilidad acepta `utf-8` y `utf-8-sig`, exige `votacion_id, fecha, diputado_id, grupo, voto` y `id, fecha, si, no, abstencion, no_vota` respectivamente, y valida los valores «Sí», «No», «Abstención», «No vota». Otros valores se rechazan en lugar de recodificarse silenciosamente. Un cambio real de esquema puede requerir modificar el adaptador tras verificar el archivo original.

El reporte JSON no contiene nombre ni identificador de diputado. Contiene hashes SHA-256 de los archivos fuente, momento de adquisición declarado, contadores, conciliación de votaciones, banderas de calidad, y advertencias sobre censos, grupos y sesgos. Es un **recibo de procesamiento**: su firma detecta modificaciones accidentales del informe pero no autentica criptográficamente la fuente institucional. La escritura se realiza sin sobrescribir y de modo atómico mediante creación temporal + enlace exclusivo.

Ejecuta `python run_demo.py` y abre **Observatorio → Auditoría CSV**. El servidor lee exclusivamente el recibo localizado en `data/local_field/report.json`, verificado antes de devolver un subconjunto fijo de campos agregados mediante `GET /api/field`. Ningún endpoint acepta subir filas nominales ni puntuar personas reales. Si el recibo se altera o no existe, el sistema muestra estado rechazado/no importado.

## Alcances y falsadores

Una conciliación exacta entre las dos tablas solo demuestra que **esos dos archivos** coinciden en los recuentos; no demuestra cobertura de la legislatura, censos de todos los escaños, atribución de grupo en fecha ni ausencia de exclusiones, filtros, identidades modificadas o cambios retrospectivos de la fuente. Votos nominales no disponibles no se imputan como `NO_VOTE`; ese estado únicamente representa una fila explícita con «No vota». Dos votaciones de una misma sesión no son independientes para inferencia.

**Gates de VSDS 2/3:** documentación/legalidad de cada descarga; cotejo de una muestra aleatoria de registros contra JSON oficiales; reconstrucción de censo de diputados en fecha; historial de primera publicación real; soporte temporal; comparadores estadísticos competentes bajo paridad informativa; replicación fuera del desarrollo. Sin esos controles la herramienta permanece en **VSDS 1/3**.

No alojes aquí los CSV crudos con datos de personas; la carpeta `data/local_field/` está excluida de Git. El juego fantasy usa personajes y puntuaciones totalmente ficticios.
