"""Deterministic local matplotlib plot, no AI image synthesis."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent
x=[0,6,12,18,24,30]
for full in (True,False):
 fig,ax=plt.subplots(figsize=(9.7,4.6))
 ax.plot(x,[24]*len(x),marker='o',lw=2.3,label='CT2: predicción individual parlamentaria')
 ax.axhline(24,alpha=.2,ls='--')
 ax.set_ylim(0,100) if full else ax.set_ylim(21,27)
 ax.set_xticks(x, ['Anterior','A · 6','B · 12','C · 18','D · 24','E · 30'])
 ax.set_ylabel('CT2 ordinal (NO probabilidad)')
 ax.set_title('CT2 tras 30 incrementos de ingeniería (sin corpus nominal validado)')
 ax.grid(alpha=.18)
 ax.legend(loc='upper right');fig.tight_layout()
 fig.savefig(P/('CT2_FULL_0_100.png' if full else 'CT2_ZOOM_21_27.png'),dpi=150)
 plt.close(fig)
fig,ax=plt.subplots(figsize=(9.7,4.6))
ax.plot(x,[1]*len(x),marker='s',lw=2.4)
ax.set(ylim=(-.13,3.13),ylabel='VSDS: valor para sociología y data science',title='Escala exclusiva del proyecto: nivel 1/3 (instrumento verificado)')
ax.set_xticks(x,['Anterior','A · 6','B · 12','C · 18','D · 24','E · 30']);ax.set_yticks([0,1,2,3],['0 · Sin utilidad','1 · Instrumento local','2 · Campo validado','3 · Uso externo validado'])
ax.grid(alpha=.18);fig.tight_layout();fig.savefig(P/'VSDS_0_3.png',dpi=150);plt.close(fig)
