# Rights and purpose gate for Congress open data · 28/10/2026

**Status: documentary legal-source audit; NOT a legal opinion, not deployment clearance.** Campaign `PFL-ABH-MAIN20B-20261028`, C03, preregistered. The repository must distinguish **(i) ability to access official institutional material, (ii) the site's reuse terms / copyright permissions, (iii) a separate GDPR lawful basis and purpose-specific safeguards for identifiable people, (iv) scientific/ethical validity of fantasy scores**. Passing one does not imply passing the others.

## Authoritative source texts inspected

1. **Congress legal notice** (https://www.congreso.es/eu/cem/aviso-legal). The site says `www.congreso.es` information is susceptible of reuse, with conditions to preserve content, avoid distorting its meaning, cite the source, mention the last update date and use content diligently and lawfully. This is **general website reuse notice**, not a case-specific opinion permitting every derivative personal profile.
2. **Congress open-data roster catalogue** (https://www.congreso.es/es/opendata/diputados). Publishes active/historic-deputy and other files in CSV/JSON/XML. The mere existence of a machine-readable file does **not** authenticate its first publication instant, validate every identity over time or establish a lawful basis for a different profiling purpose.
3. **Ley 37/2007 (BOE consolidated text)** (https://www.boe.es/buscar/act.php?id=BOE-A-2007-19814), especially Article 3.4 and Article 8.1, in its actual scope: non-commercial and commercial reuse is conceptually contemplated, but the legal framework does not waive personal data protection, source integrity, citation or any applicable purpose-specific limits. The consolidated text itself is informative; precise legal reliance needs the official sources and version verification.
4. **AEPD on lawful processing bases** (https://www.aepd.es/preguntas-frecuentes/2-tus-obligaciones-como-responsable-del-tratamiento/5-bases-legitimadoras-del-tratamiento/FAQ-0214-cuales-son-las-bases-de-legitimacion-para-el-tratamiento-de-datos). Data treatment needs an identified/documented GDPR legal basis, e.g. valid consent, law, contract or duly assessed legitimate interest; publishing data online is **not in itself such a basis**.
5. **AEPD on independent impacts of secondary processing** (https://www.aepd.es/areas-de-actuacion/internet-y-redes-sociales/derecho-al-olvido): original publisher and search engines conduct distinct processing with distinct legal bases and privacy impacts. This supports the need to examine later repackaging rather than assuming the original's purpose survives unchanged.

## Source / purpose matrix

| Operation | What source audit supports | Status for PFL |
|---|---|---|
| Link to official aggregate voting results with source and date | General publication + re-use terms available; preserve context and citations | `DOCUMENTARY_CONDITIONS_KNOWN`, NOT full legal compliance adjudication |
| Copy publisher JSON/XML vote aggregates in a research cache | Possible under applicable reuse rights and technical limits; source bytes and individual dataset rights still to be checked | `CONDITIONAL`, no captured new September XML/JSON |
| Build a persistent named-person historical dossier | Requires own lawful GDPR basis, data minimization, contemporaneous scope, transparency, retention/rights process; separately verify temporal identity | `NOT_APPROVED` |
| Rank or score named politicians based on votes/behavior for a game | New purpose and potential reputational/profiling impact; independent legal/DPO review and substantive validation required | **`BLOCKED`**, original six gates remain 0/6 |
| Infer 'who did not vote' from missing nominal entries | Not an access/rights inference; requires verified eligibility denominator, absence and provenance | `PROHIBITED_UNVERIFIED_INFERENCE` |

### Acceptance conditions before lifting a gate

Obtain the **exact rightsholder and dataset-specific terms** for the proposed files and intended use (including commercial derivative scope); record official sources and update times; classify what constitutes personal data and who is controller; identify and document relevant GDPR legal basis and compatibility with original publication purpose; assess necessity/proportionality and foreseeable harms; design notice, objection/correction and retention controls; seek expert/DPO review and where required an impact assessment. None is waived merely because a parliamentary vote is public.

This audit does **not** claim every reuse is unlawful. It identifies a real general site notice and the independent privacy constraints; the fact-specific authorization for PFL personalized scores has **not** been established. Without that evidence, **do not enable real scoring**.

**AB-DECIDE:** General site reuse conditions documented (positive evidence), but purpose-specific person-profile authorization remains **INCONCLUSIVE / gate-blocking**. C03 is documentary research, not a novel legal conclusion. Source and applicant rights must be revisited for each dataset; no raw nominal data were collected during this cycle.
