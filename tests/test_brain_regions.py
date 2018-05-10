import unittest
from io import StringIO
from nuggt import BrainRegions


class TestBrainRegions(unittest.TestCase):

    def test_parse(self):
        br = self.get_sample_br()

    def test_get_name(self):
        br = self.get_sample_br()
        self.assertEqual(br.get_name(4), "Inferior colliculus")
    def test_get_acronym(self):
        br = self.get_sample_br()
        self.assertEqual(br.get_acronym(7), "PSV")

    def test_get_hierarchy(self):
        br = self.get_sample_br()
        self.assertListEqual(br.get_hierarchy(0), ["background"])
        self.assertListEqual(
            br.get_hierarchy(4),
            ['Inferior colliculus', 'Midbrain, sensory related', 'Midbrain',
             'Brain stem'])

    def get_ids_for_region(self):
        br = self.get_sample_br()
        ids = self.get_ids_for_region("Brain stem")
        self.assertEqual(len(ids), 5)
        for iid in [1, 3, 5, 7, 8]:
            self.assertIn(iid, ids)

    def get_sample_br(self):
        return BrainRegions.parse(StringIO(sample_file))


sample_file = """id,counts,density,name,acronym
0,14362867.0,60432.9224521,b'background',b'background',b'background',b'background',b'background',b'background',b'background',b'background',b'background'
1,937.0,64000.0,"b'Tuberomammillary nucleus, ventral part'",b'TMv',"b'Tuberomammillary nucleus, ventral part'",b'Tuberomammillary nucleus',b'Mammillary body',b'Hypothalamic medial zone',b'Hypothalamus',b'Interbrain',b'Brain stem'
2,4058.0,64000.0,"b'Primary somatosensory area, mouth, layer 6b'",b'SSp-m6b',"b'Primary somatosensory area, mouth'",b'Primary somatosensory area',b'Somatosensory areas',b'Isocortex',b'Cortical plate',b'Cerebral cortex',b'Cerebrum'
4,178904.0,64000.0,b'Inferior colliculus',b'IC',b'Inferior colliculus',b'Inferior colliculus',b'Inferior colliculus',b'Inferior colliculus',"b'Midbrain, sensory related'",b'Midbrain',b'Brain stem'
6,77849.0,64000.0,b'internal capsule',b'int',b'internal capsule',b'internal capsule',b'internal capsule',b'internal capsule',b'internal capsule',b'corticospinal tract',b'lateral forebrain bundle system'
7,35174.0,64000.0,b'Principal sensory nucleus of the trigeminal',b'PSV',b'Principal sensory nucleus of the trigeminal',b'Principal sensory nucleus of the trigeminal',b'Principal sensory nucleus of the trigeminal',"b'Pons, sensory related'",b'Pons',b'Hindbrain',b'Brain stem'
9,5358.0,64000.0,"b'Primary somatosensory area, trunk, layer 6a'",b'SSp-tr6a',"b'Primary somatosensory area, trunk'",b'Primary somatosensory area',b'Somatosensory areas',b'Isocortex',b'Cortical plate',b'Cerebral cortex',b'Cerebrum'
10,66644.0,64000.0,"b'Superior colliculus, motor related, intermediate gray layer'",b'SCig',"b'Superior colliculus, motor related, intermediate gray layer'","b'Superior colliculus, motor related, intermediate gray layer'","b'Superior colliculus, motor related, intermediate gray layer'","b'Superior colliculus, motor related'","b'Midbrain, motor related'",b'Midbrain',b'Brain stem'
12,1051.0,64000.0,b'Interfascicular nucleus raphe',b'IF',b'Interfascicular nucleus raphe',b'Interfascicular nucleus raphe',b'Interfascicular nucleus raphe',b'Midbrain raphe nuclei',"b'Midbrain, behavioral state related'",b'Midbrain',b'Brain stem'
"""
if __name__ == '__main__':
    unittest.main()
