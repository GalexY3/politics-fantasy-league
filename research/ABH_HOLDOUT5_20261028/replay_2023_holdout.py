from fractions import Fraction
from collections import Counter

def dh(votes,seats,valid,threshold):
    elig={k:v for k,v in votes.items() if v*100>=threshold*valid}
    qq=sorted([(Fraction(v,d),v,k) for k,v in elig.items() for d in range(1,seats+1)],reverse=True)
    return Counter(k for _,_,k in qq[:seats])
def ham(votes,seats,valid,threshold):
    elig={k:v for k,v in votes.items() if v*100>=threshold*valid}
    s=sum(elig.values()); p={k:Fraction(v*seats,s) for k,v in elig.items()}
    x={k:int(v) for k,v in p.items()}; rem=seats-sum(x.values())
    for k in sorted(elig, key=lambda k:(p[k]-x[k],elig[k],k),reverse=True)[:rem]:x[k]+=1
    return Counter({k:v for k,v in x.items() if v>0})
def transfers(a,b):return sum(abs(a[k]-b[k]) for k in a.keys()|b.keys())//2
NA={'UPN':92392,'PSN-PSOE':68247,'EH Bildu':56535,'Geroa Bai':43660,'PPN':24019,'Contigo Zurekin':20095,'Vox':14197,'PUM+J':1740,'Ciudadanos':1273,'Eguzkilore':1261,'Voluntad Foral':582}
RIO={'PSOE':53562,'VINEA':954,'E_BLANCO':619,'Cs':1473,'PACMA':1065,'PLRi':4349,'PP':76205,'PODEMOS_IU':8543,'PR_E':6016,'VOX':12773}
names=('PSOE','PP','FORO','VOX','IU','SOS','PODEMOS','CIUDADANOS','PACMA','PCTE','SUMA','ANDECHA','PUMJ','VERDES','PUEDE')
W=(22482,21236,4049,3950,3278,2574,1063,315,281,126,93,79,44,0,0)
C=(157852,139012,14022,46452,35588,2848,18937,4333,2990,1197,981,1066,665,1717,236)
E=(15665,14883,1581,3871,1908,416,1052,326,0,78,74,100,80,0,0)
elections=[('Navarra',[(NA,50,329861,3)]),('Asturias',[(dict(zip(names,W)),6,60683,3),(dict(zip(names,C)),34,435475,3),(dict(zip(names,E)),5,40865,3)]),('La Rioja',[(RIO,33,167919,5)])]
for state,parts in elections:
    legal=Counter(); n=Counter();h=Counter();regional=[]
    for party,seats,valid,th in parts:
        lg=dh(party,seats,valid,th); nt=dh(party,seats,valid,0); hm=ham(party,seats,valid,th)
        legal.update(lg);n.update(nt);h.update(hm)
        regional.append({'legal':dict(lg),'no_threshold':dict(nt),'hamilton':dict(hm),'removed_threshold_seat_transfers':transfers(lg,nt),'hamilton_seat_transfers':transfers(lg,hm)})
    print(state,'total legal',dict(legal),'no threshold',dict(n),'hamilton',dict(h),'national transfers no threshold',transfers(legal,n),'hamilton',transfers(legal,h),'district',regional)
