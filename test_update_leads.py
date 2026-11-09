import sys
import unittest
import datetime as dt
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from update_leads import normalize, category_for

class FeedTests(unittest.TestCase):
    def item(self,n,states=None,seen='2026-11-08T08:00:00Z'):
        return {'sku':str(1014000000+n),'name':'LED Work Light '+str(n),'states':states or {'TX':1},'tier':'hot','likelihood':'high','retail':99.97,'lastSeenAt':seen,'reports':n,'score':n,'internetNumber':'335347113','upc':'030878857260'}
    def test_state_ranking_and_no_local_guarantees(self):
        items=[self.item(n) for n in range(1,11)]+[self.item(15,{'AL':1})]
        cleaned=normalize(items,dt.datetime(2026,11,8,tzinfo=dt.timezone.utc))
        self.assertEqual(cleaned[0]['region'],'alabama')
        self.assertEqual(cleaned[0]['stateCounts']['AL'],1)
        self.assertNotIn('storePrice',cleaned[0]);self.assertNotIn('inStock',cleaned[0])
    def test_upc_and_missing_sentinels(self):
        items=[self.item(n) for n in range(1,12)]
        items[0]['upc']='$undefined';items[0]['internetNumber']='$undefined'
        out=normalize(items,dt.datetime(2026,11,8,tzinfo=dt.timezone.utc))
        first=next(x for x in out if x['sku']==items[0]['sku'])
        self.assertEqual(first['upc'],'');self.assertEqual(first['productUrl'],'')
    def test_stale_filtered(self):
        items=[self.item(n) for n in range(1,12)]
        items[0]['lastSeenAt']='2026-01-01'
        self.assertEqual(len(normalize(items,dt.datetime(2026,11,8,tzinfo=dt.timezone.utc))),10)

if __name__=='__main__':unittest.main()
