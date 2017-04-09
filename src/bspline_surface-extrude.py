"""
Experiment with bezier surface and bspline surface
"""


from OCC.gp import *
from OCC.Geom import *
from OCC.TColGeom import *
from OCC.TColgp import * 
from OCC.TColStd import *
from OCC.GeomConvert import *
from OCC.BRepBuilderAPI import *
from OCC.TopoDS import *
from OCC.STEPControl import *
from OCC.BRep import *
import OCC.ShapeFix

from OCC.Display.SimpleGui import init_display
display, start_display, add_menu, add_function_to_menu = init_display()
display.EraseAll()

def extrude_edge(upole, uknots, umult, udeg, z_coord):
    """
    Try to extrude edge
    """

    # Non-periodic surface
    uperiod = False
    vperiod = False

    vdeg = 1
    
    # Create 2D array of poles (control points)
    poles = TColgp_Array2OfPnt(1, upole.Length(), 1, 2)
    for index in range(1, upole.Length() + 1):
        point = upole.Value(index)
        poles.SetValue(index, 1, point)
        poles.SetValue(index, 2, gp_Pnt(point.X(), point.Y(), point.Z() + z_coord))

    # Length of uknots and umult has to be same
    # Same rule is for vknots and vmult
    vknot_len = vmult_len = 2

    # Knots for V direction
    vknots = TColStd_Array1OfReal(1, vknot_len)

    # Main curves begins and ends at first and last points
    vknots.SetValue(1, 0.0)
    vknots.SetValue(2, 1.0)

    # Multiplicities for U and V direction
    vmult = TColStd_Array1OfInteger(1, vmult_len)

    # First and last multiplicities are set to udeg + 1 (vdeg respectively),
    # because we want main curves to start and finish on the first and
    # the last points
    vmult.SetValue(1, vdeg + 1)
    vmult.SetValue(2, vdeg + 1)

    # Some other rules, that has to hold:
    # poles.ColLength == sum(umult(i)) - udeg - 1 (e.g.: 3 == 6 - 2 - 1)

    # Try to create surface
    BSPLSURF = Geom_BSplineSurface(poles, uknots, vknots, umult, vmult, udeg, vdeg, uperiod, vperiod)
    return BSPLSURF

def cap_extrude(bspl_surf, z_coord):
    """
    Try to cap extrusion
    """
        # Non-periodic surface
    uperiod = False
    vperiod = False

    udeg = bspl_surf.UDegree()
    vdeg = bspl_surf.VDegree()

    nb_u_poles = bspl_surf.NbUPoles()
    nb_v_poles = bspl_surf.NbVPoles()

    poles = TColgp_Array2OfPnt(1, nb_u_poles, 1, nb_v_poles)
    bspl_surf.Poles(poles)
    new_poles = TColgp_Array2OfPnt(1, nb_u_poles, 1, nb_v_poles)

    nb_u_knots = nb_u_mults = bspl_surf.NbUKnots()
    nb_v_knots = nb_v_mults = bspl_surf.NbVKnots()
    uknots = TColStd_Array1OfReal(1, nb_u_knots)
    vknots = TColStd_Array1OfReal(1, nb_v_knots)
    umults = TColStd_Array1OfInteger(1, nb_u_mults)
    vmults = TColStd_Array1OfInteger(1, nb_v_mults)
    bspl_surf.UKnots(uknots)
    bspl_surf.VKnots(vknots)
    bspl_surf.VMultiplicities(umults)
    bspl_surf.VMultiplicities(vmults)

    # Set Z coordinate in poles
    for u_idx in range(1, nb_u_poles+1):
        for v_idx in range(1, nb_v_poles+1):
            _u_idx = nb_u_poles + 1 - u_idx
            _v_idx = nb_v_poles + 1 - v_idx
            point = poles.Value(_u_idx, _v_idx)
            new_poles.SetValue(u_idx, v_idx, OCC.gp.gp_Pnt(point.X(), point.Y(), point.Z() + z_coord))

    BSPLSURF = Geom_BSplineSurface(new_poles, uknots, vknots, umults, vmults, udeg, vdeg, uperiod, vperiod)
    return BSPLSURF

def extrude_surface(sewing, bspl_surf, z_coord):
    """Try to extrude """
    nb_u_poles = bspl_surf.NbUPoles()
    nb_v_poles = bspl_surf.NbVPoles()

    poles = TColgp_Array2OfPnt(1, nb_u_poles, 1, nb_v_poles)
    bspl_surf.Poles(poles)

    nb_u_knots = nb_u_mults = bspl_surf.NbUKnots()
    uknots = TColStd_Array1OfReal(1, nb_u_knots)
    umults = TColStd_Array1OfInteger(1, nb_u_mults)
    bspl_surf.UKnots(uknots)
    bspl_surf.UMultiplicities(umults)

    error = 1e-6
    # 1: Extrude one border edge
    edge = TColgp_Array1OfPnt(1, nb_u_poles)
    for index in range(1, nb_u_poles+1):
        _index = nb_u_poles + 1 - index
        edge.SetValue(index, poles.Value(1, _index))
    extruded_surf = extrude_edge(edge, uknots, umults, bspl_surf.UDegree(), z_coord)
    # extruded_surf.ExchangeUV()
    face = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeFace(extruded_surf.GetHandle(), error).Shape()
    sewing.Add(face)

    # 2: Extrude one border edge
    edge = TColgp_Array1OfPnt(1, nb_u_poles)
    for index in range(1, nb_u_poles+1):
        edge.SetValue(index, poles.Value(nb_v_poles, index))
    extruded_surf = extrude_edge(edge, uknots, umults, bspl_surf.UDegree(), z_coord)
    # extruded_surf.ExchangeUV()
    face = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeFace(extruded_surf.GetHandle(), error).Shape()
    sewing.Add(face)

    # 3: Extrude one border edge
    edge = TColgp_Array1OfPnt(1, nb_v_poles)
    for index in range(1, nb_v_poles+1):
        edge.SetValue(index, poles.Value(index, 1))
    extruded_surf = extrude_edge(edge, uknots, umults, bspl_surf.UDegree(), z_coord)
    # extruded_surf.ExchangeUV()
    face = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeFace(extruded_surf.GetHandle(), error).Shape()
    sewing.Add(face)

    # 4: Extrude one border edge
    edge = TColgp_Array1OfPnt(1, nb_v_poles)
    for index in range(1, nb_v_poles+1):
        _index = nb_v_poles + 1 - index
        edge.SetValue(index, poles.Value(_index, nb_u_poles))
    extruded_surf = extrude_edge(edge, uknots, umults, bspl_surf.UDegree(), z_coord)
    # extruded_surf.ExchangeUV()
    face = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeFace(extruded_surf.GetHandle(), error).Shape()
    sewing.Add(face)

    # Cap it
    cap_surf = cap_extrude(bspl_surf, z_coord)
    face = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeFace(cap_surf.GetHandle(), error).Shape()
    sewing.Add(face)

def bspline_surface():
    """
    Try to create B-spline surface directly
    """

    # Set U and V degree to 2
    udeg = 2
    vdeg = 2

    # Non-periodic surface
    uperiod = False
    vperiod = False

    # Create 2D array of poles (control points)
    poles = TColgp_Array2OfPnt(1, udeg + 1, 1, vdeg + 1)
    # 1
    poles.SetValue(1, 1, gp_Pnt(1, 1, 1))
    poles.SetValue(1, 2, gp_Pnt(3, 1, 2))
    poles.SetValue(1, 3, gp_Pnt(6, 1, 1))
    # 2
    poles.SetValue(2, 1, gp_Pnt(1, 2, 1))
    poles.SetValue(2, 2, gp_Pnt(3, 2, 2))
    poles.SetValue(2, 3, gp_Pnt(6, 2, 0))
    # 3
    poles.SetValue(3, 1, gp_Pnt(1, 3, 2))
    poles.SetValue(3, 2, gp_Pnt(3, 3, 2))
    poles.SetValue(3, 3, gp_Pnt(6, 3, 0))

    # Length of uknots and umult has to be same
    # Same rule is for vknots and vmult
    uknot_len = umult_len = 2
    vknot_len = vmult_len = 2

    # Knots for U and V direction
    uknots = TColStd_Array1OfReal(1, uknot_len)
    vknots = TColStd_Array1OfReal(1, vknot_len)

    # Main curves begins and ends at first and last points
    uknots.SetValue(1, 0.0)
    uknots.SetValue(2, 1.0)
    vknots.SetValue(1, 0.0)
    vknots.SetValue(2, 1.0)

    # Multiplicities for U and V direction
    umult = TColStd_Array1OfInteger(1, umult_len)
    vmult = TColStd_Array1OfInteger(1, vmult_len)

    # First and last multiplicities are set to udeg + 1 (vdeg respectively),
    # because we want main curves to start and finish on the first and
    # the last points
    umult.SetValue(1, udeg + 1)
    umult.SetValue(2, udeg + 1)
    vmult.SetValue(1, vdeg + 1)
    vmult.SetValue(2, vdeg + 1)

    # Some other rules, that has to hold:
    # poles.ColLength == sum(umult(i)) - udeg - 1 (e.g.: 3 == 6 - 2 - 1)

    # Try to create surface
    bspl_surf = Geom_BSplineSurface(poles, uknots, vknots, umult, vmult, udeg, vdeg, uperiod, vperiod)

    return bspl_surf

if __name__ == '__main__':
    bspl_surf = bspline_surface()
    sewing = OCC.BRepBuilderAPI.BRepBuilderAPI_Sewing(0.01, True, True, True, False)
    sewing.SetFloatingEdgesMode(True)
    error = 1e-6
    face = OCC.BRepBuilderAPI.BRepBuilderAPI_MakeFace(bspl_surf.GetHandle(), error).Shape()
    sewing.Add(face)
    extrude_surface(sewing, bspl_surf, -1.0)
    sewing.Perform()
    sewing_shape = sewing.SewedShape()
    shell = topods_Shell(sewing_shape)

    # Try to fix normals
    shape_fix = OCC.ShapeFix.ShapeFix_Shell(shell)
    shape_fix.FixFaceOrientation(shell)
    shape_fix.Perform()

    make_solid = BRepBuilderAPI_MakeSolid()
    make_solid.Add(shell)

    solid = make_solid.Solid()

    builder = BRep_Builder()
    builder.MakeSolid(solid)
    builder.Add(solid, shell)

    compound = TopoDS_Compound()

    builder.MakeCompound(compound)
    builder.Add(compound, solid)

    from OCC.BRepTools import breptools_Write
    breptools_Write(compound, 'extrude.brep')

    display.DisplayShape(shell, update=True)
    start_display()