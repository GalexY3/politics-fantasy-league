"""Generate strictly source-backed CT2 and source coverage figures (not empirical uncertainty)."""
from pathlib import Path
import json
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/AB30_FULL_20261025';SRC=ROOT/'data/upstream_curated_7/derived_anonymous_counts.json'
data=json.loads(SRC.read_text(encoding='utf-8'))['records']
for bounds,name in [((0,100),'CT2_full_0_100.png'),((20,28),'CT2_zoom_20_28.png')]:
    fig,ax=plt.subplots(figsize=(10,3.5));ax.plot([0,30],[24,24],marker='o');ax.set(xlim=(0,30),ylim=bounds,xlabel='Ciclos A–J registrados',ylabel='CT2 (ordinal; no probabilidad)',title='Rama de predicción parlamentaria: sin evidencia nueva confirmatoria')
    ax.grid(alpha=.25);fig.tight_layout();fig.savefig(OUT/name,dpi=160);plt.close(fig)
fig,ax=plt.subplots(figsize=(10,4));x=list(range(7));missing=[350-sum(z['nominal']) for z in data];ax.bar(x,missing);ax.set_xticks(x,[z['day'] for z in data],rotation=45,ha='right');ax.set(ylabel='Entradas nominales faltantes (sobre 350)',xlabel='Siete ejemplos seleccionados, no muestra aleatoria',title='Fuente secundaria: discrepancia nominal y agregada por votación');fig.tight_layout();fig.savefig(OUT/'NOMINAL_GAPS_7.png',dpi=160);plt.close(fig)
