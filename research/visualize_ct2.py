"""Draw the CT2 scale and an expanded view from ACTUAL ledger entries.

CT2=ordinal uncalibrated governance judgement, NOT a probability.
"""
from pathlib import Path
import csv
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
records=list(csv.DictReader((ROOT/'CT2_TRAJECTORY.csv').open(encoding='utf-8')))
y=[int(x['CT2']) for x in records]
x=list(range(len(y)))
for scale,name in [((0,100),'CT2_full.png'),((22,26),'CT2_zoom.png')]:
    fig,ax=plt.subplots(figsize=(10,3.6))
    ax.plot(x,y,marker='.',markersize=4,linewidth=1.2)
    ax.set_ylim(*scale)
    ax.set_xlim(0,max(x))
    ax.set_xlabel('Fase documental (BEGIN y C01–C30)')
    ax.set_ylabel('CT2 ordinal (1–100)')
    ax.set_title('B3 · Predicción parlamentaria — sin actualización empírica')
    ax.grid(alpha=.25)
    fig.text(.1,.01,'Serie plana por falta de experimentos externos; la escala no representa probabilidades.',fontsize=9)
    fig.tight_layout(rect=(0,.045,1,1))
    dest=ROOT.parent/'figures'/name
    fig.savefig(dest,dpi=180)
    plt.close(fig)
    print(dest)
