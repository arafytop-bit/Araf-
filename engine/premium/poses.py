"""Extra rig poses for the v3 motion grammar (patched into engine.roundhead without touching v2 renders).

run   : arms pump, long stride; use with flip_phase (5 drawings/s flipbook) + forward lean
cheer : both arms up (V)
swing : both hands up together over the head (two-handed weapon swing)
drum  : alternating raised arms (war drum), phase-driven
hold  : both hands forward at chest height (carrying / offering)
fall  : arms flung up (used while falling)
"""
import math

from engine import roundhead as RH

SH = RH.SH
_orig_arms, _orig_legs = RH.arms_for, RH.legs_for

RH.ARMS.update({
    'cheer': [(((-SH, 1.04), (-0.86, 0.62), (-1.02, 0.12), (-1.08, -0.30)), False),
              (((SH, 1.04), (0.86, 0.62), (1.02, 0.12), (1.08, -0.30)), False)],
    'swing': [(((-SH, 1.04), (-0.70, 0.55), (-0.40, 0.00), (-0.10, -0.55)), False),
              (((SH, 1.04), (0.75, 0.55), (0.45, 0.00), (0.12, -0.50)), False)],
    'hold':  [(((-SH, 1.04), (-0.82, 1.42), (-0.62, 1.70), (-0.30, 1.62)), True),
              (((SH, 1.04), (0.82, 1.42), (0.62, 1.70), (0.30, 1.62)), True)],
    'fall':  [(((-SH, 1.04), (-0.95, 0.70), (-1.25, 0.30), (-1.35, -0.05)), False),
              (((SH, 1.04), (0.95, 0.70), (1.25, 0.30), (1.35, -0.05)), False)],
})


def arms_for(pose, phase=0.0):
    if pose == 'run':
        s = math.sin(phase)
        return [(((-SH, 1.04), (-0.70 - 0.30 * s, 1.30), (-0.62 - 0.55 * s, 1.62), (-0.40 - 0.70 * s, 1.80)), False),
                (((SH, 1.04), (0.70 - 0.30 * s, 1.30), (0.62 - 0.55 * s, 1.62), (0.40 - 0.70 * s, 1.80)), False)]
    if pose == 'drum':
        s = 0.5 + 0.5 * math.sin(phase)
        lh = -0.20 + 1.4 * s
        rh = -0.20 + 1.4 * (1 - s)
        return [(((-SH, 1.04), (-0.95, 0.80), (-0.95, lh + 0.30), (-0.70, lh)), False),
                (((SH, 1.04), (0.95, 0.80), (0.95, rh + 0.30), (0.70, rh)), False)]
    return _orig_arms(pose, phase)


def legs_for(pose, phase=0.0, hip=2.40, foot=3.10):
    if pose == 'run':
        s = math.sin(phase)
        c = math.cos(phase)
        lift = 0.18
        return [((-0.24, hip), (-0.26 + 0.46 * s, foot - lift * max(0.0, c))),
                ((0.24, hip), (0.26 - 0.46 * s, foot - lift * max(0.0, -c)))]
    if pose == 'fall':
        return [((-0.26, hip), (-0.55, foot - 0.15)), ((0.26, hip), (0.55, foot - 0.15))]
    return _orig_legs(pose, phase, hip=hip, foot=foot)


RH.arms_for = arms_for
RH.legs_for = legs_for
