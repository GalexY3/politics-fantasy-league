from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parent
points=[24,24]
labels=['Inicio AB20','Tras piloto C01']
for filename,yrange in [('CT2_0_100.png',(0,100)),('CT2_zoom_22_26.png',(22,26))]:
    fig,ax=plt.subplots(figsize=(8,3.6),dpi=160)
    ax.plot([0,1],points,marker='o',linewidth=1.5)
    ax.set_xticks([0,1],labels)
    ax.set_ylabel('CT2 ordinal (1–100)')
    ax.set_ylim(*yrange)
    ax.set_xlim(-0.25,1.25)
    ax.grid(axis='y',alpha=.3)
    ax.set_title('B3 · Predicción político-institucional · sin nueva confirmación')
    ax.text(0.5,0.94,'Puntaje no probabilístico; C01 no aporta evidencia predictiva',transform=ax.transAxes,ha='center',va='top',fontsize=8)
    fig.tight_layout()
    fig.savefig(root/filename)
    plt.close(fig)