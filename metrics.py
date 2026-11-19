"""
Aggregate risk metrics (Table 6), Pareto analysis (Section 3.4) and
risk-zone counts (Figure 3). Running this file prints everything and checks
it against the values published in the paper.
"""
import numpy as np

from data import (FAILURE_MODES, SYSTEMS, RPN_THRESHOLD, SEVERITY_GATE,
                  modes_for)

# High-severity / high-occurrence zone shaded in Figure 3
ZONE_S_MIN = 8
ZONE_O_MIN = 3.5


def system_metrics(system: str) -> dict:
    ms = modes_for(system)
    rpn = np.array([m.rpn for m in ms])
    return {
        "Total Failure Modes Analyzed": len(ms),
        "Average Severity (S)": np.mean([m.S for m in ms]),
        "Average Occurrence (O)": np.mean([m.O for m in ms]),
        "Average Detection (D)": np.mean([m.D for m in ms]),
        "Average RPN": rpn.mean(),
        "Failure Modes with RPN >= 100": int((rpn >= RPN_THRESHOLD).sum()),
        "Failure Modes with RPN >= 150": int((rpn >= 150).sum()),
        "Failure Modes with Severity (S) = 10": sum(m.S == 10 for m in ms),
    }


def table6() -> dict:
    return {s: system_metrics(s) for s in SYSTEMS}


def pareto():
    """All modes sorted by RPN (descending) with cumulative % of total RPN."""
    ranked = sorted(FAILURE_MODES, key=lambda m: m.rpn, reverse=True)
    rpn = np.array([m.rpn for m in ranked], dtype=float)
    cum_pct = np.cumsum(rpn) / rpn.sum() * 100
    return ranked, cum_pct


def zone_counts() -> dict:
    return {
        s: sum(m.S >= ZONE_S_MIN and m.O >= ZONE_O_MIN for m in modes_for(s))
        for s in SYSTEMS
    }


def severity_gate_flags():
    """Modes with S >= 9: mandatory design review regardless of RPN (Sec. 2.2)."""
    return [m for m in FAILURE_MODES if m.S >= SEVERITY_GATE]


def print_report():
    t6 = table6()
    print("=" * 78)
    print("TABLE 6 - Aggregate FMEA risk metrics")
    print("=" * 78)
    header = f"{'Metric':<40}" + "".join(f"{s[:22]:>19}" for s in SYSTEMS)
    print(header)
    for metric in next(iter(t6.values())):
        row = f"{metric:<40}"
        for s in SYSTEMS:
            v = t6[s][metric]
            row += f"{v:>19.2f}" if isinstance(v, float) else f"{v:>19d}"
        print(row)

    ranked, cum = pareto()
    n = len(ranked)
    top10 = sum(m.rpn for m in ranked[:10])
    total = sum(m.rpn for m in ranked)
    print("\nPARETO (Section 3.4)")
    print(f"  total failure modes        : {n}")
    print(f"  top 10 share of modes      : {10 / n * 100:.1f}%")
    print(f"  top 10 share of total RPN  : {top10 / total * 100:.1f}%")
    print(f"  50% crossed at rank        : {int(np.argmax(cum >= 50)) + 1}")
    print(f"  80% crossed at rank        : {int(np.argmax(cum >= 80)) + 1}")
    edt_top10 = sum(m.system.startswith("Electrodynamic") for m in ranked[:10])
    print(f"  EDT modes in top 10        : {edt_top10}")

    print("\nHIGH-SEVERITY / HIGH-OCCURRENCE ZONE (Figure 3)")
    for s, c in zone_counts().items():
        print(f"  {s:<30} {c} of {len(modes_for(s))}")


def validate():
    """Assert that the code reproduces the numbers printed in the paper."""
    t6 = table6()
    ds, edt, cg = SYSTEMS
    expected = {
        ds:  (9, 7.56, 2.89, 6.89, 150.0, 5, 4, 2),
        edt: (8, 8.62, 3.75, 6.88, 221.1, 8, 6, 2),
        cg:  (7, 9.14, 2.14, 4.71, 94.9, 3, 1, 4),
    }
    for s, exp in expected.items():
        got = tuple(t6[s].values())
        for i, (g, e) in enumerate(zip(got, exp)):
            decimals = 1 if i == 4 else 2   # index 4 = Average RPN (paper: 1 decimal)
            assert round(g, decimals) == e, f"{s}: got {g}, expected {e}"

    ranked, cum = pareto()
    top10 = sum(m.rpn for m in ranked[:10])
    total = sum(m.rpn for m in ranked)
    assert len(ranked) == 24
    assert round(10 / 24 * 100) == 42
    assert round(top10 / total * 100) == 64
    assert int(np.argmax(cum >= 50)) + 1 == 8
    assert int(np.argmax(cum >= 80)) + 1 == 15
    assert ranked[0].label == "PC Fail" and ranked[0].rpn == 315
    assert sum(m.system == edt for m in ranked[:10]) == 6
    assert zone_counts() == {ds: 1, edt: 3, cg: 0}
    print("\nAll published values reproduced.")


if __name__ == "__main__":
    print_report()
    validate()
