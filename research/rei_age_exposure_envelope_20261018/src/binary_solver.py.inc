def _write_all(stream,data):
    remaining=memoryview(data)
    while remaining:
        written=stream.write(remaining)
        if written is None or written<=0: raise RuntimeError('BINARY_RPC_WRITE_FAILED')
        remaining=remaining[written:]

def _read_exact(stream,size):
    chunks=[]
    remaining=size
    while remaining:
        chunk=stream.read(remaining)
        if not chunk: raise RuntimeError('BINARY_RPC_TRUNCATED')
        chunks.append(chunk)
        remaining-=len(chunk)
    return b''.join(chunks)

def send(mode,active,x,y):
    if a.rpc_mode == 'binary64':
        if mode == 'OLD':
            raise ValueError('OLD regression RPC requires text mode')
        values=np.asarray(y,dtype='<f8')
        _write_all(server.stdin,struct.pack('<cIdI',mode.encode('ascii'),active,x,values.size))
        _write_all(server.stdin,values.tobytes())
        server.stdin.flush()
        head=_read_exact(server.stdout,5)
        status,length=struct.unpack('<BI',head)
        payload=_read_exact(server.stdout,length)
        if status: return payload.decode()
        if mode == 'R':
            if length!=8*values.size: raise RuntimeError('BINARY_RPC_RHS_SIZE')
            return np.frombuffer(payload,dtype='<f8').copy()
        return payload.decode()
    _write_all(server.stdin,(f'{mode} {active} {x:.17e} '+' '.join(format(v,'.17e') for v in y)+'\n').encode());server.stdin.flush()
    line=server.stdout.readline()
    if not line:raise RuntimeError(server.stderr.read().decode(errors='replace'))
    return line.decode().strip()
