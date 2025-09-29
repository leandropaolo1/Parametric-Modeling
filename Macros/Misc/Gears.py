# Gear calculation helper for the proposed planetary set
# Assumptions:
# - Standard full-depth 20° involute gears (addendum = m, dedendum = 1.25*m)
# - Ring gear is internal (tooth count Zr), sun and planets external
# - No profile shift
# - Simple estimate for root space clearance ~ 0.6 * circular pitch (rule of thumb)
# - Check whether a 3/16" (4.7625 mm) flat end mill can access the tooth root space

import math

# Input parameters (you can tweak)
m = 2.5                 # module (mm)
pa_deg = 20.0           # pressure angle (deg)
Zs = 26                 # sun teeth
Zp = 23                 # planet teeth
Zr = 72                 # ring teeth (internal)
root_space_factor = 0.60  # heuristic fraction of circular pitch available at root
tool_diameter_mm = 3/16 * 25.4  # 3/16" in mm

pa = math.radians(pa_deg)

def gear_metrics(z, module, pressure_angle_deg=20.0, external=True):
    pa = math.radians(pressure_angle_deg)
    d = module * z
    db = d * math.cos(pa)               # base circle diameter
    addendum = module
    dedendum = 1.25 * module
    do = d + 2 * addendum               # outside diameter
    dr = d - 2 * dedendum               # root diameter
    p_circ = math.pi * module           # circular pitch
    return {
        "z": z,
        "d (pitch dia)": d,
        "db (base dia)": db,
        "do (outside dia)": do if external else d - 2*addendum,   # for internal ring OD at tooth tips
        "dr (root dia)": dr if external else d + 2*dedendum,      # for internal ring root (toward center of tooth space)
        "addendum": addendum,
        "dedendum": dedendum,
        "circular pitch": p_circ
    }

sun = gear_metrics(Zs, m, pa_deg, external=True)
planet = gear_metrics(Zp, m, pa_deg, external=True)
# For ring: use internal gear interpretations for do/dr printing, but keep "pitch dia" as module*z
ring = gear_metrics(Zr, m, pa_deg, external=False)

# Center-distance checks for a planetary set:
a_sp = 0.5 * m * (Zs + Zp)        # sun-planet center distance (external mesh)
a_pr = 0.5 * m * (Zr - Zp)        # planet-ring center distance (internal mesh)
a_expected_equal = abs(a_sp - a_pr)

# Root space & tool check (heuristic)
p_circ = math.pi * m
estimated_root_space = root_space_factor * p_circ
m_required_for_tool = tool_diameter_mm / (root_space_factor * math.pi)

print("=== Inputs ===")
print(f"Module m = {m:.3f} mm, Pressure angle = {pa_deg:.1f}°")
print(f"Tooth counts: Sun Zs={Zs}, Planet Zp={Zp}, Ring Zr={Zr} (internal)")
print(f"Ring relation check: Zr ?= Zs + 2*Zp -> {Zr} vs {Zs + 2*Zp} (OK if equal)")
print()

print("=== Sun gear metrics (external) ===")
for k, v in sun.items():
    print(f"{k:>20}: {v:10.3f} mm" if isinstance(v,(int,float)) else f"{k:>20}: {v}")

print("\n=== Planet gear metrics (external) ===")
for k, v in planet.items():
    print(f"{k:>20}: {v:10.3f} mm" if isinstance(v,(int,float)) else f"{k:>20}: {v}")

print("\n=== Ring gear metrics (internal) ===")
for k, v in ring.items():
    print(f"{k:>20}: {v:10.3f} mm" if isinstance(v,(int,float)) else f"{k:>20}: {v}")

print("\n=== Mesh center distances ===")
print(f"Sun–Planet a_sp = 0.5*m*(Zs+Zp) = {a_sp:.3f} mm")
print(f"Planet–Ring a_pr = 0.5*m*(Zr−Zp) = {a_pr:.3f} mm")
print(f"|a_sp - a_pr| = {a_expected_equal:.6f} mm (should be ~0)")
print()

print("=== Tooth-root machining check (heuristic) ===")
print(f"Circular pitch p = π*m = {p_circ:.3f} mm")
print(f"Estimated root-space width ≈ {root_space_factor:.2f}·p = {estimated_root_space:.3f} mm")
print(f"3/16\" tool diameter = {tool_diameter_mm:.3f} mm")
if estimated_root_space >= tool_diameter_mm:
    print("OK: Estimated root space is >= tool diameter; 3/16\" flat end mill should enter the root.")
else:
    print("NOT OK: Estimated root space is < tool diameter; consider increasing module.")
    print(f"Minimum module so {root_space_factor}·π·m ≥ tool_dia: m ≥ {m_required_for_tool:.3f} mm")
    print(f"Try m = {max(2.75, round(m_required_for_tool, 2)):.2f}–{max(3.0, round(m_required_for_tool+0.1, 2)):.2f} mm and re-check.")

