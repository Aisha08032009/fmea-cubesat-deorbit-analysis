# Technical audit — FMEA for CubeSat Deorbit Systems

**Review date:** 2026-11-19  
**Scope:** user-provided JoSS published 13-page PDF and `fmea-cubesat-deorbit-code.zip`; no live hardware testing or independent reliability database analysis.  
**Result:** numerical reproduction PASS; physical scoring audit NOT established.

## Inputs and provenance

- Published article PDF SHA-256: `83f11484baf21da4698755266a20c342b7388e465c0107973d65115600f14af0`
- Supplied code ZIP SHA-256: `fb66ac8140c77b47b259f747c660c2f03980cdeedf07d9e53a0fc328b0605468`
- Paper: *Journal of Small Satellites*, 15(2), 1319–1331 (published October 30, 2026).
- Code ZIP file timestamps are November 19, 2026. Without other records, these timestamps cannot establish that the scripts in the ZIP are the original scripts used before publication. They do not negate numerical reproduction.

## Tests conducted

1. Unpacked and executed supplied `run_all.py` in a clean extracted directory; no runtime errors.
2. Transcribed the 24 S/O/D/RPN tuples in published Tables 3–5 and compared row-by-row with `data.py`: **24/24 agree**, in the same order.
3. Confirmed all 24 RPNs equal S×O×D and the category means, threshold counts and severity-gate counts agree with published Table 6.
4. Verified total RPN 3,783; highest RPN 315; top-10 subtotal 2,424 (= 64.08% of 3,783), ten modes are 41.67% of 24; thresholds pass 50% at rank 8 and 80% at rank 15; six EDT modes in top ten.
5. Independently confirmed the Figure 3 risk-zone counts: Drag Sail 1/9, EDT 3/8, Propulsion 0/7 for S≥8 and O≥3.5.
6. Generated four figures in the local environment. Content and rankings match supplied PNG visualizations; dimensions vary slightly between environments due to rendering differences, so figure PNG files are not byte-identical.
7. Included a dedicated `unittest` suite, separate score fixtures, and exported audit CSVs. This suite cross-checks implementation against article numbers, not against independently measured reliability.

## Technical interpretation

- This is **deterministic reproduction of an expert-elicited scoring dataset**, not a physical/stochastic deorbit simulation. The code cannot demonstrate S/O/D estimates are calibrated to failure frequencies or prove actual CubeSat disposal compliance.
- RPN products and their sums are prioritization constructs, not cardinal measures of mission failure probabilities. Treat the 64% Pareto figure as a *share of summed RPN values*, not 64% of actual risk or expected failures.
- The paper uses both RPN and a severity gate for prioritization. Preserve both in code and documentation.
- Under different assumptions for occurrence, detection, or mission-end criteria, rankings may change. A future extension could quantify such sensitivity, but it should not alter the published dataset without explicit new labels.
- The published article retains its own scientific limitations. The code release does not replace external review of scores or their underlying references.

## Publication and copyright

JoSS's FAQ says authors transfer article copyright in its submission process, and the PDF states publisher copyright. The private package omits the publisher's PDF and links to the official version. Confirm permission before publicly hosting a publisher-formatted PDF or derivative image materials. Software authorship and licensing should be considered separately; this package does not presume a particular license.

## Verdict

**Suitable for your private research-code portfolio now.** The numbers and plotted outputs are consistent with the paper. Before public release, confirm redistribution rights and software licensing; describe the project as reproducible FMEA scoring analysis rather than a satellite deorbit simulator. No changes to published research results are recommended on the basis of this arithmetic audit alone.
