import re

patt1 = re.compile(r'(?<=\/)\d*')
patt2 = re.compile(r'\/\d*')
match=re.findall(patt1,'/20+4d3')[0]
match=0 if match is None or match=='' else match
print(match)
msg=0
print(re.sub(patt2,'','/20+4d3'))