# Publicar manualmente o restaurar escritura del conector GitHub

Destino comprobado: `https://github.com/GalexY3/polictics_fantasy_league` (público y vacío al 24-10-2026).

**Bloqueo observado:** el conector pudo LEER el repositorio y su nombre, pero la escritura `create_file`, `create_blob` y `create_issue` devolvió 403 `Resource not accessible by integration`. No se creó ningún commit remoto. Revisar en las opciones de instalación GitHub App/ChatGPT el acceso al repositorio recién creado (permisos Contents: write) y volver a intentar. No interpretar `permissions.push=true` del perfil como garantía de escritura de la integración.

Alternativa usando Git con acceso autenticado por el titular:

```bash
# desde la carpeta politics_fantasy_league descomprimida
python -m pytest -q
git init
git add .
git commit -m "Initial Politics Fantasy research AB30 documentary and prototype"
git branch -M main
git remote add origin https://github.com/GalexY3/polictics_fantasy_league.git
git push -u origin main
```

No se incluyen credenciales, datos políticos personales extraídos ni corpus con licencias desconocidas. Si el repositorio remoto deja de estar vacío, hay que recuperar primero su historial y reconciliarlo antes de hacer push, no hacer `--force`.

**Regla AB:** los ensayos de ingeniería aquí documentados son anteriores a cualquier commit remoto; NO reclamar freeze-before-run retroactivo. Los próximos experimentos con datos políticos deben congelarse en un commit previo distinto y con los datasets/licencias asegurados.