import FreeCAD as App

# --------------------------------------------------------------------
# Fetch the two objects from the document by name
binder_object = App.ActiveDocument.getObject("Binder")
offset_object = App.ActiveDocument.getObject("Offset2D")

if binder_object is None or offset_object is None:
    raise RuntimeError("Could not find 'Binder' or 'Offset2D' in the document")

# --------------------------------------------------------------------
# Utility functions

def get_global_rotation(freecad_object):
    """
    Return the object's rotation in global/world coordinates.
    Some objects (like Links) support getGlobalPlacement().
    If not, fall back to the object's local Placement.Rotation.
    """
    get_global = getattr(freecad_object, "getGlobalPlacement", None)
    return get_global().Rotation if callable(get_global) else freecad_object.Placement.Rotation


def calculate_delta_rotation(rotation_from, rotation_to):
    """
    Compute the rotation that transforms orientation 'rotation_from' into 'rotation_to'.
    Formula: Δ = (rotation_from)⁻¹ * rotation_to
    """
    rotation_inverse = App.Rotation(rotation_from)  # copy rotation_from
    rotation_inverse.invert()                       # invert it → (rotation_from)⁻¹
    return rotation_inverse.multiply(rotation_to)   # result = inverse * rotation_to


def print_rotation_info(label, rotation):
    """
    Print rotation info in both Euler angles (Yaw, Pitch, Roll)
    and axis-angle representation.
    """
    yaw, pitch, roll = rotation.toEuler()
    axis = rotation.Axis
    angle = rotation.Angle
    print(f"{label}: "
          f"YPR=({yaw:.3f}, {pitch:.3f}, {roll:.3f}) "
          f"axis=({axis.x:.3f}, {axis.y:.3f}, {axis.z:.3f}) "
          f"angle={angle:.3f}°")

# --------------------------------------------------------------------
# Compare Binder vs Offset2D

binder_rotation = get_global_rotation(binder_object)   # global rotation of Binder
offset_rotation = get_global_rotation(offset_object)   # global rotation of Offset2D

# Δ Binder→Offset2D = rotation that maps Binder’s orientation to Offset2D’s orientation
delta_rotation = calculate_delta_rotation(binder_rotation, offset_rotation)

print("== Global Placement Rotations ==")
print_rotation_info("Binder", binder_rotation)
print_rotation_info("Offset2D", offset_rotation)
print_rotation_info("Δ Binder→Offset2D", delta_rotation)

# --------------------------------------------------------------------
# Align Offset2D to Binder (overwrite rotation so they match)
print("\nAligning Offset2D rotation to Binder...")
offset_object.Placement.Rotation = binder_rotation
App.ActiveDocument.recompute()

# --------------------------------------------------------------------
# Verify the alignment
new_offset_rotation = get_global_rotation(offset_object)
new_delta_rotation = calculate_delta_rotation(binder_rotation, new_offset_rotation)

print("\n== After Alignment ==")
print_rotation_info("Offset2D (new)", new_offset_rotation)
print_rotation_info("Δ Binder→Offset2D", new_delta_rotation)
