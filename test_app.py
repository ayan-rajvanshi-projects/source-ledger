import unittest,io,os,json,tempfile,urllib.error
from pathlib import Path
from unittest.mock import patch
import app
FIX={'search_metadata':{'id':'fixture-only'},'organic_results':[{'title':'Fixture','link':'https://example.com/','snippet':'Fixture, not evidence'},{'title':'Bad URL','link':'javascript:alert(1)'}]}
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.db=patch.object(app,'DB',Path(self.tmp.name)/'db');self.db.start()
 def tearDown(self):self.db.stop();self.tmp.cleanup()
 def test_no_key_no_calls(self):
  with patch.dict(os.environ,{},clear=True):
   with self.assertRaises(ValueError):app.search('test')
  with app.connect() as c:self.assertEqual(c.execute('SELECT calls FROM budget').fetchone()[0],0)
 def test_persistent_cache(self):
  with patch.dict(os.environ,{'SERPAPI_KEY':'fixture-only'}),patch.object(app.urllib.request,'urlopen',return_value=io.BytesIO(json.dumps(FIX).encode())) as m:
   a=app.search('same');b=app.search('same');self.assertFalse(a['cached']);self.assertTrue(b['cached']);self.assertEqual(m.call_count,1);self.assertEqual(b['budget_used'],1);self.assertEqual(len(a['results']),1);self.assertEqual(len(a['results'][0]['lead_hash']),64)
 def test_cap_stops_network(self):
  with app.connect() as c:c.execute('UPDATE budget SET calls=200');c.commit()
  with patch.dict(os.environ,{'SERPAPI_KEY':'fixture-only'}),patch.object(app.urllib.request,'urlopen') as m:
   with self.assertRaises(ValueError):app.search('new')
   self.assertEqual(m.call_count,0)
 def test_provider_error_hides_key_and_counts_attempt(self):
  with patch.dict(os.environ,{'SERPAPI_KEY':'fixture-secret'}),patch.object(app.urllib.request,'urlopen',side_effect=Exception('https://provider/?api_key=fixture-secret')) as m:
   with self.assertRaises(ValueError) as e:app.search('fail')
   self.assertNotIn('fixture-secret',str(e.exception));self.assertEqual(m.call_count,1)
  with app.connect() as c:self.assertEqual(c.execute('SELECT calls FROM budget').fetchone()[0],1)
if __name__=='__main__':unittest.main()
