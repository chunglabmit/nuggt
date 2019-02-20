import unittest
from io import StringIO
from nuggt import BrainRegions


class TestBrainRegions(unittest.TestCase):

    def test_parse(self):
        br = self.get_sample_br()

    def test_get_name(self):
        br = self.get_sample_br()
        self.assertEqual(br.get_name(812), "Inferior colliculus")

    def test_get_acronym(self):
        br = self.get_sample_br()
        self.assertEqual(br.get_acronym(7), "FRP1")

    def test_get_hierarchy(self):
        br = self.get_sample_br()
        self.assertListEqual(
            br.get_hierarchy(812),
            ['Inferior colliculus', 'Midbrain, sensory related', 'Midbrain',
             'Brain stem', 'Basic cell groups and regions', 'root'])

    def get_sample_br(self):
        return BrainRegions.parse(StringIO(sample_file))


sample_file = """id,name,acronym,parent_structure_id,depth
0,"root","root",-1,0
1,"Basic cell groups and regions","grey",0,1
2,"Cerebrum","CH",1,2
3,"Cerebral cortex","CTX",2,3
4,"Cortical plate","CTXpl",3,4
5,"Isocortex","Isocortex",4,5
6,"Frontal pole, cerebral cortex","FRP",5,6
7,"Frontal pole, layer 1","FRP1",6,7
8,"Frontal pole, layer 2/3","FRP2/3",6,7
9,"Frontal pole, layer 5","FRP5",6,7
10,"Frontal pole, layer 6a","FRP6a",6,7
11,"Frontal pole, layer 6b","FRP6b",6,7
12,"Somatomotor areas","MO",5,6
13,"Somatomotor areas, Layer 1","MO1",12,7
14,"Somatomotor areas, Layer 2/3","MO2/3",12,7
15,"Somatomotor areas, Layer 5","MO5",12,7
16,"Somatomotor areas, Layer 6a","MO6a",12,7
17,"Somatomotor areas, Layer 6b","MO6b",12,7
18,"Primary motor area","MOp",12,7
19,"Primary motor area, Layer 1","MOp1",18,8
20,"Primary motor area, Layer 2/3","MOp2/3",18,8
21,"Primary motor area, Layer 5","MOp5",18,8
22,"Primary motor area, Layer 6a","MOp6a",18,8
23,"Primary motor area, Layer 6b","MOp6b",18,8
24,"Secondary motor area","MOs",12,7
25,"Secondary motor area, layer 1","MOs1",24,8
26,"Secondary motor area, layer 2/3","MOs2/3",24,8
27,"Secondary motor area, layer 5","MOs5",24,8
28,"Secondary motor area, layer 6a","MOs6a",24,8
29,"Secondary motor area, layer 6b","MOs6b",24,8
30,"Somatosensory areas","SS",5,6
31,"Somatosensory areas, layer 1","SS1",30,7
32,"Somatosensory areas, layer 2/3","SS2/3",30,7
33,"Somatosensory areas, layer 4","SS4",30,7
34,"Somatosensory areas, layer 5","SS5",30,7
35,"Somatosensory areas, layer 6a","SS6a",30,7
36,"Somatosensory areas, layer 6b","SS6b",30,7
37,"Primary somatosensory area","SSp",30,7
38,"Primary somatosensory area, layer 1","SSp1",37,8
39,"Primary somatosensory area, layer 2/3","SSp2/3",37,8
40,"Primary somatosensory area, layer 4","SSp4",37,8
41,"Primary somatosensory area, layer 5","SSp5",37,8
42,"Primary somatosensory area, layer 6a","SSp6a",37,8
43,"Primary somatosensory area, layer 6b","SSp6b",37,8
44,"Primary somatosensory area, nose","SSp-n",37,8
45,"Primary somatosensory area, nose, layer 1","SSp-n1",44,9
46,"Primary somatosensory area, nose, layer 2/3","SSp-n2/3",44,9
47,"Primary somatosensory area, nose, layer 4","SSp-n4",44,9
48,"Primary somatosensory area, nose, layer 5","SSp-n5",44,9
49,"Primary somatosensory area, nose, layer 6a","SSp-n6a",44,9
50,"Primary somatosensory area, nose, layer 6b","SSp-n6b",44,9
51,"Primary somatosensory area, barrel field","SSp-bfd",37,8
52,"Primary somatosensory area, barrel field, layer 1","SSp-bfd1",51,9
53,"Primary somatosensory area, barrel field, layer 2/3","SSp-bfd2/3",51,9
54,"Primary somatosensory area, barrel field, layer 4","SSp-bfd4",51,9
55,"Primary somatosensory area, barrel field, layer 5","SSp-bfd5",51,9
56,"Primary somatosensory area, barrel field, layer 6a","SSp-bfd6a",51,9
57,"Primary somatosensory area, barrel field, layer 6b","SSp-bfd6b",51,9
58,"Rostrolateral lateral visual area","VISrll",51,9
59,"Rostrolateral lateral visual area, layer 1","VISrll1",58,10
60,"Rostrolateral lateral visual area, layer 2/3","VISrll2/3",58,10
61,"Rostrolateral lateral visual area, layer 4","VISrll4",58,10
62,"Rostrolateral lateral visual area,layer 5","VISrll5",58,10
63,"Rostrolateral lateral visual area, layer 6a","VISrll6a",58,10
64,"Rostrolateral lateral visual area, layer 6b","VISrll6b",58,10
65,"Primary somatosensory area, lower limb","SSp-ll",37,8
66,"Primary somatosensory area, lower limb, layer 1","SSp-ll1",65,9
67,"Primary somatosensory area, lower limb, layer 2/3","SSp-ll2/3",65,9
68,"Primary somatosensory area, lower limb, layer 4","SSp-ll4",65,9
69,"Primary somatosensory area, lower limb, layer 5","SSp-ll5",65,9
70,"Primary somatosensory area, lower limb, layer 6a","SSp-ll6a",65,9
71,"Primary somatosensory area, lower limb, layer 6b","SSp-ll6b",65,9
72,"Primary somatosensory area, mouth","SSp-m",37,8
73,"Primary somatosensory area, mouth, layer 1","SSp-m1",72,9
74,"Primary somatosensory area, mouth, layer 2/3","SSp-m2/3",72,9
75,"Primary somatosensory area, mouth, layer 4","SSp-m4",72,9
76,"Primary somatosensory area, mouth, layer 5","SSp-m5",72,9
77,"Primary somatosensory area, mouth, layer 6a","SSp-m6a",72,9
78,"Primary somatosensory area, mouth, layer 6b","SSp-m6b",72,9
79,"Primary somatosensory area, upper limb","SSp-ul",37,8
80,"Primary somatosensory area, upper limb, layer 1","SSp-ul1",79,9
81,"Primary somatosensory area, upper limb, layer 2/3","SSp-ul2/3",79,9
82,"Primary somatosensory area, upper limb, layer 4","SSp-ul4",79,9
83,"Primary somatosensory area, upper limb, layer 5","SSp-ul5",79,9
84,"Primary somatosensory area, upper limb, layer 6a","SSp-ul6a",79,9
85,"Primary somatosensory area, upper limb, layer 6b","SSp-ul6b",79,9
86,"Primary somatosensory area, trunk","SSp-tr",37,8
87,"Primary somatosensory area, trunk, layer 1","SSp-tr1",86,9
88,"Primary somatosensory area, trunk, layer 2/3","SSp-tr2/3",86,9
89,"Primary somatosensory area, trunk, layer 4","SSp-tr4",86,9
90,"Primary somatosensory area, trunk, layer 5","SSp-tr5",86,9
91,"Primary somatosensory area, trunk, layer 6a","SSp-tr6a",86,9
92,"Primary somatosensory area, trunk, layer 6b","SSp-tr6b",86,9
93,"Primary somatosensory area, unassigned","SSp-un",37,8
94,"Primary somatosensory area, unassigned, layer 1","SSp-un1",93,9
95,"Primary somatosensory area, unassigned, layer 2/3","SSp-un2/3",93,9
96,"Primary somatosensory area, unassigned, layer 4","SSp-un4",93,9
97,"Primary somatosensory area, unassigned, layer 5","SSp-un5",93,9
98,"Primary somatosensory area, unassigned, layer 6a","SSp-un6a",93,9
99,"Primary somatosensory area, unassigned, layer 6b","SSp-un6b",93,9
100,"Supplemental somatosensory area","SSs",30,7
101,"Supplemental somatosensory area, layer 1","SSs1",100,8
102,"Supplemental somatosensory area, layer 2/3","SSs2/3",100,8
103,"Supplemental somatosensory area, layer 4","SSs4",100,8
104,"Supplemental somatosensory area, layer 5","SSs5",100,8
105,"Supplemental somatosensory area, layer 6a","SSs6a",100,8
106,"Supplemental somatosensory area, layer 6b","SSs6b",100,8
107,"Gustatory areas","GU",5,6
108,"Gustatory areas, layer 1","GU1",107,7
109,"Gustatory areas, layer 2/3","GU2/3",107,7
110,"Gustatory areas, layer 4","GU4",107,7
111,"Gustatory areas, layer 5","GU5",107,7
112,"Gustatory areas, layer 6a","GU6a",107,7
113,"Gustatory areas, layer 6b","GU6b",107,7
114,"Visceral area","VISC",5,6
115,"Visceral area, layer 1","VISC1",114,7
116,"Visceral area, layer 2/3","VISC2/3",114,7
117,"Visceral area, layer 4","VISC4",114,7
118,"Visceral area, layer 5","VISC5",114,7
119,"Visceral area, layer 6a","VISC6a",114,7
120,"Visceral area, layer 6b","VISC6b",114,7
121,"Auditory areas","AUD",5,6
122,"Dorsal auditory area","AUDd",121,7
123,"Dorsal auditory area, layer 1","AUDd1",122,8
124,"Dorsal auditory area, layer 2/3","AUDd2/3",122,8
125,"Dorsal auditory area, layer 4","AUDd4",122,8
126,"Dorsal auditory area, layer 5","AUDd5",122,8
127,"Dorsal auditory area, layer 6a","AUDd6a",122,8
128,"Dorsal auditory area, layer 6b","AUDd6b",122,8
129,"Laterolateral anterior visual area","VISlla",122,8
130,"Laterolateral anterior visual area, layer 1","VISlla1",129,9
131,"Laterolateral anterior visual area, layer 2/3","VISlla2/3",129,9
132,"Laterolateral anterior visual area, layer 4","VISlla4",129,9
133,"Laterolateral anterior visual area,layer 5","VISlla5",129,9
134,"Laterolateral anterior visual area, layer 6a","VISlla6a",129,9
135,"Laterolateral anterior visual area, layer 6b","VISlla6b",129,9
136,"Primary auditory area","AUDp",121,7
137,"Primary auditory area, layer 1","AUDp1",136,8
138,"Primary auditory area, layer 2/3","AUDp2/3",136,8
139,"Primary auditory area, layer 4","AUDp4",136,8
140,"Primary auditory area, layer 5","AUDp5",136,8
141,"Primary auditory area, layer 6a","AUDp6a",136,8
142,"Primary auditory area, layer 6b","AUDp6b",136,8
143,"Posterior auditory area","AUDpo",121,7
144,"Posterior auditory area, layer 1","AUDpo1",143,8
145,"Posterior auditory area, layer 2/3","AUDpo2/3",143,8
146,"Posterior auditory area, layer 4","AUDpo4",143,8
147,"Posterior auditory area, layer 5","AUDpo5",143,8
148,"Posterior auditory area, layer 6a","AUDpo6a",143,8
149,"Posterior auditory area, layer 6b","AUDpo6b",143,8
150,"Ventral auditory area","AUDv",121,7
151,"Ventral auditory area, layer 1","AUDv1",150,8
152,"Ventral auditory area, layer 2/3","AUDv2/3",150,8
153,"Ventral auditory area, layer 4","AUDv4",150,8
154,"Ventral auditory area, layer 5","AUDv5",150,8
155,"Ventral auditory area, layer 6a","AUDv6a",150,8
156,"Ventral auditory area, layer 6b","AUDv6b",150,8
157,"Visual areas","VIS",5,6
158,"Visual areas, layer 1","VIS1",157,7
159,"Visual areas, layer 2/3","VIS2/3",157,7
160,"Visual areas, layer 4","VIS4",157,7
161,"Visual areas, layer 5","VIS5",157,7
162,"Visual areas, layer 6a","VIS6a",157,7
163,"Visual areas, layer 6b","VIS6b",157,7
164,"Anterolateral visual area","VISal",157,7
165,"Anterolateral visual area, layer 1","VISal1",164,8
166,"Anterolateral visual area, layer 2/3","VISal2/3",164,8
167,"Anterolateral visual area, layer 4","VISal4",164,8
168,"Anterolateral visual area, layer 5","VISal5",164,8
169,"Anterolateral visual area, layer 6a","VISal6a",164,8
170,"Anterolateral visual area, layer 6b","VISal6b",164,8
171,"Anteromedial visual area","VISam",157,7
172,"Anteromedial visual area, layer 1","VISam1",171,8
173,"Anteromedial visual area, layer 2/3","VISam2/3",171,8
174,"Anteromedial visual area, layer 4","VISam4",171,8
175,"Anteromedial visual area, layer 5","VISam5",171,8
176,"Anteromedial visual area, layer 6a","VISam6a",171,8
177,"Anteromedial visual area, layer 6b","VISam6b",171,8
178,"Lateral visual area","VISl",157,7
179,"Lateral visual area, layer 1","VISl1",178,8
180,"Lateral visual area, layer 2/3","VISl2/3",178,8
181,"Lateral visual area, layer 4","VISl4",178,8
182,"Lateral visual area, layer 5","VISl5",178,8
183,"Lateral visual area, layer 6a","VISl6a",178,8
184,"Lateral visual area, layer 6b","VISl6b",178,8
185,"Primary visual area","VISp",157,7
186,"Primary visual area, layer 1","VISp1",185,8
187,"Primary visual area, layer 2/3","VISp2/3",185,8
188,"Primary visual area, layer 4","VISp4",185,8
189,"Primary visual area, layer 5","VISp5",185,8
190,"Primary visual area, layer 6a","VISp6a",185,8
191,"Primary visual area, layer 6b","VISp6b",185,8
192,"Posterolateral visual area","VISpl",157,7
193,"Posterolateral visual area, layer 1","VISpl1",192,8
194,"Posterolateral visual area, layer 2/3","VISpl2/3",192,8
195,"Posterolateral visual area, layer 4","VISpl4",192,8
196,"Posterolateral visual area, layer 5","VISpl5",192,8
197,"Posterolateral visual area, layer 6a","VISpl6a",192,8
198,"Posterolateral visual area, layer 6b","VISpl6b",192,8
199,"posteromedial visual area","VISpm",157,7
200,"posteromedial visual area, layer 1","VISpm1",199,8
201,"posteromedial visual area, layer 2/3","VISpm2/3",199,8
202,"posteromedial visual area, layer 4","VISpm4",199,8
203,"posteromedial visual area, layer 5","VISpm5",199,8
204,"posteromedial visual area, layer 6a","VISpm6a",199,8
205,"posteromedial visual area, layer 6b","VISpm6b",199,8
206,"Laterointermediate area","VISli",157,7
207,"Laterointermediate area, layer 1","VISli1",206,8
208,"Laterointermediate area, layer 2/3","VISli2/3",206,8
209,"Laterointermediate area, layer 4","VISli4",206,8
210,"Laterointermediate area, layer 5","VISli5",206,8
211,"Laterointermediate area, layer 6a","VISli6a",206,8
212,"Laterointermediate area, layer 6b","VISli6b",206,8
213,"Postrhinal area","VISpor",157,7
214,"Postrhinal area, layer 1","VISpor1",213,8
215,"Postrhinal area, layer 2/3","VISpor2/3",213,8
216,"Postrhinal area, layer 4","VISpor4",213,8
217,"Postrhinal area, layer 5","VISpor5",213,8
218,"Postrhinal area, layer 6a","VISpor6a",213,8
219,"Postrhinal area, layer 6b","VISpor6b",213,8
220,"Anterior cingulate area","ACA",5,6
221,"Anterior cingulate area, layer 1","ACA1",220,7
222,"Anterior cingulate area, layer 2/3","ACA2/3",220,7
223,"Anterior cingulate area, layer 5","ACA5",220,7
224,"Anterior cingulate area, layer 6a","ACA6a",220,7
225,"Anterior cingulate area, layer 6b","ACA6b",220,7
226,"Anterior cingulate area, dorsal part","ACAd",220,7
227,"Anterior cingulate area, dorsal part, layer 1","ACAd1",226,8
228,"Anterior cingulate area, dorsal part, layer 2/3","ACAd2/3",226,8
229,"Anterior cingulate area, dorsal part, layer 5","ACAd5",226,8
230,"Anterior cingulate area, dorsal part, layer 6a","ACAd6a",226,8
231,"Anterior cingulate area, dorsal part, layer 6b","ACAd6b",226,8
232,"Anterior cingulate area, ventral part","ACAv",220,7
233,"Anterior cingulate area, ventral part, layer 1","ACAv1",232,8
234,"Anterior cingulate area, ventral part, layer 2/3","ACAv2/3",232,8
235,"Anterior cingulate area, ventral part, layer 5","ACAv5",232,8
236,"Anterior cingulate area, ventral part, 6a","ACAv6a",232,8
237,"Anterior cingulate area, ventral part, 6b","ACAv6b",232,8
238,"Prelimbic area","PL",5,6
239,"Prelimbic area, layer 1","PL1",238,7
240,"Prelimbic area, layer 2","PL2",238,7
241,"Prelimbic area, layer 2/3","PL2/3",238,7
242,"Prelimbic area, layer 5","PL5",238,7
243,"Prelimbic area, layer 6a","PL6a",238,7
244,"Prelimbic area, layer 6b","PL6b",238,7
245,"Infralimbic area","ILA",5,6
246,"Infralimbic area, layer 1","ILA1",245,7
247,"Infralimbic area, layer 2","ILA2",245,7
248,"Infralimbic area, layer 2/3","ILA2/3",245,7
249,"Infralimbic area, layer 5","ILA5",245,7
250,"Infralimbic area, layer 6a","ILA6a",245,7
251,"Infralimbic area, layer 6b","ILA6b",245,7
252,"Orbital area","ORB",5,6
253,"Orbital area, layer 1","ORB1",252,7
254,"Orbital area, layer 2/3","ORB2/3",252,7
255,"Orbital area, layer 5","ORB5",252,7
256,"Orbital area, layer 6a","ORB6a",252,7
257,"Orbital area, layer 6b","ORB6b",252,7
258,"Orbital area, lateral part","ORBl",252,7
259,"Orbital area, lateral part, layer 1","ORBl1",258,8
260,"Orbital area, lateral part, layer 2/3","ORBl2/3",258,8
261,"Orbital area, lateral part, layer 5","ORBl5",258,8
262,"Orbital area, lateral part, layer 6a","ORBl6a",258,8
263,"Orbital area, lateral part, layer 6b","ORBl6b",258,8
264,"Orbital area, medial part","ORBm",252,7
265,"Orbital area, medial part, layer 1","ORBm1",264,8
266,"Orbital area, medial part, layer 2","ORBm2",264,8
267,"Orbital area, medial part, layer 2/3","ORBm2/3",264,8
268,"Orbital area, medial part, layer 5","ORBm5",264,8
269,"Orbital area, medial part, layer 6a","ORBm6a",264,8
270,"Orbital area, medial part, layer 6b","ORBm6b",264,8
271,"Orbital area, ventral part","ORBv",252,7
272,"Orbital area, ventrolateral part","ORBvl",252,7
273,"Orbital area, ventrolateral part, layer 1","ORBvl1",272,8
274,"Orbital area, ventrolateral part, layer 2/3","ORBvl2/3",272,8
275,"Orbital area, ventrolateral part, layer 5","ORBvl5",272,8
276,"Orbital area, ventrolateral part, layer 6a","ORBvl6a",272,8
277,"Orbital area, ventrolateral part, layer 6b","ORBvl6b",272,8
278,"Agranular insular area","AI",5,6
279,"Agranular insular area, dorsal part","AId",278,7
280,"Agranular insular area, dorsal part, layer 1","AId1",279,8
281,"Agranular insular area, dorsal part, layer 2/3","AId2/3",279,8
282,"Agranular insular area, dorsal part, layer 5","AId5",279,8
283,"Agranular insular area, dorsal part, layer 6a","AId6a",279,8
284,"Agranular insular area, dorsal part, layer 6b","AId6b",279,8
285,"Agranular insular area, posterior part","AIp",278,7
286,"Agranular insular area, posterior part, layer 1","AIp1",285,8
287,"Agranular insular area, posterior part, layer 2/3","AIp2/3",285,8
288,"Agranular insular area, posterior part, layer 5","AIp5",285,8
289,"Agranular insular area, posterior part, layer 6a","AIp6a",285,8
290,"Agranular insular area, posterior part, layer 6b","AIp6b",285,8
291,"Agranular insular area, ventral part","AIv",278,7
292,"Agranular insular area, ventral part, layer 1","AIv1",291,8
293,"Agranular insular area, ventral part, layer 2/3","AIv2/3",291,8
294,"Agranular insular area, ventral part, layer 5","AIv5",291,8
295,"Agranular insular area, ventral part, layer 6a","AIv6a",291,8
296,"Agranular insular area, ventral part, layer 6b","AIv6b",291,8
297,"Retrosplenial area","RSP",5,6
298,"Retrosplenial area, lateral agranular part","RSPagl",297,7
299,"Retrosplenial area, lateral agranular part, layer 1","RSPagl1",298,8
300,"Retrosplenial area, lateral agranular part, layer 2/3","RSPagl2/3",298,8
301,"Retrosplenial area, lateral agranular part, layer 5","RSPagl5",298,8
302,"Retrosplenial area, lateral agranular part, layer 6a","RSPagl6a",298,8
303,"Retrosplenial area, lateral agranular part, layer 6b","RSPagl6b",298,8
304,"Mediomedial anterior visual area","VISmma",298,8
305,"Mediomedial anterior visual area, layer 1","VISmma1",304,9
306,"Mediomedial anterior visual area, layer 2/3","VISmma2/3",304,9
307,"Mediomedial anterior visual area, layer 4","VISmma4",304,9
308,"Mediomedial anterior visual area,layer 5","VISmma5",304,9
309,"Mediomedial anterior visual area, layer 6a","VISmma6a",304,9
310,"Mediomedial anterior visual area, layer 6b","VISmma6b",304,9
311,"Mediomedial posterior visual area","VISmmp",298,8
312,"Mediomedial posterior visual area, layer 1","VISmmp1",311,9
313,"Mediomedial posterior visual area, layer 2/3","VISmmp2/3",311,9
314,"Mediomedial posterior visual area, layer 4","VISmmp4",311,9
315,"Mediomedial posterior visual area,layer 5","VISmmp5",311,9
316,"Mediomedial posterior visual area, layer 6a","VISmmp6a",311,9
317,"Mediomedial posterior visual area, layer 6b","VISmmp6b",311,9
318,"Medial visual area","VISm",298,8
319,"Medial visual area, layer 1","VISm1",318,9
320,"Medial visual area, layer 2/3","VISm2/3",318,9
321,"Medial visual area, layer 4","VISm4",318,9
322,"Medial visual area,layer 5","VISm5",318,9
323,"Medial visual area, layer 6a","VISm6a",318,9
324,"Medial visual area, layer 6b","VISm6b",318,9
325,"Retrosplenial area, dorsal part","RSPd",297,7
326,"Retrosplenial area, dorsal part, layer 1","RSPd1",325,8
327,"Retrosplenial area, dorsal part, layer 2/3","RSPd2/3",325,8
328,"Retrosplenial area, dorsal part, layer 4","RSPd4",325,8
329,"Retrosplenial area, dorsal part, layer 5","RSPd5",325,8
330,"Retrosplenial area, dorsal part, layer 6a","RSPd6a",325,8
331,"Retrosplenial area, dorsal part, layer 6b","RSPd6b",325,8
332,"Retrosplenial area, ventral part","RSPv",297,7
333,"Retrosplenial area, ventral part, layer 1","RSPv1",332,8
334,"Retrosplenial area, ventral part, layer 2","RSPv2",332,8
335,"Retrosplenial area, ventral part, layer 2/3","RSPv2/3",332,8
336,"Retrosplenial area, ventral part, layer 5","RSPv5",332,8
337,"Retrosplenial area, ventral part, layer 6a","RSPv6a",332,8
338,"Retrosplenial area, ventral part, layer 6b","RSPv6b",332,8
339,"Posterior parietal association areas","PTLp",5,6
340,"Posterior parietal association areas, layer 1","PTLp1",339,7
341,"Posterior parietal association areas, layer 2/3","PTLp2/3",339,7
342,"Posterior parietal association areas, layer 4","PTLp4",339,7
343,"Posterior parietal association areas, layer 5","PTLp5",339,7
344,"Posterior parietal association areas, layer 6a","PTLp6a",339,7
345,"Posterior parietal association areas, layer 6b","PTLp6b",339,7
346,"Anterior area","VISa",339,7
347,"Anterior area, layer 1","VISa1",346,8
348,"Anterior area, layer 2/3","VISa2/3",346,8
349,"Anterior area, layer 4","VISa4",346,8
350,"Anterior area, layer 5","VISa5",346,8
351,"Anterior area, layer 6a","VISa6a",346,8
352,"Anterior area, layer 6b","VISa6b",346,8
353,"Rostrolateral visual area","VISrl",339,7
354,"Rostrolateral area, layer 1","VISrl1",353,8
355,"Rostrolateral area, layer 2/3","VISrl2/3",353,8
356,"Rostrolateral area, layer 4","VISrl4",353,8
357,"Rostrolateral area, layer 5","VISrl5",353,8
358,"Rostrolateral area, layer 6a","VISrl6a",353,8
359,"Rostrolateral area, layer 6b","VISrl6b",353,8
360,"Temporal association areas","TEa",5,6
361,"Temporal association areas, layer 1","TEa1",360,7
362,"Temporal association areas, layer 2/3","TEa2/3",360,7
363,"Temporal association areas, layer 4","TEa4",360,7
364,"Temporal association areas, layer 5","TEa5",360,7
365,"Temporal association areas, layer 6a","TEa6a",360,7
366,"Temporal association areas, layer 6b","TEa6b",360,7
367,"Perirhinal area","PERI",5,6
368,"Perirhinal area, layer 1","PERI1",367,7
369,"Perirhinal area, layer 2/3","PERI2/3",367,7
370,"Perirhinal area, layer 5","PERI5",367,7
371,"Perirhinal area, layer 6a","PERI6a",367,7
372,"Perirhinal area, layer 6b","PERI6b",367,7
373,"Ectorhinal area","ECT",5,6
374,"Ectorhinal area/Layer 1","ECT1",373,7
375,"Ectorhinal area/Layer 2/3","ECT2/3",373,7
376,"Ectorhinal area/Layer 5","ECT5",373,7
377,"Ectorhinal area/Layer 6a","ECT6a",373,7
378,"Ectorhinal area/Layer 6b","ECT6b",373,7
379,"Olfactory areas","OLF",4,5
380,"Main olfactory bulb","MOB",379,6
381,"Main olfactory bulb, glomerular layer","MOBgl",380,7
382,"Main olfactory bulb, granule layer","MOBgr",380,7
383,"Main olfactory bulb, inner plexiform layer","MOBipl",380,7
384,"Main olfactory bulb, mitral layer","MOBmi",380,7
385,"Main olfactory bulb, outer plexiform layer","MOBopl",380,7
386,"Accessory olfactory bulb","AOB",379,6
387,"Accessory olfactory bulb, glomerular layer","AOBgl",386,7
388,"Accessory olfactory bulb, granular layer","AOBgr",386,7
389,"Accessory olfactory bulb, mitral layer","AOBmi",386,7
390,"Anterior olfactory nucleus","AON",379,6
391,"Anterior olfactory nucleus, dorsal part","AONd",390,7
392,"Anterior olfactory nucleus, external part","AONe",390,7
393,"Anterior olfactory nucleus, lateral part","AONl",390,7
394,"Anterior olfactory nucleus, medial part","AONm",390,7
395,"Anterior olfactory nucleus, posteroventral part","AONpv",390,7
396,"Anterior olfactory nucleus, layer 1","AON1",390,7
397,"Anterior olfactory nucleus, layer 2","AON2",390,7
398,"Taenia tecta","TT",379,6
399,"Taenia tecta, dorsal part","TTd",398,7
400,"Taenia tecta, dorsal part, layers 1-4","TTd1-4",399,8
401,"Taenia tecta, dorsal part, layer 1","TTd1",399,8
402,"Taenia tecta, dorsal part, layer 2","TTd2",399,8
403,"Taenia tecta, dorsal part, layer 3","TTd3",399,8
404,"Taenia tecta, dorsal part, layer 4","TTd4",399,8
405,"Taenia tecta, ventral part","TTv",398,7
406,"Taenia tecta, ventral part, layers 1-3","TTv1-3",405,8
407,"Taenia tecta, ventral part, layer 1","TTv1",405,8
408,"Taenia tecta, ventral part, layer 2","TTv2",405,8
409,"Taenia tecta, ventral part, layer 3","TTv3",405,8
410,"Dorsal peduncular area","DP",379,6
411,"Dorsal peduncular area, layer 1","DP1",410,7
412,"Dorsal peduncular area, layer 2","DP2",410,7
413,"Dorsal peduncular area, layer 2/3","DP2/3",410,7
414,"Dorsal peduncular area, layer 5","DP5",410,7
415,"Dorsal peduncular area, layer 6a","DP6a",410,7
416,"Piriform area","PIR",379,6
417,"Piriform area, layers 1-3","PIR1-3",416,7
418,"Piriform area, molecular layer","PIR1",416,7
419,"Piriform area, pyramidal layer","PIR2",416,7
420,"Piriform area, polymorph layer","PIR3",416,7
421,"Nucleus of the lateral olfactory tract","NLOT",379,6
422,"Nucleus of the lateral olfactory tract, layers 1-3","NLOT1-3",421,7
423,"Nucleus of the lateral olfactory tract, molecular layer","NLOT1",421,7
424,"Nucleus of the lateral olfactory tract, pyramidal layer","NLOT2",421,7
425,"Nucleus of the lateral olfactory tract, layer 3","NLOT3",421,7
426,"Cortical amygdalar area","COA",379,6
427,"Cortical amygdalar area, anterior part","COAa",426,7
428,"Cortical amygdalar area, anterior part, layer 1","COAa1",427,8
429,"Cortical amygdalar area, anterior part, layer 2","COAa2",427,8
430,"Cortical amygdalar area, anterior part, layer 3","COAa3",427,8
431,"Cortical amygdalar area, posterior part","COAp",426,7
432,"Cortical amygdalar area, posterior part, lateral zone","COApl",431,8
433,"Cortical amygdalar area, posterior part, lateral zone, layers 1-2","COApl1-2",432,9
434,"Cortical amygdalar area, posterior part, lateral zone, layers 1-3","COApl1-3",432,9
435,"Cortical amygdalar area, posterior part, lateral zone, layer 1","COApl1",432,9
436,"Cortical amygdalar area, posterior part, lateral zone, layer 2","COApl2",432,9
437,"Cortical amygdalar area, posterior part, lateral zone, layer 3","COApl3",432,9
438,"Cortical amygdalar area, posterior part, medial zone","COApm",431,8
439,"Cortical amygdalar area, posterior part, medial zone, layers 1-2","COApm1-2",438,9
440,"Cortical amygdalar area, posterior part, medial zone, layers 1-3","COApm1-3",438,9
441,"Cortical amygdalar area, posterior part, medial zone, layer 1","COApm1",438,9
442,"Cortical amygdalar area, posterior part, medial zone, layer 2","COApm2",438,9
443,"Cortical amygdalar area, posterior part, medial zone, layer 3","COApm3",438,9
444,"Piriform-amygdalar area","PAA",379,6
445,"Piriform-amygdalar area, layers 1-3","PAA1-3",444,7
446,"Piriform-amygdalar area, molecular layer","PAA1",444,7
447,"Piriform-amygdalar area, pyramidal layer","PAA2",444,7
448,"Piriform-amygdalar area, polymorph layer","PAA3",444,7
449,"Postpiriform transition area","TR",379,6
450,"Postpiriform transition area, layers 1-3","TR1-3",449,7
451,"Postpiriform transition area, layers 1","TR1",449,7
452,"Postpiriform transition area, layers 2","TR2",449,7
453,"Postpiriform transition area, layers 3","TR3",449,7
454,"Hippocampal formation","HPF",4,5
455,"Hippocampal region","HIP",454,6
456,"Ammon's horn","CA",455,7
457,"Field CA1","CA1",456,8
458,"Field CA1, stratum lacunosum-moleculare","CA1slm",457,9
459,"Field CA1, stratum oriens","CA1so",457,9
460,"Field CA1, pyramidal layer","CA1sp",457,9
461,"Field CA1, stratum radiatum","CA1sr",457,9
462,"Field CA2","CA2",456,8
463,"Field CA2, stratum lacunosum-moleculare","CA2slm",462,9
464,"Field CA2, stratum oriens","CA2so",462,9
465,"Field CA2, pyramidal layer","CA2sp",462,9
466,"Field CA2, stratum radiatum","CA2sr",462,9
467,"Field CA3","CA3",456,8
468,"Field CA3, stratum lacunosum-moleculare","CA3slm",467,9
469,"Field CA3, stratum lucidum","CA3slu",467,9
470,"Field CA3, stratum oriens","CA3so",467,9
471,"Field CA3, pyramidal layer","CA3sp",467,9
472,"Field CA3, stratum radiatum","CA3sr",467,9
473,"Dentate gyrus","DG",455,7
474,"Dentate gyrus, molecular layer","DG-mo",473,8
475,"Dentate gyrus, polymorph layer","DG-po",473,8
476,"Dentate gyrus, granule cell layer","DG-sg",473,8
477,"Dentate gyrus, subgranular zone","DG-sgz",473,8
478,"Dentate gyrus crest","DGcr",473,8
479,"Dentate gyrus crest, molecular layer","DGcr-mo",478,9
480,"Dentate gyrus crest, polymorph layer","DGcr-po",478,9
481,"Dentate gyrus crest, granule cell layer","DGcr-sg",478,9
482,"Dentate gyrus lateral blade","DGlb",473,8
483,"Dentate gyrus lateral blade, molecular layer","DGlb-mo",482,9
484,"Dentate gyrus lateral blade, polymorph layer","DGlb-po",482,9
485,"Dentate gyrus lateral blade, granule cell layer","DGlb-sg",482,9
486,"Dentate gyrus medial blade","DGmb",473,8
487,"Dentate gyrus medial blade, molecular layer","DGmb-mo",486,9
488,"Dentate gyrus medial blade, polymorph layer","DGmb-po",486,9
489,"Dentate gyrus medial blade, granule cell layer","DGmb-sg",486,9
490,"Fasciola cinerea","FC",455,7
491,"Induseum griseum","IG",455,7
492,"Retrohippocampal region","RHP",454,6
493,"Entorhinal area","ENT",492,7
494,"Entorhinal area, lateral part","ENTl",493,8
495,"Entorhinal area, lateral part, layer 1","ENTl1",494,9
496,"Entorhinal area, lateral part, layer 2","ENTl2",494,9
497,"Entorhinal area, lateral part, layer 2/3","ENTl2/3",494,9
498,"Entorhinal area, lateral part, layer 2a","ENTl2a",494,9
499,"Entorhinal area, lateral part, layer 2b","ENTl2b",494,9
500,"Entorhinal area, lateral part, layer 3","ENTl3",494,9
501,"Entorhinal area, lateral part, layer 4","ENTl4",494,9
502,"Entorhinal area, lateral part, layer 4/5","ENTl4/5",494,9
503,"Entorhinal area, lateral part, layer 5","ENTl5",494,9
504,"Entorhinal area, lateral part, layer 5/6","ENTl5/6",494,9
505,"Entorhinal area, lateral part, layer 6a","ENTl6a",494,9
506,"Entorhinal area, lateral part, layer 6b","ENTl6b",494,9
507,"Entorhinal area, medial part, dorsal zone","ENTm",493,8
508,"Entorhinal area, medial part, dorsal zone, layer 1","ENTm1",507,9
509,"Entorhinal area, medial part, dorsal zone, layer 2","ENTm2",507,9
510,"Entorhinal area, medial part, dorsal zone, layer 2a","ENTm2a",507,9
511,"Entorhinal area, medial part, dorsal zone, layer 2b","ENTm2b",507,9
512,"Entorhinal area, medial part, dorsal zone, layer 3","ENTm3",507,9
513,"Entorhinal area, medial part, dorsal zone, layer 4","ENTm4",507,9
514,"Entorhinal area, medial part, dorsal zone, layer 5","ENTm5",507,9
515,"Entorhinal area, medial part, dorsal zone, layer 5/6","ENTm5/6",507,9
516,"Entorhinal area, medial part, dorsal zone, layer 6","ENTm6",507,9
517,"Entorhinal area, medial part, ventral zone","ENTmv",493,8
518,"Entorhinal area, medial part, ventral zone, layer 1","ENTmv1",517,9
519,"Entorhinal area, medial part, ventral zone, layer 2","ENTmv2",517,9
520,"Entorhinal area, medial part, ventral zone, layer 3","ENTmv3",517,9
521,"Entorhinal area, medial part, ventral zone, layer 4","ENTmv4",517,9
522,"Entorhinal area, medial part, ventral zone, layer 5/6","ENTmv5/6",517,9
523,"Parasubiculum","PAR",492,7
524,"Parasubiculum, layer 1","PAR1",523,8
525,"Parasubiculum, layer 2","PAR2",523,8
526,"Parasubiculum, layer 3","PAR3",523,8
527,"Postsubiculum","POST",492,7
528,"Postsubiculum, layer 1","POST1",527,8
529,"Postsubiculum, layer 2","POST2",527,8
530,"Postsubiculum, layer 3","POST3",527,8
531,"Presubiculum","PRE",492,7
532,"Presubiculum, layer 1","PRE1",531,8
533,"Presubiculum, layer 2","PRE2",531,8
534,"Presubiculum, layer 3","PRE3",531,8
535,"Subiculum","SUB",492,7
536,"Subiculum, dorsal part","SUBd",535,8
537,"Subiculum, dorsal part, molecular layer","SUBd-m",536,9
538,"Subiculum, dorsal part, pyramidal layer","SUBd-sp",536,9
539,"Subiculum, dorsal part, stratum radiatum","SUBd-sr",536,9
540,"Subiculum, ventral part","SUBv",535,8
541,"Subiculum, ventral part, molecular layer","SUBv-m",540,9
542,"Subiculum, ventral part, pyramidal layer","SUBv-sp",540,9
543,"Subiculum, ventral part, stratum radiatum","SUBv-sr",540,9
544,"Prosubiculum","ProS",492,7
545,"Prosubiculum, dorsal part","ProSd",544,8
546,"Prosubiculum, dorsal part, molecular layer","ProSd-m",545,9
547,"Prosubiculum, dorsal part, pyramidal layer","ProSd-sp",545,9
548,"Prosubiculum, dorsal part, stratum radiatum","ProSd-sr",545,9
549,"Prosubiculum, ventral part","ProSv",544,8
550,"Prosubiculum, ventral part, molecular layer","ProSv-m",549,9
551,"Prosubiculum, ventral part, pyramidal layer","ProSv-sp",549,9
552,"Prosubiculum, ventral part, stratum radiatum","Prosv-sr",549,9
553,"Hippocampo-amygdalar transition area","HATA",492,7
554,"Area prostriata","APr",492,7
555,"Cortical subplate","CTXsp",3,4
556,"Layer 6b, isocortex","6b",555,5
557,"Claustrum","CLA",555,5
558,"Endopiriform nucleus","EP",555,5
559,"Endopiriform nucleus, dorsal part","EPd",558,6
560,"Endopiriform nucleus, ventral part","EPv",558,6
561,"Lateral amygdalar nucleus","LA",555,5
562,"Basolateral amygdalar nucleus","BLA",555,5
563,"Basolateral amygdalar nucleus, anterior part","BLAa",562,6
564,"Basolateral amygdalar nucleus, posterior part","BLAp",562,6
565,"Basolateral amygdalar nucleus, ventral part","BLAv",562,6
566,"Basomedial amygdalar nucleus","BMA",555,5
567,"Basomedial amygdalar nucleus, anterior part","BMAa",566,6
568,"Basomedial amygdalar nucleus, posterior part","BMAp",566,6
569,"Posterior amygdalar nucleus","PA",555,5
570,"Cerebral nuclei","CNU",2,3
571,"Striatum","STR",570,4
572,"Striatum dorsal region","STRd",571,5
573,"Caudoputamen","CP",572,6
574,"Striatum ventral region","STRv",571,5
575,"Nucleus accumbens","ACB",574,6
576,"Fundus of striatum","FS",574,6
577,"Olfactory tubercle","OT",574,6
578,"Islands of Calleja","isl",577,7
579,"Major island of Calleja","islm",577,7
580,"Olfactory tubercle, layers 1-3","OT1-3",577,7
581,"Olfactory tubercle, molecular layer","OT1",577,7
582,"Olfactory tubercle, pyramidal layer","OT2",577,7
583,"Olfactory tubercle, polymorph layer","OT3",577,7
584,"Lateral strip of striatum","LSS",574,6
585,"Lateral septal complex","LSX",571,5
586,"Lateral septal nucleus","LS",585,6
587,"Lateral septal nucleus, caudal (caudodorsal) part","LSc",586,7
588,"Lateral septal nucleus, rostral (rostroventral) part","LSr",586,7
589,"Lateral septal nucleus, ventral part","LSv",586,7
590,"Septofimbrial nucleus","SF",585,6
591,"Septohippocampal nucleus","SH",585,6
592,"Striatum-like amygdalar nuclei","sAMY",571,5
593,"Anterior amygdalar area","AAA",592,6
594,"Bed nucleus of the accessory olfactory tract","BA",592,6
595,"Central amygdalar nucleus","CEA",592,6
596,"Central amygdalar nucleus, capsular part","CEAc",595,7
597,"Central amygdalar nucleus, lateral part","CEAl",595,7
598,"Central amygdalar nucleus, medial part","CEAm",595,7
599,"Intercalated amygdalar nucleus","IA",592,6
600,"Medial amygdalar nucleus","MEA",592,6
601,"Medial amygdalar nucleus, anterodorsal part","MEAad",600,7
602,"Medial amygdalar nucleus, anteroventral part","MEAav",600,7
603,"Medial amygdalar nucleus, posterodorsal part","MEApd",600,7
604,"Medial amygdalar nucleus, posterodorsal part, sublayer a","MEApd-a",603,8
605,"Medial amygdalar nucleus, posterodorsal part, sublayer b","MEApd-b",603,8
606,"Medial amygdalar nucleus, posterodorsal part, sublayer c","MEApd-c",603,8
607,"Medial amygdalar nucleus, posteroventral part","MEApv",600,7
608,"Pallidum","PAL",570,4
609,"Pallidum, dorsal region","PALd",608,5
610,"Globus pallidus, external segment","GPe",609,6
611,"Globus pallidus, internal segment","GPi",609,6
612,"Pallidum, ventral region","PALv",608,5
613,"Substantia innominata","SI",612,6
614,"Magnocellular nucleus","MA",612,6
615,"Pallidum, medial region","PALm",608,5
616,"Medial septal complex","MSC",615,6
617,"Medial septal nucleus","MS",616,7
618,"Diagonal band nucleus","NDB",616,7
619,"Triangular nucleus of septum","TRS",615,6
620,"Pallidum, caudal region","PALc",608,5
621,"Bed nuclei of the stria terminalis","BST",620,6
622,"Bed nuclei of the stria terminalis, anterior division","BSTa",621,7
623,"Bed nuclei of the stria terminalis, anterior division, anterolateral area","BSTal",622,8
624,"Bed nuclei of the stria terminalis, anterior division, anteromedial area","BSTam",622,8
625,"Bed nuclei of the stria terminalis, anterior division, dorsomedial nucleus","BSTdm",622,8
626,"Bed nuclei of the stria terminalis, anterior division, fusiform nucleus","BSTfu",622,8
627,"Bed nuclei of the stria terminalis, anterior division, juxtacapsular nucleus","BSTju",622,8
628,"Bed nuclei of the stria terminalis, anterior division, magnocellular nucleus","BSTmg",622,8
629,"Bed nuclei of the stria terminalis, anterior division, oval nucleus","BSTov",622,8
630,"Bed nuclei of the stria terminalis, anterior division, rhomboid nucleus","BSTrh",622,8
631,"Bed nuclei of the stria terminalis, anterior division, ventral nucleus","BSTv",622,8
632,"Bed nuclei of the stria terminalis, posterior division","BSTp",621,7
633,"Bed nuclei of the stria terminalis, posterior division, dorsal nucleus","BSTd",632,8
634,"Bed nuclei of the stria terminalis, posterior division, principal nucleus","BSTpr",632,8
635,"Bed nuclei of the stria terminalis, posterior division, interfascicular nucleus","BSTif",632,8
636,"Bed nuclei of the stria terminalis, posterior division, transverse nucleus","BSTtr",632,8
637,"Bed nuclei of the stria terminalis, posterior division, strial extension","BSTse",632,8
638,"Bed nucleus of the anterior commissure","BAC",620,6
639,"Brain stem","BS",1,2
640,"Interbrain","IB",639,3
641,"Thalamus","TH",640,4
642,"Thalamus, sensory-motor cortex related","DORsm",641,5
643,"Ventral group of the dorsal thalamus","VENT",642,6
644,"Ventral anterior-lateral complex of the thalamus","VAL",643,7
645,"Ventral medial nucleus of the thalamus","VM",643,7
646,"Ventral posterior complex of the thalamus","VP",643,7
647,"Ventral posterolateral nucleus of the thalamus","VPL",646,8
648,"Ventral posterolateral nucleus of the thalamus, parvicellular part","VPLpc",646,8
649,"Ventral posteromedial nucleus of the thalamus","VPM",646,8
650,"Ventral posteromedial nucleus of the thalamus, parvicellular part","VPMpc",646,8
651,"Posterior triangular thalamic nucleus","PoT",643,7
652,"Subparafascicular nucleus","SPF",642,6
653,"Subparafascicular nucleus, magnocellular part","SPFm",652,7
654,"Subparafascicular nucleus, parvicellular part","SPFp",652,7
655,"Subparafascicular area","SPA",642,6
656,"Peripeduncular nucleus","PP",642,6
657,"Geniculate group, dorsal thalamus","GENd",642,6
658,"Medial geniculate complex","MG",657,7
659,"Medial geniculate complex, dorsal part","MGd",658,8
660,"Medial geniculate complex, ventral part","MGv",658,8
661,"Medial geniculate complex, medial part","MGm",658,8
662,"Dorsal part of the lateral geniculate complex","LGd",657,7
663,"Dorsal part of the lateral geniculate complex, shell","LGd-sh",662,8
664,"Dorsal part of the lateral geniculate complex, core","LGd-co",662,8
665,"Dorsal part of the lateral geniculate complex, ipsilateral zone","LGd-ip",662,8
666,"Thalamus, polymodal association cortex related","DORpm",641,5
667,"Lateral group of the dorsal thalamus","LAT",666,6
668,"Lateral posterior nucleus of the thalamus","LP",667,7
669,"Posterior complex of the thalamus","PO",667,7
670,"Posterior limiting nucleus of the thalamus","POL",667,7
671,"Suprageniculate nucleus","SGN",667,7
672,"Ethmoid nucleus of the thalamus","Eth",667,7
673,"Retroethmoid nucleus","REth",667,7
674,"Anterior group of the dorsal thalamus","ATN",666,6
675,"Anteroventral nucleus of thalamus","AV",674,7
676,"Anteromedial nucleus","AM",674,7
677,"Anteromedial nucleus, dorsal part","AMd",676,8
678,"Anteromedial nucleus, ventral part","AMv",676,8
679,"Anterodorsal nucleus","AD",674,7
680,"Interanteromedial nucleus of the thalamus","IAM",674,7
681,"Interanterodorsal nucleus of the thalamus","IAD",674,7
682,"Lateral dorsal nucleus of thalamus","LD",674,7
683,"Medial group of the dorsal thalamus","MED",666,6
684,"Intermediodorsal nucleus of the thalamus","IMD",683,7
685,"Mediodorsal nucleus of thalamus","MD",683,7
686,"Mediodorsal nucleus of the thalamus, central part","MDc",685,8
687,"Mediodorsal nucleus of the thalamus, lateral part","MDl",685,8
688,"Mediodorsal nucleus of the thalamus, medial part","MDm",685,8
689,"Submedial nucleus of the thalamus","SMT",683,7
690,"Perireunensis nucleus","PR",683,7
691,"Midline group of the dorsal thalamus","MTN",666,6
692,"Paraventricular nucleus of the thalamus","PVT",691,7
693,"Parataenial nucleus","PT",691,7
694,"Nucleus of reuniens","RE",691,7
695,"Xiphoid thalamic nucleus","Xi",691,7
696,"Intralaminar nuclei of the dorsal thalamus","ILM",666,6
697,"Rhomboid nucleus","RH",696,7
698,"Central medial nucleus of the thalamus","CM",696,7
699,"Paracentral nucleus","PCN",696,7
700,"Central lateral nucleus of the thalamus","CL",696,7
701,"Parafascicular nucleus","PF",696,7
702,"Posterior intralaminar thalamic nucleus","PIL",696,7
703,"Reticular nucleus of the thalamus","RT",666,6
704,"Geniculate group, ventral thalamus","GENv",666,6
705,"Intergeniculate leaflet of the lateral geniculate complex","IGL",704,7
706,"Intermediate geniculate nucleus","IntG",704,7
707,"Ventral part of the lateral geniculate complex","LGv",704,7
708,"Ventral part of the lateral geniculate complex, lateral zone","LGvl",707,8
709,"Ventral part of the lateral geniculate complex, medial zone","LGvm",707,8
710,"Subgeniculate nucleus","SubG",704,7
711,"Epithalamus","EPI",666,6
712,"Medial habenula","MH",711,7
713,"Lateral habenula","LH",711,7
714,"Pineal body","PIN",711,7
715,"Hypothalamus","HY",640,4
716,"Periventricular zone","PVZ",715,5
717,"Supraoptic nucleus","SO",716,6
718,"Accessory supraoptic group","ASO",716,6
719,"Nucleus circularis","NC",718,7
720,"Paraventricular hypothalamic nucleus","PVH",716,6
721,"Paraventricular hypothalamic nucleus, magnocellular division","PVHm",720,7
722,"Paraventricular hypothalamic nucleus, magnocellular division, anterior magnocellular part","PVHam",721,8
723,"Paraventricular hypothalamic nucleus, magnocellular division, medial magnocellular part","PVHmm",721,8
724,"Paraventricular hypothalamic nucleus, magnocellular division, posterior magnocellular part","PVHpm",721,8
725,"Paraventricular hypothalamic nucleus, magnocellular division, posterior magnocellular part, lateral zone","PVHpml",724,9
726,"Paraventricular hypothalamic nucleus, magnocellular division, posterior magnocellular part, medial zone","PVHpmm",724,9
727,"Paraventricular hypothalamic nucleus, parvicellular division","PVHp",720,7
728,"Paraventricular hypothalamic nucleus, parvicellular division, anterior parvicellular part","PVHap",727,8
729,"Paraventricular hypothalamic nucleus, parvicellular division, medial parvicellular part, dorsal zone","PVHmpd",727,8
730,"Paraventricular hypothalamic nucleus, parvicellular division, periventricular part","PVHpv",727,8
731,"Periventricular hypothalamic nucleus, anterior part","PVa",716,6
732,"Periventricular hypothalamic nucleus, intermediate part","PVi",716,6
733,"Arcuate hypothalamic nucleus","ARH",716,6
734,"Periventricular region","PVR",715,5
735,"Anterodorsal preoptic nucleus","ADP",734,6
736,"Anterior hypothalamic area","AHA",734,6
737,"Anteroventral preoptic nucleus","AVP",734,6
738,"Anteroventral periventricular nucleus","AVPV",734,6
739,"Dorsomedial nucleus of the hypothalamus","DMH",734,6
740,"Dorsomedial nucleus of the hypothalamus, anterior part","DMHa",739,7
741,"Dorsomedial nucleus of the hypothalamus, posterior part","DMHp",739,7
742,"Dorsomedial nucleus of the hypothalamus, ventral part","DMHv",739,7
743,"Median preoptic nucleus","MEPO",734,6
744,"Medial preoptic area","MPO",734,6
745,"Vascular organ of the lamina terminalis","OV",734,6
746,"Posterodorsal preoptic nucleus","PD",734,6
747,"Parastrial nucleus","PS",734,6
748,"Suprachiasmatic preoptic nucleus","PSCH",734,6
749,"Periventricular hypothalamic nucleus, posterior part","PVp",734,6
750,"Periventricular hypothalamic nucleus, preoptic part","PVpo",734,6
751,"Subparaventricular zone","SBPV",734,6
752,"Suprachiasmatic nucleus","SCH",734,6
753,"Subfornical organ","SFO",734,6
754,"Ventromedial preoptic nucleus","VMPO",734,6
755,"Ventrolateral preoptic nucleus","VLPO",734,6
756,"Hypothalamic medial zone","MEZ",715,5
757,"Anterior hypothalamic nucleus","AHN",756,6
758,"Anterior hypothalamic nucleus, anterior part","AHNa",757,7
759,"Anterior hypothalamic nucleus, central part","AHNc",757,7
760,"Anterior hypothalamic nucleus, dorsal part","AHNd",757,7
761,"Anterior hypothalamic nucleus, posterior part","AHNp",757,7
762,"Mammillary body","MBO",756,6
763,"Lateral mammillary nucleus","LM",762,7
764,"Medial mammillary nucleus","MM",762,7
765,"Medial mammillary nucleus, median part","MMme",764,8
766,"Medial mammillary nucleus, lateral part","MMl",764,8
767,"Medial mammillary nucleus, medial part","MMm",764,8
768,"Medial mammillary nucleus, posterior part","MMp",764,8
769,"Medial mammillary nucleus, dorsal part","MMd",764,8
770,"Supramammillary nucleus","SUM",762,7
771,"Supramammillary nucleus, lateral part","SUMl",770,8
772,"Supramammillary nucleus, medial part","SUMm",770,8
773,"Tuberomammillary nucleus","TM",762,7
774,"Tuberomammillary nucleus, dorsal part","TMd",773,8
775,"Tuberomammillary nucleus, ventral part","TMv",773,8
776,"Medial preoptic nucleus","MPN",756,6
777,"Medial preoptic nucleus, central part","MPNc",776,7
778,"Medial preoptic nucleus, lateral part","MPNl",776,7
779,"Medial preoptic nucleus, medial part","MPNm",776,7
780,"Dorsal premammillary nucleus","PMd",756,6
781,"Ventral premammillary nucleus","PMv",756,6
782,"Paraventricular hypothalamic nucleus, descending division","PVHd",756,6
783,"Paraventricular hypothalamic nucleus, descending division, dorsal parvicellular part","PVHdp",782,7
784,"Paraventricular hypothalamic nucleus, descending division, forniceal part","PVHf",782,7
785,"Paraventricular hypothalamic nucleus, descending division, lateral parvicellular part","PVHlp",782,7
786,"Paraventricular hypothalamic nucleus, descending division, medial parvicellular part, ventral zone","PVHmpv",782,7
787,"Ventromedial hypothalamic nucleus","VMH",756,6
788,"Ventromedial hypothalamic nucleus, anterior part","VMHa",787,7
789,"Ventromedial hypothalamic nucleus, central part","VMHc",787,7
790,"Ventromedial hypothalamic nucleus, dorsomedial part","VMHdm",787,7
791,"Ventromedial hypothalamic nucleus, ventrolateral part","VMHvl",787,7
792,"Posterior hypothalamic nucleus","PH",756,6
793,"Hypothalamic lateral zone","LZ",715,5
794,"Lateral hypothalamic area","LHA",793,6
795,"Lateral preoptic area","LPO",793,6
796,"Preparasubthalamic nucleus","PST",793,6
797,"Parasubthalamic nucleus","PSTN",793,6
798,"Perifornical nucleus","PeF",793,6
799,"Retrochiasmatic area","RCH",793,6
800,"Subthalamic nucleus","STN",793,6
801,"Tuberal nucleus","TU",793,6
802,"Zona incerta","ZI",793,6
803,"Dopaminergic A13 group","A13",802,7
804,"Fields of Forel","FF",802,7
805,"Median eminence","ME",715,5
806,"Midbrain","MB",639,3
807,"Midbrain, sensory related","MBsen",806,4
808,"Superior colliculus, sensory related","SCs",807,5
809,"Superior colliculus, optic layer","SCop",808,6
810,"Superior colliculus, superficial gray layer","SCsg",808,6
811,"Superior colliculus, zonal layer","SCzo",808,6
812,"Inferior colliculus","IC",807,5
813,"Inferior colliculus, central nucleus","ICc",812,6
814,"Inferior colliculus, dorsal nucleus","ICd",812,6
815,"Inferior colliculus, external nucleus","ICe",812,6
816,"Nucleus of the brachium of the inferior colliculus","NB",807,5
817,"Nucleus sagulum","SAG",807,5
818,"Parabigeminal nucleus","PBG",807,5
819,"Midbrain trigeminal nucleus","MEV",807,5
820,"Subcommissural organ","SCO",807,5
821,"Midbrain, motor related","MBmot",806,4
822,"Substantia nigra, reticular part","SNr",821,5
823,"Ventral tegmental area","VTA",821,5
824,"Paranigral nucleus","PN",821,5
825,"Midbrain reticular nucleus, retrorubral area","RR",821,5
826,"Midbrain reticular nucleus","MRN",821,5
827,"Midbrain reticular nucleus, magnocellular part","MRNm",826,6
828,"Midbrain reticular nucleus, magnocellular part, general","MRNmg",826,6
829,"Midbrain reticular nucleus, parvicellular part","MRNp",826,6
830,"Superior colliculus, motor related","SCm",821,5
831,"Superior colliculus, motor related, deep gray layer","SCdg",830,6
832,"Superior colliculus, motor related, deep white layer","SCdw",830,6
833,"Superior colliculus, motor related, intermediate white layer","SCiw",830,6
834,"Superior colliculus, motor related, intermediate gray layer","SCig",830,6
835,"Superior colliculus, motor related, intermediate gray layer, sublayer a","SCig-a",834,7
836,"Superior colliculus, motor related, intermediate gray layer, sublayer b","SCig-b",834,7
837,"Superior colliculus, motor related, intermediate gray layer, sublayer c","SCig-c",834,7
838,"Periaqueductal gray","PAG",821,5
839,"Precommissural nucleus","PRC",838,6
840,"Interstitial nucleus of Cajal","INC",838,6
841,"Nucleus of Darkschewitsch","ND",838,6
842,"Supraoculomotor periaqueductal gray","Su3",838,6
843,"Pretectal region","PRT",821,5
844,"Anterior pretectal nucleus","APN",843,6
845,"Medial pretectal area","MPT",843,6
846,"Nucleus of the optic tract","NOT",843,6
847,"Nucleus of the posterior commissure","NPC",843,6
848,"Olivary pretectal nucleus","OP",843,6
849,"Posterior pretectal nucleus","PPT",843,6
850,"Retroparafascicular nucleus","RPF",843,6
851,"Intercollicular nucleus","InCo",821,5
852,"Cuneiform nucleus","CUN",821,5
853,"Red nucleus","RN",821,5
854,"Oculomotor nucleus","III",821,5
855,"Medial accesory oculomotor nucleus","MA3",821,5
856,"Edinger-Westphal nucleus","EW",821,5
857,"Trochlear nucleus","IV",821,5
858,"Paratrochlear nucleus","Pa4",821,5
859,"Ventral tegmental nucleus","VTN",821,5
860,"Anterior tegmental nucleus","AT",821,5
861,"Lateral terminal nucleus of the accessory optic tract","LT",821,5
862,"Dorsal terminal nucleus of the accessory optic tract","DT",821,5
863,"Medial terminal nucleus of the accessory optic tract","MT",821,5
864,"Substantia nigra, lateral part","SNl",821,5
865,"Midbrain, behavioral state related","MBsta",806,4
866,"Substantia nigra, compact part","SNc",865,5
867,"Pedunculopontine nucleus","PPN",865,5
868,"Midbrain raphe nuclei","RAmb",865,5
869,"Interfascicular nucleus raphe","IF",868,6
870,"Interpeduncular nucleus","IPN",868,6
871,"Interpeduncular nucleus, rostral","IPR",870,7
872,"Interpeduncular nucleus, caudal","IPC",870,7
873,"Interpeduncular nucleus, apical","IPA",870,7
874,"Interpeduncular nucleus, lateral","IPL",870,7
875,"Interpeduncular nucleus, intermediate","IPI",870,7
876,"Interpeduncular nucleus, dorsomedial","IPDM",870,7
877,"Interpeduncular nucleus, dorsolateral","IPDL",870,7
878,"Interpeduncular nucleus, rostrolateral","IPRL",870,7
879,"Rostral linear nucleus raphe","RL",868,6
880,"Central linear nucleus raphe","CLI",868,6
881,"Dorsal nucleus raphe","DR",868,6
882,"Hindbrain","HB",639,3
883,"Pons","P",882,4
884,"Pons, sensory related","P-sen",883,5
885,"Nucleus of the lateral lemniscus","NLL",884,6
886,"Nucleus of the lateral lemniscus, dorsal part","NLLd",885,7
887,"Nucleus of the lateral lemniscus, horizontal part","NLLh",885,7
888,"Nucleus of the lateral lemniscus, ventral part","NLLv",885,7
889,"Principal sensory nucleus of the trigeminal","PSV",884,6
890,"Parabrachial nucleus","PB",884,6
891,"Koelliker-Fuse subnucleus","KF",890,7
892,"Parabrachial nucleus, lateral division","PBl",890,7
893,"Parabrachial nucleus, lateral division, central lateral part","PBlc",892,8
894,"Parabrachial nucleus, lateral division, dorsal lateral part","PBld",892,8
895,"Parabrachial nucleus, lateral division, external lateral part","PBle",892,8
896,"Parabrachial nucleus, lateral division, superior lateral part","PBls",892,8
897,"Parabrachial nucleus, lateral division, ventral lateral part","PBlv",892,8
898,"Parabrachial nucleus, medial division","PBm",890,7
899,"Parabrachial nucleus, medial division, external medial part","PBme",898,8
900,"Parabrachial nucleus, medial division, medial medial part","PBmm",898,8
901,"Parabrachial nucleus, medial division, ventral medial part","PBmv",898,8
902,"Superior olivary complex","SOC",884,6
903,"Superior olivary complex, periolivary region","POR",902,7
904,"Superior olivary complex, medial part","SOCm",902,7
905,"Superior olivary complex, lateral part","SOCl",902,7
906,"Pons, motor related","P-mot",883,5
907,"Barrington's nucleus","B",906,6
908,"Dorsal tegmental nucleus","DTN",906,6
909,"Lateral tegmental nucleus","LTN",906,6
910,"Posterodorsal tegmental nucleus","PDTg",906,6
911,"Pontine central gray","PCG",906,6
912,"Pontine gray","PG",906,6
913,"Pontine reticular nucleus, caudal part","PRNc",906,6
914,"Pontine reticular nucleus, ventral part","PRNv",906,6
915,"Supragenual nucleus","SG",906,6
916,"Superior salivatory nucleus","SSN",906,6
917,"Supratrigeminal nucleus","SUT",906,6
918,"Tegmental reticular nucleus","TRN",906,6
919,"Motor nucleus of trigeminal","V",906,6
920,"Peritrigeminal zone","P5",906,6
921,"Accessory trigeminal nucleus","Acs5",906,6
922,"Parvicellular motor 5 nucleus","PC5",906,6
923,"Intertrigeminal nucleus","I5",906,6
924,"Pons, behavioral state related","P-sat",883,5
925,"Superior central nucleus raphe","CS",924,6
926,"Superior central nucleus raphe, lateral part","CSl",925,7
927,"Superior central nucleus raphe, medial part","CSm",925,7
928,"Locus ceruleus","LC",924,6
929,"Laterodorsal tegmental nucleus","LDT",924,6
930,"Nucleus incertus","NI",924,6
931,"Pontine reticular nucleus","PRNr",924,6
932,"Nucleus raphe pontis","RPO",924,6
933,"Subceruleus nucleus","SLC",924,6
934,"Sublaterodorsal nucleus","SLD",924,6
935,"Medulla","MY",882,4
936,"Medulla, sensory related","MY-sen",935,5
937,"Area postrema","AP",936,6
938,"Cochlear nuclei","CN",936,6
939,"Granular lamina of the cochlear nuclei","CNlam",938,7
940,"Cochlear nucleus, subpedunclular granular region","CNspg",938,7
941,"Dorsal cochlear nucleus","DCO",938,7
942,"Ventral cochlear nucleus","VCO",938,7
943,"Dorsal column nuclei","DCN",936,6
944,"Cuneate nucleus","CU",943,7
945,"Gracile nucleus","GR",943,7
946,"External cuneate nucleus","ECU",936,6
947,"Nucleus of the trapezoid body","NTB",936,6
948,"Nucleus of the solitary tract","NTS",936,6
949,"Nucleus of the solitary tract, central part","NTSce",948,7
950,"Nucleus of the solitary tract, commissural part","NTSco",948,7
951,"Nucleus of the solitary tract, gelatinous part","NTSge",948,7
952,"Nucleus of the solitary tract, lateral part","NTSl",948,7
953,"Nucleus of the solitary tract, medial part","NTSm",948,7
954,"Spinal nucleus of the trigeminal, caudal part","SPVC",936,6
955,"Spinal nucleus of the trigeminal, interpolar part","SPVI",936,6
956,"Spinal nucleus of the trigeminal, oral part","SPVO",936,6
957,"Spinal nucleus of the trigeminal, oral part, caudal dorsomedial part","SPVOcdm",956,7
958,"Spinal nucleus of the trigeminal, oral part, middle dorsomedial part, dorsal zone","SPVOmdmd",956,7
959,"Spinal nucleus of the trigeminal, oral part, middle dorsomedial part, ventral zone","SPVOmdmv",956,7
960,"Spinal nucleus of the trigeminal, oral part, rostral dorsomedial part","SPVOrdm",956,7
961,"Spinal nucleus of the trigeminal, oral part, ventrolateral part","SPVOvl",956,7
962,"Paratrigeminal nucleus","Pa5",936,6
963,"Nucleus z","z",936,6
964,"Medulla, motor related","MY-mot",935,5
965,"Abducens nucleus","VI",964,6
966,"Accessory abducens nucleus","ACVI",964,6
967,"Facial motor nucleus","VII",964,6
968,"Accessory facial motor nucleus","ACVII",964,6
969,"Efferent vestibular nucleus","EV",964,6
970,"Nucleus ambiguus","AMB",964,6
971,"Nucleus ambiguus, dorsal division","AMBd",970,7
972,"Nucleus ambiguus, ventral division","AMBv",970,7
973,"Dorsal motor nucleus of the vagus nerve","DMX",964,6
974,"Efferent cochlear group","ECO",964,6
975,"Gigantocellular reticular nucleus","GRN",964,6
976,"Infracerebellar nucleus","ICB",964,6
977,"Inferior olivary complex","IO",964,6
978,"Intermediate reticular nucleus","IRN",964,6
979,"Inferior salivatory nucleus","ISN",964,6
980,"Linear nucleus of the medulla","LIN",964,6
981,"Lateral reticular nucleus","LRN",964,6
982,"Lateral reticular nucleus, magnocellular part","LRNm",981,7
983,"Lateral reticular nucleus, parvicellular part","LRNp",981,7
984,"Magnocellular reticular nucleus","MARN",964,6
985,"Medullary reticular nucleus","MDRN",964,6
986,"Medullary reticular nucleus, dorsal part","MDRNd",985,7
987,"Medullary reticular nucleus, ventral part","MDRNv",985,7
988,"Parvicellular reticular nucleus","PARN",964,6
989,"Parasolitary nucleus","PAS",964,6
990,"Paragigantocellular reticular nucleus","PGRN",964,6
991,"Paragigantocellular reticular nucleus, dorsal part","PGRNd",990,7
992,"Paragigantocellular reticular nucleus, lateral part","PGRNl",990,7
993,"Perihypoglossal nuclei","PHY",964,6
994,"Nucleus intercalatus","NIS",993,7
995,"Nucleus of Roller","NR",993,7
996,"Nucleus prepositus","PRP",993,7
997,"Paramedian reticular nucleus","PMR",964,6
998,"Parapyramidal nucleus","PPY",964,6
999,"Parapyramidal nucleus, deep part","PPYd",998,7
1000,"Parapyramidal nucleus, superficial part","PPYs",998,7
1001,"Vestibular nuclei","VNC",964,6
1002,"Lateral vestibular nucleus","LAV",1001,7
1003,"Medial vestibular nucleus","MV",1001,7
1004,"Spinal vestibular nucleus","SPIV",1001,7
1005,"Superior vestibular nucleus","SUV",1001,7
1006,"Nucleus x","x",964,6
1007,"Hypoglossal nucleus","XII",964,6
1008,"Nucleus y","y",964,6
1009,"Interstitial nucleus of the vestibular nerve","INV",964,6
1010,"Medulla, behavioral state related","MY-sat",935,5
1011,"Nucleus raphe magnus","RM",1010,6
1012,"Nucleus raphe pallidus","RPA",1010,6
1013,"Nucleus raphe obscurus","RO",1010,6
1014,"Cerebellum","CB",1,2
1015,"Cerebellar cortex","CBX",1014,3
1016,"Cerebellar cortex, molecular layer","CBXmo",1015,4
1017,"Cerebellar cortex, Purkinje layer","CBXpu",1015,4
1018,"Cerebellar cortex, granular layer","CBXgr",1015,4
1019,"Vermal regions","VERM",1015,4
1020,"Lingula (I)","LING",1019,5
1021,"Lingula (I), molecular layer","LINGmo",1020,6
1022,"Lingula (I), Purkinje layer","LINGpu",1020,6
1023,"Lingula (I), granular layer","LINGgr",1020,6
1024,"Central lobule","CENT",1019,5
1025,"Lobule II","CENT2",1024,6
1026,"Lobule II, molecular layer","CENT2mo",1025,7
1027,"Lobule II, Purkinje layer","CENT2pu",1025,7
1028,"Lobule II, granular layer","CENT2gr",1025,7
1029,"Lobule III","CENT3",1024,6
1030,"Lobule III, molecular layer","CENT3mo",1029,7
1031,"Lobule III, Purkinje layer","CENT3pu",1029,7
1032,"Lobule III, granular layer","CENT3gr",1029,7
1033,"Culmen","CUL",1019,5
1034,"Lobule IV","CUL4",1033,6
1035,"Lobule IV, molecular layer","CUL4mo",1034,7
1036,"Lobule IV, Purkinje layer","CUL4pu",1034,7
1037,"Lobule IV, granular layer","CUL4gr",1034,7
1038,"Lobule V","CUL5",1033,6
1039,"Lobule V, molecular layer","CUL5mo",1038,7
1040,"Lobule V, Purkinje layer","CUL5pu",1038,7
1041,"Lobule V, granular layer","CUL5gr",1038,7
1042,"Lobules IV-V","CUL4, 5",1033,6
1043,"Lobules IV-V, molecular layer","CUL4, 5mo",1042,7
1044,"Lobules IV-V, Purkinje layer","CUL4, 5pu",1042,7
1045,"Lobules IV-V, granular layer","CUL4, 5gr",1042,7
1046,"Declive (VI)","DEC",1019,5
1047,"Declive (VI), molecular layer","DECmo",1046,6
1048,"Declive (VI), Purkinje layer","DECpu",1046,6
1049,"Declive (VI), granular layer","DECgr",1046,6
1050,"Folium-tuber vermis (VII)","FOTU",1019,5
1051,"Folium-tuber vermis (VII), molecular layer","FOTUmo",1050,6
1052,"Folium-tuber vermis (VII), Purkinje layer","FOTUpu",1050,6
1053,"Folium-tuber vermis (VII), granular layer","FOTUgr",1050,6
1054,"Pyramus (VIII)","PYR",1019,5
1055,"Pyramus (VIII), molecular layer","PYRmo",1054,6
1056,"Pyramus (VIII), Purkinje layer","PYRpu",1054,6
1057,"Pyramus (VIII), granular layer","PYRgr",1054,6
1058,"Uvula (IX)","UVU",1019,5
1059,"Uvula (IX), molecular layer","UVUmo",1058,6
1060,"Uvula (IX), Purkinje layer","UVUpu",1058,6
1061,"Uvula (IX), granular layer","UVUgr",1058,6
1062,"Nodulus (X)","NOD",1019,5
1063,"Nodulus (X), molecular layer","NODmo",1062,6
1064,"Nodulus (X), Purkinje layer","NODpu",1062,6
1065,"Nodulus (X), granular layer","NODgr",1062,6
1066,"Hemispheric regions","HEM",1015,4
1067,"Simple lobule","SIM",1066,5
1068,"Simple lobule, molecular layer","SIMmo",1067,6
1069,"Simple lobule, Purkinje layer","SIMpu",1067,6
1070,"Simple lobule, granular layer","SIMgr",1067,6
1071,"Ansiform lobule","AN",1066,5
1072,"Crus 1","ANcr1",1071,6
1073,"Crus 1, molecular layer","ANcr1mo",1072,7
1074,"Crus 1, Purkinje layer","ANcr1pu",1072,7
1075,"Crus 1, granular layer","ANcr1gr",1072,7
1076,"Crus 2","ANcr2",1071,6
1077,"Crus 2, molecular layer","ANcr2mo",1076,7
1078,"Crus 2, Purkinje layer","ANcr2pu",1076,7
1079,"Crus 2, granular layer","ANcr2gr",1076,7
1080,"Paramedian lobule","PRM",1066,5
1081,"Paramedian lobule, molecular layer","PRMmo",1080,6
1082,"Paramedian lobule, Purkinje layer","PRMpu",1080,6
1083,"Paramedian lobule, granular layer","PRMgr",1080,6
1084,"Copula pyramidis","COPY",1066,5
1085,"Copula pyramidis, molecular layer","COPYmo",1084,6
1086,"Copula pyramidis, Purkinje layer","COPYpu",1084,6
1087,"Copula pyramidis, granular layer","COPYgr",1084,6
1088,"Paraflocculus","PFL",1066,5
1089,"Paraflocculus, molecular layer","PFLmo",1088,6
1090,"Paraflocculus, Purkinje layer","PFLpu",1088,6
1091,"Paraflocculus, granular layer","PFLgr",1088,6
1092,"Flocculus","FL",1066,5
1093,"Flocculus, molecular layer","FLmo",1092,6
1094,"Flocculus, Purkinje layer","FLpu",1092,6
1095,"Flocculus, granular layer","FLgr",1092,6
1096,"Cerebellar nuclei","CBN",1014,3
1097,"Fastigial nucleus","FN",1096,4
1098,"Interposed nucleus","IP",1096,4
1099,"Dentate nucleus","DN",1096,4
1100,"Vestibulocerebellar nucleus","VeCB",1096,4
1101,"fiber tracts","fiber tracts",0,1
1102,"cranial nerves","cm",1101,2
1103,"terminal nerve","tn",1102,3
1104,"vomeronasal nerve","von",1102,3
1105,"olfactory nerve","In",1102,3
1106,"olfactory nerve layer of main olfactory bulb","onl",1105,4
1107,"lateral olfactory tract, general","lotg",1105,4
1108,"lateral olfactory tract, body","lot",1107,5
1109,"dorsal limb","lotd",1107,5
1110,"accessory olfactory tract","aolt",1107,5
1111,"anterior commissure, olfactory limb","aco",1105,4
1112,"optic nerve","IIn",1102,3
1113,"accessory optic tract","aot",1112,4
1114,"brachium of the superior colliculus","bsc",1112,4
1115,"superior colliculus commissure","csc",1112,4
1116,"optic chiasm","och",1112,4
1117,"optic tract","opt",1112,4
1118,"tectothalamic pathway","ttp",1112,4
1119,"oculomotor nerve","IIIn",1102,3
1120,"medial longitudinal fascicle","mlf",1119,4
1121,"posterior commissure","pc",1119,4
1122,"trochlear nerve","IVn",1102,3
1123,"trochlear nerve decussation","IVd",1122,4
1124,"abducens nerve","VIn",1102,3
1125,"trigeminal nerve","Vn",1102,3
1126,"motor root of the trigeminal nerve","moV",1125,4
1127,"sensory root of the trigeminal nerve","sV",1125,4
1128,"midbrain tract of the trigeminal nerve","mtV",1127,5
1129,"spinal tract of the trigeminal nerve","sptV",1127,5
1130,"facial nerve","VIIn",1102,3
1131,"intermediate nerve","iVIIn",1130,4
1132,"genu of the facial nerve","gVIIn",1130,4
1133,"vestibulocochlear nerve","VIIIn",1102,3
1134,"efferent cochleovestibular bundle","cvb",1133,4
1135,"vestibular nerve","vVIIIn",1133,4
1136,"cochlear nerve","cVIIIn",1133,4
1137,"trapezoid body","tb",1136,5
1138,"intermediate acoustic stria","ias",1136,5
1139,"dorsal acoustic stria","das",1136,5
1140,"lateral lemniscus","ll",1136,5
1141,"inferior colliculus commissure","cic",1136,5
1142,"brachium of the inferior colliculus","bic",1136,5
1143,"glossopharyngeal nerve","IXn",1102,3
1144,"vagus nerve","Xn",1102,3
1145,"solitary tract","ts",1144,4
1146,"accessory spinal nerve","XIn",1102,3
1147,"hypoglossal nerve","XIIn",1102,3
1148,"ventral roots","vrt",1102,3
1149,"dorsal roots","drt",1102,3
1150,"cervicothalamic tract","cett",1149,4
1151,"dorsolateral fascicle","dl",1150,5
1152,"dorsal commissure of the spinal cord","dcm",1150,5
1153,"ventral commissure of the spinal cord","vc",1150,5
1154,"fasciculus proprius","fpr",1150,5
1155,"dorsal column","dc",1150,5
1156,"cuneate fascicle","cuf",1155,6
1157,"gracile fascicle","grf",1155,6
1158,"internal arcuate fibers","iaf",1155,6
1159,"medial lemniscus","ml",1150,5
1160,"spinothalamic tract","sst",1102,3
1161,"lateral spinothalamic tract","sttl",1160,4
1162,"ventral spinothalamic tract","sttv",1160,4
1163,"spinocervical tract","scrt",1160,4
1164,"spino-olivary pathway","sop",1160,4
1165,"spinoreticular pathway","srp",1160,4
1166,"spinovestibular pathway","svp",1160,4
1167,"spinotectal pathway","stp",1160,4
1168,"spinohypothalamic pathway","shp",1160,4
1169,"spinotelenchephalic pathway","step",1160,4
1170,"hypothalamohypophysial tract","hht",1169,5
1171,"cerebellum related fiber tracts","cbf",1101,2
1172,"cerebellar commissure","cbc",1171,3
1173,"cerebellar peduncles","cbp",1171,3
1174,"superior cerebelar peduncles","scp",1173,4
1175,"superior cerebellar peduncle decussation","dscp",1174,5
1176,"spinocerebellar tract","sct",1175,6
1177,"uncinate fascicle","uf",1174,5
1178,"ventral spinocerebellar tract","sctv",1174,5
1179,"middle cerebellar peduncle","mcp",1173,4
1180,"inferior cerebellar peduncle","icp",1173,4
1181,"dorsal spinocerebellar tract","sctd",1180,5
1182,"cuneocerebellar tract","cct",1180,5
1183,"juxtarestiform body","jrb",1180,5
1184,"bulbocerebellar tract","bct",1180,5
1185,"olivocerebellar tract","oct",1184,6
1186,"reticulocerebellar tract","rct",1184,6
1187,"trigeminocerebellar tract","tct",1173,4
1188,"arbor vitae","arb",1171,3
1189,"supra-callosal cerebral white matter","scwm",1101,2
1190,"lateral forebrain bundle system","lfbs",1101,2
1191,"corpus callosum","cc",1190,3
1192,"corpus callosum, anterior forceps","fa",1191,4
1193,"external capsule","ec",1192,5
1194,"corpus callosum, extreme capsule","ee",1191,4
1195,"genu of corpus callosum","ccg",1191,4
1196,"corpus callosum, posterior forceps","fp",1191,4
1197,"corpus callosum, rostrum","ccr",1191,4
1198,"corpus callosum, body","ccb",1191,4
1199,"corpus callosum, splenium","ccs",1191,4
1200,"corticospinal tract","cst",1190,3
1201,"internal capsule","int",1200,4
1202,"cerebal peduncle","cpd",1200,4
1203,"corticotectal tract","cte",1200,4
1204,"corticorubral tract","crt",1200,4
1205,"corticopontine tract","cpt",1200,4
1206,"corticobulbar tract","cbt",1200,4
1207,"pyramid","py",1200,4
1208,"pyramidal decussation","pyd",1200,4
1209,"corticospinal tract, crossed","cstc",1200,4
1210,"corticospinal tract, uncrossed","cstu",1200,4
1211,"thalamus related","lfbst",1190,3
1212,"external medullary lamina of the thalamus","em",1211,4
1213,"internal medullary lamina of the thalamus","im",1211,4
1214,"middle thalamic commissure","mtc",1211,4
1215,"thalamic peduncles","tp",1211,4
1216,"optic radiation","or",1211,4
1217,"auditory radiation","ar",1211,4
1218,"extrapyramidal fiber systems","eps",1101,2
1219,"cerebral nuclei related","epsc",1218,3
1220,"pallidothalamic pathway","pap",1219,4
1221,"nigrostriatal tract","nst",1219,4
1222,"nigrothalamic fibers","ntt",1219,4
1223,"pallidotegmental fascicle","ptf",1219,4
1224,"striatonigral pathway","snp",1219,4
1225,"subthalamic fascicle","stf",1219,4
1226,"tectospinal pathway","tsp",1218,3
1227,"direct tectospinal pathway","tspd",1226,4
1228,"doral tegmental decussation","dtd",1226,4
1229,"crossed tectospinal pathway","tspc",1226,4
1230,"rubrospinal tract","rust",1218,3
1231,"ventral tegmental decussation","vtd",1230,4
1232,"rubroreticular tract","rrt",1230,4
1233,"central tegmental bundle","ctb",1218,3
1234,"retriculospinal tract","rst",1218,3
1235,"retriculospinal tract, lateral part","rstl",1234,4
1236,"retriculospinal tract, medial part","rstm",1234,4
1237,"vestibulospinal pathway","vsp",1218,3
1238,"medial forebrain bundle system","mfbs",1101,2
1239,"cerebrum related","mfbc",1238,3
1240,"amygdalar capsule","amc",1239,4
1241,"ansa peduncularis","apd",1239,4
1242,"anterior commissure, temporal limb","act",1239,4
1243,"cingulum bundle","cing",1239,4
1244,"fornix system","fxs",1239,4
1245,"alveus","alv",1244,5
1246,"dorsal fornix","df",1244,5
1247,"fimbria","fi",1244,5
1248,"precommissural fornix, general","fxprg",1244,5
1249,"precommissural fornix diagonal band","db",1248,6
1250,"postcommissural fornix","fxpo",1244,5
1251,"medial corticohypothalamic tract","mct",1250,6
1252,"columns of the fornix","fx",1250,6
1253,"hippocampal commissures","hc",1244,5
1254,"dorsal hippocampal commissure","dhc",1253,6
1255,"ventral hippocampal commissure","vhc",1253,6
1256,"perforant path","per",1244,5
1257,"angular path","ab",1244,5
1258,"longitudinal association bundle","lab",1239,4
1259,"stria terminalis","st",1239,4
1260,"commissural branch of stria terminalis","stc",1259,5
1261,"hypothalamus related","mfsbshy",1238,3
1262,"medial forebrain bundle","mfb",1261,4
1263,"ventrolateral hypothalamic tract","vlt",1261,4
1264,"preoptic commissure","poc",1261,4
1265,"supraoptic commissures","sup",1261,4
1266,"supraoptic commissures, anterior","supa",1265,5
1267,"supraoptic commissures, dorsal","supd",1265,5
1268,"supraoptic commissures, ventral","supv",1265,5
1269,"premammillary commissure","pmx",1261,4
1270,"supramammillary decussation","smd",1261,4
1271,"propriohypothalamic pathways","php",1261,4
1272,"propriohypothalamic pathways, dorsal","phpd",1271,5
1273,"propriohypothalamic pathways, lateral","phpl",1271,5
1274,"propriohypothalamic pathways, medial","phpm",1271,5
1275,"propriohypothalamic pathways, ventral","phpv",1271,5
1276,"periventricular bundle of the hypothalamus","pvbh",1261,4
1277,"mammillary related","mfbsma",1261,4
1278,"principal mammillary tract","pm",1277,5
1279,"mammillothalamic tract","mtt",1277,5
1280,"mammillotegmental tract","mtg",1277,5
1281,"mammillary peduncle","mp",1277,5
1282,"dorsal thalamus related","mfbst",1261,4
1283,"periventricular bundle of the thalamus","pvbt",1282,5
1284,"epithalamus related","mfbse",1261,4
1285,"stria medullaris","sm",1284,5
1286,"fasciculus retroflexus","fr",1284,5
1287,"habenular commissure","hbc",1284,5
1288,"pineal stalk","PIS",1284,5
1289,"midbrain related","mfbsm",1261,4
1290,"dorsal longitudinal fascicle","dlf",1289,5
1291,"dorsal tegmental tract","dtt",1289,5
1292,"ventricular systems","VS",0,1
1293,"lateral ventricle","VL",1292,2
1294,"rhinocele","RC",1293,3
1295,"subependymal zone","SEZ",1293,3
1296,"choroid plexus","chpl",1293,3
1297,"choroid fissure","chfl",1293,3
1298,"interventricular foramen","IVF",1292,2
1299,"third ventricle","V3",1292,2
1300,"cerebral aqueduct","AQ",1292,2
1301,"fourth ventricle","V4",1292,2
1302,"lateral recess","V4r",1301,3
1303,"central canal, spinal cord/medulla","c",1292,2
1304,"grooves","grv",0,1
1305,"grooves of the cerebral cortex","grv of CTX",1304,2
1306,"endorhinal groove","eg",1305,3
1307,"hippocampal fissure","hf",1305,3
1308,"rhinal fissure","rf",1305,3
1309,"rhinal incisure","ri",1305,3
1310,"grooves of the cerebellar cortex","grv of CBX",1304,2
1311,"precentral fissure","pce",1310,3
1312,"preculminate fissure","pcf",1310,3
1313,"primary fissure","pri",1310,3
1314,"posterior superior fissure","psf",1310,3
1315,"prepyramidal fissure","ppf",1310,3
1316,"secondary fissure","sec",1310,3
1317,"posterolateral fissure","plf",1310,3
1318,"nodular fissure","nf",1310,3
1319,"simple fissure","sif",1310,3
1320,"intercrural fissure","icf",1310,3
1321,"ansoparamedian fissure","apf",1310,3
1322,"intraparafloccular fissure","ipf",1310,3
1323,"paramedian sulcus","pms",1310,3
1324,"parafloccular sulcus","pfs",1310,3
1325,"Interpeduncular fossa","IPF",1304,2
1326,"retina","retina",0,1
"""
if __name__ == '__main__':
    unittest.main()
