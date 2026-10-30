from pathlib import Path
import base64,hashlib,json,os,re,socket,subprocess,tarfile,threading,time,sys

ROOT=Path(__file__).resolve().parent
REPO=Path(r'C:\Github\Politics-Fantasy-Codex')
RUNTIME=Path(os.environ['TEMP'])/'pfl-linux-vm'
SHARE=ROOT/'share'
PORT=19536
COMMIT='20e01950bc00044b546c7e7c658fab168232bb57'
assert subprocess.check_output(['git','rev-parse','exec/pfl-mechanism-and-t028-qa-20261029'],cwd=REPO,text=True).strip()==COMMIT
bundle=SHARE/'repo.bundle'
subprocess.run(['git','bundle','create',str(bundle),'exec/pfl-mechanism-and-t028-qa-20261029'],cwd=REPO,check=True)
subprocess.run(['git','bundle','verify',str(bundle)],cwd=REPO,check=True,capture_output=True)
print('BUNDLE',bundle.stat().st_size,hashlib.sha256(bundle.read_bytes()).hexdigest(),flush=True)
args=[str(RUNTIME/'qemu/qemu-system-x86_64.exe'),'-m','2048','-smp','1','-accel','tcg',
      '-kernel',str(RUNTIME/'alpine/boot/vmlinuz-virt'),'-initrd',str(RUNTIME/'alpine/boot/initramfs-virt'),
      '-append','console=ttyS0 modules=loop,squashfs,sd-mod,usb-storage quiet noapic',
      '-cdrom',str(RUNTIME/'alpine-virt-3.24.3-x86_64.iso'),
      '-drive',f'file=fat:{SHARE.as_posix()},format=raw,if=ide,snapshot=on',
      '-netdev','user,id=net0','-device','e1000,netdev=net0',
      '-display','none','-serial',f'tcp:127.0.0.1:{PORT},server=on,wait=off','-monitor','none','-no-reboot']
(ROOT/'qemu_args.json').write_text(json.dumps(args,indent=2)+'\n')
hostlog=(ROOT/'qemu_host.log').open('wb')
proc=subprocess.Popen(args,stdout=hostlog,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
(ROOT/'qemu.pid').write_text(str(proc.pid))
sock=None
try:
 for _ in range(100):
  try:sock=socket.create_connection(('127.0.0.1',PORT),timeout=.5);break
  except OSError:
   if proc.poll() is not None:raise RuntimeError('QEMU exited '+str(proc.returncode))
   time.sleep(.2)
 if sock is None:raise RuntimeError('No serial TCP')
 sock.settimeout(.5)
 data=bytearray(); lock=threading.Lock(); done=False
 serial=(ROOT/'serial.log').open('wb')
 def reader():
  global done
  while not done:
   try:
    chunk=sock.recv(65536)
    if not chunk:break
    with lock:data.extend(chunk)
    serial.write(chunk);serial.flush()
   except socket.timeout:pass
   except OSError:break
 threading.Thread(target=reader,daemon=True).start()
 def text():
  with lock:return bytes(data).decode('utf-8','replace')
 def waitfor(token,timeout):
  end=time.monotonic()+timeout;last=time.monotonic()
  while time.monotonic()<end:
   if token in text():return
   if proc.poll() is not None:raise RuntimeError('QEMU stopped before '+token)
   if time.monotonic()-last>30:
    s=text();stages=re.findall(r'T025_STAGE_[A-Z]+',s)
    print('WAITING',token,'STAGE',stages[-1] if stages else 'BOOT','SERIAL_BYTES',len(data),flush=True);last=time.monotonic()
   time.sleep(.2)
  raise TimeoutError(token+' not seen')
 def send(command):
  for char in command:
   sock.sendall(char.encode());time.sleep(.025)
 waitfor('localhost login:',120);send('root\r');waitfor('localhost:~#',30)
 print('LOGGED_IN',flush=True)
 send('mount -o ro /dev/sda1 /mnt; sh /mnt/bootstrap.sh\r')
 waitfor('T025_STAGE_DONE',1000)
 payload=text();match=re.search(r'T025_ARCHIVE_BEGIN\r?\n([A-Za-z0-9+/=\r\n]+)\r?\nT025_ARCHIVE_END',payload)
 if not match:raise RuntimeError('No archive block')
 blob=base64.b64decode(match.group(1));archive=ROOT/'results.tgz';archive.write_bytes(blob)
 after=payload[match.end():]
 expected=re.search(r'([a-f0-9]{64})\s+/tmp/t025-results.tgz',after)
 digest=hashlib.sha256(blob).hexdigest()
 if not expected or expected.group(1)!=digest:raise RuntimeError('Archive digest mismatch '+digest)
 with tarfile.open(archive,'r:gz') as tf:
  for member in tf.getmembers():
   path=Path(member.name)
   if path.is_absolute() or '..' in path.parts or member.issym() or member.islnk():raise RuntimeError('Unsafe archive member')
  tf.extractall(ROOT,filter='data')
 manifest=json.loads((ROOT/'results/MANIFEST.json').read_text())
 for name,info in manifest['files'].items():
  f=ROOT/'results'/name
  assert f.stat().st_size==info['bytes'] and hashlib.sha256(f.read_bytes()).hexdigest()==info['sha256'],name
 print('RESULTS_VERIFIED',digest,flush=True)
 print((ROOT/'results/exits.txt').read_text(),flush=True)
 for name in ['achievements','atlas','counts','atlas_tests','pytest','node']:
  s=(ROOT/'results'/f'{name}.out').read_text(encoding='utf-8',errors='replace')
  print(name,'\n'+'\n'.join(s.splitlines()[-10:]),flush=True)
 send('poweroff\r');proc.wait(timeout=45);print('VM_POWERED_OFF',proc.returncode,flush=True)
 done=True;sock.close();serial.close()
except Exception:
 if sock is not None:
  try:
   for char in 'poweroff\r':sock.sendall(char.encode());time.sleep(.025)
  except OSError:pass
 try:proc.wait(timeout=40)
 except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=10)
 raise
finally:
 hostlog.close()
