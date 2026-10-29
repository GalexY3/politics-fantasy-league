"""Look for task's independently stated counts in official publication originals."""
import json,pathlib,re,hashlib,xml.etree.ElementTree as ET
R=pathlib.Path(__file__).parent; D=R/'private_raw'
dog=(D/'dog_galicia.html').read_text('utf8');boe=(D/'boe_xml.xml').read_text('utf8')
ET.fromstring(boe)
queries={'dog':{'valid_header':'1.501.857','valid_provinces':'1.501.757',
 'candidate_header':'1.488.805','candidate_provinces':'1.488.705','voters':'1.515.944','invalid':'14.187'},
 'boe':{'voters':'17.652.007','valid':'17.527.438','invalid':'124.569'}}
reports={}
for name,source in (('dog',dog),('boe',boe)):
 reports[name]={label:{'display':token,'occurrences':len(re.findall(re.escape(token),source))} for label,token in queries[name].items()}
report={'comparison':'literal occurrences in official HTML/XML, not sufficient on their own to disambiguate semantic table headings',
 'source_hashes':{'dog_html':hashlib.sha256((D/'dog_galicia.html').read_bytes()).hexdigest(),'boe_xml':hashlib.sha256((D/'boe_xml.xml').read_bytes()).hexdigest()},
 'queries':reports,'galicia_csv_reconstruction':'AGGREGATE.json',
 'first_public_at':'UNKNOWN','discrepancy_cause':'UNKNOWN'}
(R/'PUBLICATION_COUNTS.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(report,ensure_ascii=False,indent=2))
