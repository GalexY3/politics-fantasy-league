/**
 * Local-only PFL fictional pilot viewer. No collection, scoring, cookies or persistence.
 * NOT an approved human experiment and not a public server.
 */
import http from 'node:http';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {resolve} from 'node:path';
const dir=resolve(fileURLToPath(new URL('.', import.meta.url)));
const allow=new Map([
 ['/', ['index.html','text/html; charset=utf-8']],
 ['/index.html',['index.html','text/html; charset=utf-8']],
 ['/app.mjs',['app.mjs','text/javascript; charset=utf-8']],
 ['/style.css',['style.css','text/css; charset=utf-8']],
 ['/materials.mjs',['../src/politics_fantasy/fictional_transfer_items.mjs','text/javascript; charset=utf-8']]
]);
const headers={
 'Content-Security-Policy':"default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'none'; form-action 'none'; frame-ancestors 'none'; base-uri 'none'; object-src 'none'; img-src 'none'",
 'X-Content-Type-Options':'nosniff',
 'Referrer-Policy':'no-referrer',
 'Cache-Control':'no-store, max-age=0',
 'Permissions-Policy':'geolocation=(), microphone=(), camera=()',
 'X-Frame-Options':'DENY'
};
const server=http.createServer(async(req,res)=>{
 const method=req.method||'';
 if(method!=='GET'&&method!=='HEAD'){res.writeHead(405,{...headers,Allow:'GET, HEAD'});res.end();return}
 const hit=allow.get(req.url||'');
 if(!hit){res.writeHead(404,headers);res.end();return}
 try{
  const data=await readFile(resolve(dir,hit[0]));
  res.writeHead(200,{...headers,'Content-Type':hit[1],'Content-Length':data.byteLength});
  res.end(method==='HEAD'?undefined:data);
 }catch{
  res.writeHead(500,headers);res.end();
 }
});
server.requestTimeout=10000;
server.headersTimeout=10000;
server.listen(8787,'127.0.0.1',()=>console.log('PFL ficticio: http://127.0.0.1:8787 · SIN recogida de datos'));
export {server};
