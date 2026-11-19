"""Reproduce every table value and figure in the paper."""
import csv

from data import FAILURE_MODES
from metrics import print_report, validate
from figures import save_all


def export_csv(path="fmea_tables.csv"):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["System", "Subsystem", "Failure Mode", "Effect",
                    "S", "O", "D", "RPN", "RPN>=100", "S>=9"])
        for m in FAILURE_MODES:
            w.writerow([m.system, m.subsystem, m.mode, m.effect,
                        m.S, m.O, m.D, m.rpn,
                        "yes" if m.rpn >= 100 else "", "yes" if m.S >= 9 else ""])
    print(f"saved {path}")


if __name__ == "__main__":
    print_report()
    validate()
    export_csv()
    save_all()
