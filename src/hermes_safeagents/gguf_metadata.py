"""GGUF header metadata reader for decision-model provenance.

Extracted from safeagents-eval run.py so the plugin verifies decision-model
identity without importing the evaluation checkout. Reads only GGUF headers;
no inference, no writes.
"""
import struct
from pathlib import Path


def metadata(path):
    with Path(path).open('rb') as f:
        def num(fmt):return struct.unpack('<'+fmt,f.read(struct.calcsize('<'+fmt)))[0]
        def string():return f.read(num('Q')).decode('utf-8')
        def value(t):
            fmts={0:'B',1:'b',2:'H',3:'h',4:'I',5:'i',6:'f',7:'?',10:'Q',11:'q',12:'d'}
            if t==8:return string()
            if t==9:
                subtype,n=num('I'),num('Q')
                return [value(subtype) for _ in range(n)]
            return num(fmts[t])
        assert f.read(4)==b'GGUF'
        version,n_tensors,n_kv=num('I'),num('Q'),num('Q')
        out={}
        for _ in range(n_kv):
            key=string(); v=value(num('I'))
            if 'decision' in key or key in ('general.architecture','general.name') or ('chat_template' in key and 'systemone' in key):out[key]=v
        return {'file':Path(path).name,'bytes':Path(path).stat().st_size,'version':version,'metadata':out}
