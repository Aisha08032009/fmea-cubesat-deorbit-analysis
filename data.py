"""
FMEA dataset for CubeSat deorbit systems (Tables 3-5 of the paper).

Shermatova, A. (2026). Failure Mode and Effects Analysis (FMEA) for CubeSat
Deorbit Systems: A Comparative Risk Assessment of Drag Sails, Electrodynamic
Tethers, and Propulsion Modules. Journal of Small Satellites, 15(2), 1319-1331.

Scoring (Table 2, Section 2.3.1):
    S = Severity   (1-10), anchored to the resulting deorbit-timeline impact
    O = Occurrence (1-10), anchored to anomaly databases / reliability literature
    D = Detection  (1-10), anchored to standard CubeSat telemetry
    RPN = S * O * D
"""
from dataclasses import dataclass

RPN_THRESHOLD = 100      # action-priority cutoff (Section 2.2)
SEVERITY_GATE = 9        # S >= 9 is flagged for mandatory design review

DRAG_SAIL = "Drag Sail"
EDT = "Electrodynamic Tether (EDT)"
COLD_GAS = "Cold-Gas Propulsion"
SYSTEMS = [DRAG_SAIL, EDT, COLD_GAS]


@dataclass(frozen=True)
class FailureMode:
    system: str
    subsystem: str
    mode: str
    effect: str
    S: int
    O: int
    D: int
    label: str  # short name used on the Pareto chart (Figure 4)

    @property
    def rpn(self) -> int:
        return self.S * self.O * self.D


FAILURE_MODES = [
    # ---------------- Table 3: Drag Sail ----------------
    FailureMode(DRAG_SAIL, "Deployment Mechanism",
                "Latch seizure (corrosion/cold welding) - fails to release",
                "Sail does not deploy - deorbit impossible",
                10, 3, 8, "Latch Seizure"),
    FailureMode(DRAG_SAIL, "Deployment Mechanism",
                "Actuator failure (motor/spring) - mechanical fault",
                "Partial or no deployment - reduced or zero drag",
                9, 4, 7, "Actuator Fail"),
    FailureMode(DRAG_SAIL, "Structural Assembly",
                "Boom fails to fully deploy/lock",
                "Reduced effective drag area - longer deorbit time",
                7, 3, 5, "Boom Not Locked"),
    FailureMode(DRAG_SAIL, "Structural Assembly",
                "Boom structural failure due to dynamic loads",
                "Sail collapses - significant area loss",
                8, 2, 6, "Boom Failure"),
    FailureMode(DRAG_SAIL, "Sail Membrane",
                "Puncture/tear from micrometeoroid or debris",
                "Localized puncture; rip-stop weave arrests tear propagation, "
                "limiting area loss provided sail area is sized with margin",
                5, 2, 9, "Membrane Puncture"),
    FailureMode(DRAG_SAIL, "Sail Membrane",
                "Material degradation, atomic-oxygen erosion (material-dependent)",
                "Significant for uncoated Mylar/Kapton-class films; reduced for "
                "AO-resistant materials or coating; UV embrittlement is secondary",
                4, 3, 8, "Material Degradation"),
    FailureMode(DRAG_SAIL, "Control & Sensing",
                "Deployment command not issued (software fault)",
                "System remains stowed - no deorbit",
                10, 2, 3, "Command Fault"),
    FailureMode(DRAG_SAIL, "Control & Sensing",
                "False-positive deployment confirmation sensor",
                "Ground believes sail is deployed when it is not",
                9, 3, 9, "False Sensor"),
    FailureMode(DRAG_SAIL, "Structural Assembly / Control & Sensing",
                "Failure to achieve/maintain sail orientation relative to velocity vector",
                "Reduced effective cross-sectional area in the ram direction; "
                "extends deorbit time even with full physical deployment",
                6, 4, 7, "Orientation Fail"),

    # ---------------- Table 4: Electrodynamic Tether ----------------
    FailureMode(EDT, "Deployment System",
                "Tether jams on spool during deployment",
                "Partial deployment - drastically reduced Lorentz force",
                9, 4, 6, "Tether Jam"),
    FailureMode(EDT, "Deployment System",
                "Deployment motor/mechanism fails",
                "Tether remains stowed - no electrodynamic effect",
                10, 3, 7, "Deploy Motor Fail"),
    FailureMode(EDT, "Tether Assembly",
                "Tether severed by micrometeoroid/debris",
                "Loss of electrical continuity - system rendered inert",
                10, 3, 10, "Tether Cut"),
    FailureMode(EDT, "Tether Assembly",
                "Tether insulation failure (arcing/short)",
                "Loss of generated current - reduced or no thrust",
                8, 4, 8, "Insulation Fail"),
    FailureMode(EDT, "Plasma Contactor",
                "Contactor fails to emit/collect electrons",
                "Current loop cannot close - no Lorentz force",
                9, 5, 7, "PC Fail"),
    FailureMode(EDT, "Plasma Contactor",
                "Contactor surface contamination/erosion",
                "Increased impedance, reduced current, lower thrust",
                7, 4, 8, "Contamination"),
    FailureMode(EDT, "Power & Control Unit",
                "Anode/cathode power converter failure",
                "No current driven through tether",
                9, 3, 4, "Converter Fail"),
    FailureMode(EDT, "Power & Control Unit",
                "Control software fault (current regulation)",
                "Suboptimal or zero current - reduced deorbit efficiency",
                7, 4, 5, "EDT Software"),

    # ---------------- Table 5: Cold-Gas Propulsion ----------------
    FailureMode(COLD_GAS, "Propellant Storage",
                "Micro-leak in tank/valve seal over mission life",
                "Insufficient propellant mass for required delta-V",
                10, 2, 7, "Micro-leak"),
    FailureMode(COLD_GAS, "Propellant Storage",
                "Tank rupture (corrosion/defect)",
                "Catastrophic propellant loss, possible satellite damage",
                10, 1, 2, "Tank Rupture"),
    FailureMode(COLD_GAS, "Thruster Assembly",
                "Solenoid valve sticks open/closed",
                "No thrust or uncontrolled thrust (propellant waste)",
                10, 3, 5, "Valve Stuck"),
    FailureMode(COLD_GAS, "Thruster Assembly",
                "Nozzle clogging (contamination)",
                "Reduced thrust or misdirected thrust vector",
                8, 2, 6, "Nozzle Clog"),
    FailureMode(COLD_GAS, "Pressure Regulation",
                "Pressure regulator failure (stuck open/closed)",
                "Unable to feed propellant at correct pressure",
                9, 2, 4, "Regulator Fail"),
    FailureMode(COLD_GAS, "Control Electronics",
                "Firing sequence software fault",
                "Maneuver not executed or executed incorrectly",
                10, 2, 3, "Firing Software"),
    FailureMode(COLD_GAS, "Telemetry System",
                "Faulty pressure/temperature sensor readings",
                "Incorrect system state knowledge - faulty decisions",
                7, 3, 6, "Sensor Fault"),
]


def modes_for(system: str):
    return [m for m in FAILURE_MODES if m.system == system]
