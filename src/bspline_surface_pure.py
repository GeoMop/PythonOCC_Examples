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


def bezier_surfaces(event=None):
    """
    Create bezier surface, then create bspline surface from import
    it and search, what is inside created bspline surface.
    """
    array = TColgp_Array2OfPnt(1, 3, 1, 3)

    array.SetValue(1, 1, gp_Pnt(1, 1, 1))
    array.SetValue(1, 2, gp_Pnt(2, 1, 2))
    array.SetValue(1, 3, gp_Pnt(3, 1, 1))
    array.SetValue(2, 1, gp_Pnt(1, 2, 1))
    array.SetValue(2, 2, gp_Pnt(2, 2, 2))
    array.SetValue(2, 3, gp_Pnt(3, 2, 0))
    array.SetValue(3, 1, gp_Pnt(1, 3, 2))
    array.SetValue(3, 2, gp_Pnt(2, 3, 1))
    array.SetValue(3, 3, gp_Pnt(3, 3, 0))

    BZ1 = Geom_BezierSurface(array)

    bezierarray = TColGeom_Array2OfBezierSurface(1, 1, 1, 1)
    bezierarray.SetValue(1, 1, BZ1.GetHandle())
    BB = GeomConvert_CompBezierSurfacesToBSplineSurface(bezierarray)

    if BB.IsDone():
        # Poles
        poles = BB.Poles().GetObject().Array2()
        # print "poles: ", poles, poles.LowerCol(), poles.ColLength(), poles.LowerRow(), poles.RowLength()
        for pole_i in range(poles.LowerCol(), poles.ColLength() + 1, 1):
            for pole_j in range(poles.LowerRow(), poles.RowLength() + 1, 1):
                point = poles.Value(pole_i, pole_j)
                print(pole_i, pole_j, ": (", point.X(), point.Y(), point.Z(), ")")
        print()

        # Knots U and V
        uknots = BB.UKnots().GetObject().Array1()
        vknots = BB.VKnots().GetObject().Array1()
        print("uknots: ", uknots)
        for i in range(uknots.Lower(), uknots.Length() + 1, 1):
            print(uknots.Value(i))
        print("vknots: ", vknots)
        for j in range(vknots.Lower(), vknots.Length() + 1, 1):
            print(vknots.Value(j))
        print()

        # Multi U and V
        umult = BB.UMultiplicities().GetObject().Array1()
        vmult = BB.VMultiplicities().GetObject().Array1()
        print("umult: ", umult)
        for i in range(umult.Lower(), umult.Length() + 1, 1):
            print(umult.Value(i))
        print("vmult: ", vmult)
        for j in range(vmult.Lower(), vmult.Length() + 1, 1):
            print(vmult.Value(i))
        print()

        udeg = BB.UDegree()
        vdeg = BB.VDegree()
        print("udeg, vdeg: ", udeg, vdeg)

        BSPLSURF = Geom_BSplineSurface(poles, uknots, vknots, umult, vmult, udeg, vdeg, 0, 0)

    from OCC.Display.SimpleGui import init_display
    display, start_display, add_menu, add_function_to_menu = init_display()
    display.EraseAll()
    display.DisplayShape(BSPLSURF.GetHandle(), update=True)
    start_display()

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
    poles.SetValue(1, 1, gp_Pnt(1, 1, 1))
    poles.SetValue(1, 2, gp_Pnt(2, 1, 2))
    poles.SetValue(1, 3, gp_Pnt(3, 1, 1))
    poles.SetValue(2, 1, gp_Pnt(1, 2, 1))
    poles.SetValue(2, 2, gp_Pnt(2, 2, 2))
    poles.SetValue(2, 3, gp_Pnt(3, 2, 0))
    poles.SetValue(3, 1, gp_Pnt(1, 3, 2))
    poles.SetValue(3, 2, gp_Pnt(2, 3, 1))
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
    BSPLSURF = Geom_BSplineSurface(poles, uknots, vknots, umult, vmult, udeg, vdeg, uperiod, vperiod)

    # Display surface
    from OCC.Display.SimpleGui import init_display
    display, start_display, add_menu, add_function_to_menu = init_display()
    display.EraseAll()
    display.DisplayShape(BSPLSURF.GetHandle(), update=True)
    start_display()

if __name__ == '__main__':
    #bezier_surfaces()
    bspline_surface()