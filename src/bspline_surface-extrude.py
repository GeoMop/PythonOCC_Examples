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
    
    print "poles"
    # Create 2D array of poles (control points)
    poles = TColgp_Array2OfPnt(1, upole.Length(), 1, 2)
    for index in range(1, upole.Length() + 1):
        point = upole.Value(index)
        poles.SetValue(index, 1, point)
        poles.SetValue(index, 2, gp_Pnt(point.X(), point.Y(), z_coord))

    # Length of uknots and umult has to be same
    # Same rule is for vknots and vmult
    vknot_len = vmult_len = 2

    # Knots for V direction
    vknots = TColStd_Array1OfReal(1, vknot_len)

    print "knots"
    # Main curves begins and ends at first and last points
    vknots.SetValue(1, 0.0)
    vknots.SetValue(2, 1.0)

    # Multiplicities for U and V direction
    vmult = TColStd_Array1OfInteger(1, vmult_len)

    print "mults"
    # First and last multiplicities are set to udeg + 1 (vdeg respectively),
    # because we want main curves to start and finish on the first and
    # the last points
    vmult.SetValue(1, vdeg + 1)
    vmult.SetValue(2, vdeg + 1)

    # Some other rules, that has to hold:
    # poles.ColLength == sum(umult(i)) - udeg - 1 (e.g.: 3 == 6 - 2 - 1)

    # Try to create surface
    BSPLSURF = Geom_BSplineSurface(poles, uknots, vknots, umult, vmult, udeg, vdeg, uperiod, vperiod)

    display.DisplayShape(BSPLSURF.GetHandle(), update=True)

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
    for u_val in range(1, nb_u_poles+1):
        for v_val in range(1, nb_v_poles+1):
            point = poles.Value(u_val, v_val)
            poles.SetValue(u_val, v_val, OCC.gp.gp_Pnt(point.X(), point.Y(), z_coord))

    BSPLSURF = Geom_BSplineSurface(poles, uknots, vknots, umults, vmults, udeg, vdeg, uperiod, vperiod)
    display.DisplayShape(BSPLSURF.GetHandle(), update=True)

def extrude_surface(bspl_surf, z_coord):
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

    # 1: Extrude one border edge
    edge = TColgp_Array1OfPnt(1, nb_u_poles)
    for index in range(1, nb_u_poles+1):
        edge.SetValue(index, poles.Value(1, index))
    extrude_edge(edge, uknots, umults, bspl_surf.UDegree(), z_coord)

    # 2: Extrude one border edge
    edge = TColgp_Array1OfPnt(1, nb_u_poles)
    for index in range(1, nb_u_poles+1):
        edge.SetValue(index, poles.Value(nb_v_poles, index))
    extrude_edge(edge, uknots, umults, bspl_surf.UDegree(), z_coord)

    # 3: Extrude one border edge
    edge = TColgp_Array1OfPnt(1, nb_v_poles)
    for index in range(1, nb_v_poles+1):
        edge.SetValue(index, poles.Value(index, 1))
    extrude_edge(edge, uknots, umults, bspl_surf.UDegree(), z_coord)

    # 2: Extrude one border edge
    edge = TColgp_Array1OfPnt(1, nb_v_poles)
    for index in range(1, nb_v_poles+1):
        edge.SetValue(index, poles.Value(index, nb_u_poles))
    extrude_edge(edge, uknots, umults, bspl_surf.UDegree(), z_coord)

    # Cap it
    cap_extrude(bspl_surf, z_coord)

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
    poles.SetValue(1, 2, gp_Pnt(2, 1, 2))
    poles.SetValue(1, 3, gp_Pnt(3, 1, 1))
    # 2
    poles.SetValue(2, 1, gp_Pnt(1, 2, 1))
    poles.SetValue(2, 2, gp_Pnt(2, 2, 2))
    poles.SetValue(2, 3, gp_Pnt(3, 2, 0))
    # 3
    poles.SetValue(3, 1, gp_Pnt(1, 3, 2))
    poles.SetValue(3, 2, gp_Pnt(2, 3, 2))
    poles.SetValue(3, 3, gp_Pnt(3, 3, 0))

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

    display.DisplayShape(bspl_surf.GetHandle(), update=True)

    return bspl_surf

if __name__ == '__main__':
    bspl_surf = bspline_surface()
    extrude_surface(bspl_surf, -1.0)
    start_display()