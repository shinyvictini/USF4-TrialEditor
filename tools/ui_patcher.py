"""Generate expanded USF4 UI archives from verified original resources."""
import hashlib
import struct
import zlib
from pathlib import Path
import bz2

SPECS = {
 'trial_tasks.emz': ('trial_tasks', '8f2fc64fefe7b72a4555d4eb93bdda49fc0e6b9f74bb21a0eb98876f72afd677', '0bebe99a5eb6c4d0686a95cc1959f39b3f701a180a98331d5459cd11041b9691', '2e802ebd3a97128e1cb8243788b6135709014ed93675cae83e7523a3149d63b1', 16),
 'ultra_trial_menu.emz': ('ultra_trial_menu', '63ee74b3dd593e5575b826b023f405da2cf50b3824bbbabb5d1bca00bd7f4a24', '8f119fbd9763092e202e7e36078730c5f276d97fb822fdbca7f870e3468f7c9d', 'b766514522ff229b51a8b2e860febd20772c336bcca7654ecfc26cb960a579ab', 128),
}
def digest(data): return hashlib.sha256(data).hexdigest()
def u32(data, pos): return struct.unpack_from('<I', data, pos)[0]
def put(data, pos, value): struct.pack_into('<I', data, pos, value)
def signed(data):
    return int.from_bytes(data, 'little') & ((1<<63)-1) if not data[7]&128 else -(int.from_bytes(data,'little') & ((1<<63)-1))

def apply_patch(old, patch):
    # Standard BSDIFF40, using only the Python standard library.
    if patch[:8] != b'BSDIFF40': raise ValueError('Invalid patch header')
    a,b,n = (signed(patch[i:i+8]) for i in (8,16,24))
    if min(a,b,n)<0 or n>1000000 or 32+a+b>len(patch): raise ValueError('Invalid patch lengths')
    ctrl=bz2.decompress(patch[32:32+a]); diff=bz2.decompress(patch[32+a:32+a+b]); extra=bz2.decompress(patch[32+a+b:]); out=bytearray(); p=q=r=c=0
    while len(out)<n:
        if c+24>len(ctrl): raise ValueError('Truncated patch')
        x,y,z=(signed(ctrl[i:i+8]) for i in (c,c+8,c+16)); c+=24
        if min(x,y)<0 or len(out)+x+y>n or q+x>len(diff) or r+y>len(extra): raise ValueError('Invalid patch control')
        out.extend((diff[q+i]+(old[p+i] if 0<=p+i<len(old) else 0))&255 for i in range(x)); p+=x; q+=x
        out.extend(extra[r:r+y]); r+=y; p+=z
    return bytes(out)

def build_ui(original, patch_dir):
    original=Path(original); key=original.name
    if key=='trial_tasks_tu3.emz': key='trial_tasks.emz'
    stem, expected, gfx_hash, new_hash, alignment=SPECS[key]
    raw=original.read_bytes()
    if digest(raw)!=expected: raise ValueError(f'Unsupported original: {original}')
    emb=zlib.decompress(raw[u32(raw,12):],-15)
    if emb[:4]!=b'#EMB' or len(emb)!=u32(raw,8) or zlib.crc32(emb)!=u32(raw,4): raise ValueError('Invalid EMB archive')
    count=u32(emb,12); table=u32(emb,24); names=u32(emb,28)
    entries=[]
    for i in range(count):
        t=table+8*i; start=t+u32(emb,t); size=u32(emb,t+4); f=u32(emb,names+4*i)
        entries.append((t,start,size,f,emb[f:emb.index(b'\0',f)]))
    target=b'trial_tasks.gfx' if stem=='trial_tasks' else b'trial_menu.gfx'
    t,start,size,f,name=next(e for e in entries if e[4]==target)
    movie=emb[start:start+size]
    if movie[:3]!=b'CFX': raise ValueError('Expected CFX movie')
    gfx=b'GFX'+movie[3:8]+zlib.decompress(movie[8:])
    if digest(gfx)!=gfx_hash: raise ValueError('Original GFX hash mismatch')
    modified=apply_patch(gfx,(Path(patch_dir)/(stem+'.gfx.bsdiff')).read_bytes())
    if digest(modified)!=new_hash: raise ValueError('Modified GFX hash mismatch')
    cfx=b'CFX'+modified[3:8]+zlib.compress(modified[8:],9)
    end=min([e[1] for e in entries if e[1]>start]+[e[3] for e in entries if e[3]>start])
    padded=cfx+bytes((-len(cfx))%alignment)
    delta=len(padded)-(end-start)
    result=bytearray(emb[:start]+padded+emb[end:])
    for et,es,ez,ef,en in entries:
        put(result,et,es+(delta if es>=end else 0)-et)
        put(result,et+4,(len(padded) if stem=='trial_tasks' else len(cfx)) if et==t else ez)
    for i,e in enumerate(entries): put(result,names+4*i,e[3]+(delta if e[3]>=end else 0))
    header=bytearray(raw[:16]); put(header,4,zlib.crc32(result)); put(header,8,len(result))
    compressor=zlib.compressobj(9,zlib.DEFLATED,-15)
    return bytes(header)+compressor.compress(result)+compressor.flush()
