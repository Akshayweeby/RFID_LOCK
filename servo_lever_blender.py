"""Build the MG995 -> thumbturn lever arm in Blender and export it as STL.

Run headless:
    blender --background --python servo_lever_blender.py -- /path/to/out.stl

Dimensions match servo_lever.scad. They are ESTIMATES from the photos:
measure the real thumbturn and MG995 horn before printing.
"""
import math
import sys

import bpy
import bmesh

# ---- parameters (mm) -------------------------------------------------------
HORN_BORE_D = 5.2
HORN_SCREW_D = 3.2
HORN_PATTERN_R = 8.0
HUB_D = 16.0
ARM_T = 4.0
ARM_W = 14.0
END_D = ARM_W + 6.0
SPINDLE_D = 8.0
PADDLE_LEN = 40.0
PADDLE_W = 12.0
PADDLE_T = 6.0
CLEARANCE = 0.3
REACH = 60.0


def out_path():
    argv = sys.argv
    return argv[argv.index("--") + 1] if "--" in argv else "servo_lever.stl"


def cyl(name, d, h, x=0.0, y=0.0, z=0.0):
    bpy.ops.mesh.primitive_cylinder_add(radius=d / 2, depth=h, location=(x, y, z + h / 2))
    obj = bpy.context.active_object
    obj.name = name
    return obj


def arm_body():
    """Stadium-shaped arm: convex hull of the hub circle and the end circle.

    A boolean join of separate cylinders and a bar breaks the later cuts in
    Blender, so the arm is built as one convex mesh instead.
    """
    bm = bmesh.new()
    pts = []
    for cx, r in ((0.0, HUB_D / 2), (REACH, (ARM_W + 6) / 2)):
        for z in (0.0, ARM_T):
            for i in range(64):
                a = 2 * math.pi * i / 64
                pts.append(bm.verts.new((cx + r * math.cos(a), r * math.sin(a), z)))
    bmesh.ops.convex_hull(bm, input=pts)
    me = bpy.data.meshes.new("arm")
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new("servo_lever_arm", me)
    bpy.context.collection.objects.link(obj)
    return obj


def cut(target, cutter):
    mod = target.modifiers.new("cut", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = cutter
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def rhombus_prism(name, length, width, depth, z0, x=0.0):
    """Diamond-shaped prism (4-sided, rotated 45 deg) for the paddle pocket."""
    half_l, half_w = length / 2 + CLEARANCE, width / 2 + CLEARANCE
    verts = [(x + half_l, 0, z0), (x, half_w, z0), (x - half_l, 0, z0), (x, -half_w, z0)]
    verts += [(v[0], v[1], z0 + depth) for v in verts[:4]]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], [
        (0, 1, 2, 3), (7, 6, 5, 4),
        (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0),
    ])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def main():
    # Builds in the currently open scene. Nothing is cleared.
    arm = arm_body()

    # spline bore at the servo horn
    cut(arm, cyl("bore", HORN_BORE_D + 0.0, ARM_T + 2, z=-1))

    # four M3 holes on the horn pattern
    for a in (45, 135, 225, 315):
        rad = math.radians(a)
        cut(arm, cyl("m3", HORN_SCREW_D, ARM_T + 2,
                     x=HORN_PATTERN_R * math.cos(rad),
                     y=HORN_PATTERN_R * math.sin(rad), z=-1))

    # spindle bore at the far end
    cut(arm, cyl("spindle", SPINDLE_D + CLEARANCE, ARM_T + 2, x=REACH, z=-1))

    # paddle pocket, cut from the top face down through the paddle thickness
    cut(arm, rhombus_prism("pocket", PADDLE_LEN, PADDLE_W, PADDLE_T + 1,
                           z0=ARM_T - PADDLE_T, x=REACH))

    arm.name = "servo_lever_arm"
    print("Built servo_lever_arm in the current scene")

    # STL export only when a path is passed after "--"
    if "--" in sys.argv:
        bpy.ops.object.select_all(action="DESELECT")
        arm.select_set(True)
        bpy.context.view_layer.objects.active = arm
        bpy.ops.wm.stl_export(filepath=out_path(), export_selected_objects=True)
        print("Wrote", out_path())


main()
