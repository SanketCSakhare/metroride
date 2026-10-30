import json,unittest
from pathlib import Path
class SnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.d=json.loads((Path(__file__).parents[1]/'dist/data.json').read_text())
    def test_totals_reconcile(self):
        d=self.d;m=d['meta'];self.assertEqual(m['raw_rows'],m['valid_rows']+m['excluded_rows']);self.assertEqual(sum(d['hourly']),m['valid_rows']);self.assertEqual(sum(map(sum,d['heatmap'])),m['valid_rows']);self.assertEqual(sum(z['n'] for z in d['zones']),m['valid_rows']);self.assertEqual(sum(x['n'] for x in d['daily']),m['valid_rows'])
    def test_routes_and_quantiles(self):
        d=self.d;self.assertEqual(len({(r['pu'],r['do']) for r in d['routes']}),len(d['routes']))
        for r in d['routes']:
            self.assertGreaterEqual(r['n'],30);self.assertLessEqual(r['low'],r['fare']);self.assertLessEqual(r['fare'],r['high']);self.assertTrue(1<=r['minutes']<=180)
    def test_dates_and_domain(self):
        self.assertEqual(len(self.d['daily']),31);self.assertEqual(len(self.d['hourly']),24);self.assertTrue(all(x['date'].startswith('2025-01-') for x in self.d['daily']))
if __name__=='__main__':unittest.main()
