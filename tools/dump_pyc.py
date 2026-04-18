import marshal, dis, types, os
p = os.path.join(os.path.dirname(__file__), '..', 'extracted_apk_0_1_34', 'desktop_app.pyc')
out1 = os.path.join(os.path.dirname(__file__), '..', 'extracted_apk_0_1_34', 'desktop_disasm.txt')
out2 = os.path.join(os.path.dirname(__file__), '..', 'extracted_apk_0_1_34', 'desktop_codeinfo.txt')

if not os.path.exists(p):
    print('ERROR: pyc not found at', p)
    raise SystemExit(1)

with open(p,'rb') as f:
    header = f.read(16)
    code = marshal.load(f)


def walk(code, out, prefix=''):
    out.write(f"CODE_OBJECT {prefix}{getattr(code,'co_name','<module>')}\n")
    out.write(f"  argcount={getattr(code,'co_argcount',None)} kwonly={getattr(code,'co_kwonlyargcount',None)}\n")
    out.write(f"  varnames={getattr(code,'co_varnames',())}\n")
    out.write(f"  names={getattr(code,'co_names',())}\n")
    consts=[c for c in getattr(code,'co_consts',()) if isinstance(c,(str,int,float,bytes,tuple))]
    out.write(f"  consts_sample={consts[:30]}\n\n")
    for c in getattr(code,'co_consts',()):
        if isinstance(c, types.CodeType):
            walk(c, out, prefix=prefix+'  ')

with open(out1,'w',encoding='utf-8',errors='replace') as f:
    f.write('PYC_HEADER='+repr(header)+"\n\n")
    dis.dis(code, file=f)

with open(out2,'w',encoding='utf-8',errors='replace') as f:
    f.write('PYC_HEADER='+repr(header)+"\n\n")
    walk(code,f)

print('wrote',out1,out2)
