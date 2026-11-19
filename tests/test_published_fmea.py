"""Independent article-vs-code numeric consistency checks, not validation of FMEA score justification."""
import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from data import FAILURE_MODES, SYSTEMS, modes_for
from metrics import table6, pareto, zone_counts, validate
from run_all import export_csv
import figures

# Values transcribed independently from JoSS Vol. 15 (2) Tables 3-5, pp. 1324-1325.
PUBLISHED_SOD = {
    "Drag Sail": [
        (10,3,8,240), (9,4,7,252), (7,3,5,105),
        (8,2,6,96), (5,2,9,90), (4,3,8,96),
        (10,2,3,60), (9,3,9,243), (6,4,7,168),
    ],
    "Electrodynamic Tether (EDT)": [
        (9,4,6,216), (10,3,7,210), (10,3,10,300),
        (8,4,8,256), (9,5,7,315), (7,4,8,224),
        (9,3,4,108), (7,4,5,140),
    ],
    "Cold-Gas Propulsion": [
        (10,2,7,140), (10,1,2,20), (10,3,5,150),
        (8,2,6,96), (9,2,4,72), (10,2,3,60),
        (7,3,6,126),
    ],
}

class TestPublishedFMEA(unittest.TestCase):
    def test_all_24_scores_against_published_tables(self):
        self.assertEqual(len(FAILURE_MODES), 24)
        for system, expected in PUBLISHED_SOD.items():
            actual = [(x.S,x.O,x.D,x.rpn) for x in modes_for(system)]
            self.assertEqual(actual, expected, system)

    def test_score_bounds_and_unique_modes(self):
        self.assertEqual(len({(m.system,m.mode) for m in FAILURE_MODES}),24)
        for m in FAILURE_MODES:
            self.assertTrue(all(isinstance(x,int) and 1<=x<=10 for x in (m.S,m.O,m.D)))
            self.assertEqual(m.rpn,m.S*m.O*m.D)

    def test_table_6_published_metrics(self):
        expected = {
           "Drag Sail": (9,7.56,2.89,6.89,150.0,5,4,2),
           "Electrodynamic Tether (EDT)": (8,8.62,3.75,6.88,221.1,8,6,2),
           "Cold-Gas Propulsion": (7,9.14,2.14,4.71,94.9,3,1,4),
        }
        for sys, exp in expected.items():
            got=list(table6()[sys].values())
            for i,(a,e) in enumerate(zip(got,exp)):
                self.assertEqual(round(float(a),1 if i==4 else 2),float(e))

    def test_pareto_section_3_4(self):
        ranked,cumulative=pareto()
        self.assertEqual(len(ranked),24)
        self.assertEqual(sum(m.rpn for m in ranked),3783)
        self.assertEqual(sum(m.rpn for m in ranked[:10]),2424)
        self.assertAlmostEqual(float(cumulative[9]),2424/3783*100)
        self.assertEqual(next(i+1 for i,c in enumerate(cumulative) if c>=50),8)
        self.assertEqual(next(i+1 for i,c in enumerate(cumulative) if c>=80),15)
        self.assertEqual(sum('Electrodynamic' in m.system for m in ranked[:10]),6)

    def test_risk_zone_figure3(self):
        self.assertEqual(list(zone_counts().values()),[1,3,0])

    def test_csv_export_matches_scores(self):
        with tempfile.TemporaryDirectory() as temp:
            f=Path(temp)/'rows.csv'; export_csv(f)
            with f.open(newline='', encoding='utf-8') as fh: rows=list(csv.DictReader(fh))
            self.assertEqual(len(rows),24)
            for row, mode in zip(rows,FAILURE_MODES):
                self.assertEqual(tuple(map(int,[row['S'],row['O'],row['D'],row['RPN']])),(mode.S,mode.O,mode.D,mode.rpn))
                self.assertEqual(row['RPN>=100']=='yes',mode.rpn>=100)
                self.assertEqual(row['S>=9']=='yes',mode.S>=9)

    def test_all_4_figures_can_render(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(figures,'OUT',Path(tmp)):
                figures.save_all(dpi=60)
            self.assertEqual(len(list(Path(tmp).glob('figure*.png'))),4)

    def test_existing_validate(self):
        validate()

if __name__ == '__main__': unittest.main()
