#!/usr/bin/env python3
from pathlib import Path
import re

p=Path('main_menu/setup/start/06_pops.txt')
text=p.read_text(encoding='utf-8')
pattern=re.compile(r"([^^\s=\n][^=\n]*)\s*=\s*{")

from collections import defaultdict

def find_matching_brace(text,start_idx):
    j=start_idx
    depth=0
    n=len(text)
    while j<n:
        if text[j]=='{':
            depth+=1
        elif text[j]=='}':
            depth-=1
            if depth==0:
                return j+1
        j+=1
    return -1

candidates=[]
i=0
while True:
    m=pattern.search(text,i)
    if not m:
        break
    start=m.start()
    block_start=m.end()-1
    block_end=find_matching_brace(text,block_start)
    if block_end==-1:
        break
    block=text[start:block_end]
    # find pops
    pops=[]
    idx=0
    while True:
        mm=re.search(r'define_pop\s*=\s*{', block[idx:])
        if not mm:
            break
        s=idx+mm.start()
        bs=idx+mm.end()-1
        e=find_matching_brace(block,bs)
        if e==-1:
            break
        pops.append(block[s:e])
        idx=e
    attrs=[]
    for pb in pops:
        a={k:v for k,v in re.findall(r'(\w+)\s*=\s*([^\s\}]+)',pb)}
        s=float(a.get('size','0'))
        attrs.append((a.get('type'),a.get('culture'),s,pb))
    total_jurchen=sum(1 for t,c,s,p in attrs if c=='jurchen_culture')
    nobles_jurchen=sum(1 for t,c,s,p in attrs if t=='nobles' and c=='jurchen_culture')
    if total_jurchen>0 and nobles_jurchen>0 and total_jurchen==nobles_jurchen:
        sum_mongo=sum(s for t,c,s,p in attrs if c=='mongolian_culture')
        sum_tumed=sum(s for t,c,s,p in attrs if c=='tumed_culture')
        if sum_mongo>0 or sum_tumed>0:
            # get location name
            name=m.group(1).strip()
            candidates.append((name,sum_mongo,sum_tumed,len([1 for t,c,s,p in attrs if t=='nobles'])))
    i=block_end

for name,sm,st,n in candidates:
    print(name, 'mongolian=',sm,'tumed=',st,'nobles=',n)

print('Total candidates:',len(candidates))
