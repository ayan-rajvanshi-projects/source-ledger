#!/usr/bin/env python3
"""Local-first public search evidence notebook. No external dependencies."""
import hashlib,json,os,sqlite3,time,urllib.request,urllib.parse
from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
DB=Path(__file__).with_name('.ledger-cache.sqlite3'); MAX_CALLS=200

def connect():
 c=sqlite3.connect(DB);c.execute('CREATE TABLE IF NOT EXISTS cache (query TEXT PRIMARY KEY, payload TEXT NOT NULL)');c.execute('CREATE TABLE IF NOT EXISTS budget (id INTEGER PRIMARY KEY CHECK(id=1), calls INTEGER NOT NULL)');c.execute('INSERT OR IGNORE INTO budget VALUES(1,0)');c.commit();return c

def search(q):
 key=os.environ.get('SERPAPI_KEY','').strip()
 if not key:raise ValueError('Set SERPAPI_KEY on the local server. No live search was run.')
 with connect() as c:
  calls=c.execute('SELECT calls FROM budget WHERE id=1').fetchone()[0]
  hit=c.execute('SELECT payload FROM cache WHERE query=?',(q,)).fetchone()
  if hit:return {**json.loads(hit[0]),'cached':True,'budget_used':calls,'budget_limit':MAX_CALLS}
  if calls>=MAX_CALLS:raise ValueError('Local 200-call safety cap reached. No paid overage attempted.')
  # Reserve before network I/O: failures also consume local budget, never auto-retry.
  c.execute('UPDATE budget SET calls=calls+1 WHERE id=1');c.commit();calls+=1
 url='https://serpapi.com/search.json?'+urllib.parse.urlencode({'engine':'google','q':q,'api_key':key,'num':10,'gl':'in','hl':'en'})
 try:
  with urllib.request.urlopen(url,timeout=25) as r:raw=json.load(r)
 except Exception:raise ValueError('Search provider failed or timed out. The attempt counts against the local safety cap. Check account status before retrying.') from None
 if raw.get('error'):raise ValueError('Search provider returned an error. Check your SerpApi account before retrying.')
 results=[]
 for x in raw.get('organic_results',[]):
  link=str(x.get('link',''));u=urllib.parse.urlparse(link)
  if u.scheme not in ('http','https') or not u.netloc:continue
  record={'title':str(x.get('title','')),'url':link,'domain':u.netloc.lower(),'snippet':str(x.get('snippet',''))}
  record['lead_hash']=hashlib.sha256(json.dumps(record,sort_keys=True).encode()).hexdigest();results.append(record)
 out={'query':q,'retrieved_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'search_id':raw.get('search_metadata',{}).get('id'),'engine':'google','results':results}
 with connect() as c:c.execute('INSERT OR REPLACE INTO cache VALUES (?,?)',(q,json.dumps(out)));c.commit()
 return {**out,'cached':False,'budget_used':calls,'budget_limit':MAX_CALLS}

class App(BaseHTTPRequestHandler):
 def send_json(self,status,out):
  b=json.dumps(out).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(b)
 def do_GET(self):
  if self.path=='/':
   b=Path(__file__).with_name('index.html').read_bytes();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write(b)
  elif self.path=='/health':
   with connect() as c:calls=c.execute('SELECT calls FROM budget WHERE id=1').fetchone()[0]
   self.send_json(200,{'key_configured':bool(os.environ.get('SERPAPI_KEY','').strip()),'budget_used':calls,'budget_limit':MAX_CALLS})
  else:self.send_error(404)
 def do_POST(self):
  if self.path!='/search':self.send_error(404);return
  # Browser Origin may be omitted by CLI clients, but reject foreign web origins.
  origin=self.headers.get('Origin','')
  if origin and origin not in ('http://127.0.0.1:8765','http://localhost:8765'):
   self.send_json(403,{'error':'Only the local notebook may request searches.'});return
  try:
   n=int(self.headers.get('Content-Length','0'))
   if n<=0 or n>10000:raise ValueError('Invalid request size')
   data=json.loads(self.rfile.read(n));q=str(data.get('q','')).strip()
   if not q or len(q)>240:raise ValueError('Enter a query under 240 characters')
   self.send_json(200,search(q))
  except (ValueError,json.JSONDecodeError) as e:self.send_json(400,{'error':str(e)})
  except Exception:self.send_json(500,{'error':'Local storage error. No automatic retry was made.'})
 def log_message(self,*args):pass  # Do not print user queries into access logs.
if __name__=='__main__':HTTPServer(('127.0.0.1',8765),App).serve_forever()
