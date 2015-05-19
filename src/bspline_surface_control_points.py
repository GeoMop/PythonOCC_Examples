"""
Display control points of surface 
"""

from OCC.gp import *
from OCC.Geom import *
from OCC.TColGeom import *
from OCC.TColgp import * 
from OCC.GeomConvert import *
from OCC.BRepBuilderAPI import *
from OCC.TopoDS import *
from OCC.STEPControl import *
from OCC.Display.SimpleGui import init_display

display, start_display, add_menu, add_function_to_menu = init_display()

def bezier_surfaces():
    """
    Generate and display bspline surface with control points
    """
    display.EraseAll()
    array1 = TColgp_Array2OfPnt(1, 3, 1, 3)

    point = gp_Pnt(1, 1, -1)
    display.DisplayShape(point, update=False)
    array1.SetValue(1, 1, point)
    point = gp_Pnt(2, 1, 0)
    display.DisplayShape(point, update=False)
    array1.SetValue(1, 2, point)
    point = gp_Pnt(3, 1, -1)
    display.DisplayShape(point, update=False)
    array1.SetValue(1, 3, point)

    point = gp_Pnt(1, 2, 3)
    display.DisplayShape(point, update=False)
    array1.SetValue(2, 1, point)
    point = gp_Pnt(2, 2, 5)
    display.DisplayShape(point, update=False)
    array1.SetValue(2, 2, point)
    point = gp_Pnt(3, 2, 2)
    display.DisplayShape(point, update=False)
    array1.SetValue(2, 3, point)

    point = gp_Pnt(1, 3, 2)
    display.DisplayShape(point, update=False)
    array1.SetValue(3, 1, point)
    point = gp_Pnt(2, 3, 1)
    display.DisplayShape(point, update=False)
    array1.SetValue(3, 2, point)
    point = gp_Pnt(3, 3, 0)
    display.DisplayShape(point, update=False)
    array1.SetValue(3, 3, point)

    BZ1 = Geom_BezierSurface(array1)

    bezierarray = TColGeom_Array2OfBezierSurface(1, 1, 1, 1)
    bezierarray.SetValue(1, 1, BZ1.GetHandle())
    
    BB = GeomConvert_CompBezierSurfacesToBSplineSurface(bezierarray)
    if BB.IsDone():
        poles = BB.Poles().GetObject().Array2()
        print(type(poles))
        uknots = BB.UKnots().GetObject().Array1()
        print(type(uknots))
        vknots = BB.VKnots().GetObject().Array1()
        print(type(vknots))
        umult = BB.UMultiplicities().GetObject().Array1()
        vmult = BB.VMultiplicities().GetObject().Array1()
        udeg = BB.UDegree()
        vdeg = BB.VDegree()

        # Display control points of B-Spline surface
        #for i in range(poles.LowerRow(), poles.UpperRow() + 1):
        #    for j in range(poles.LowerCol(), poles.UpperCol() + 1):
        #        display.DisplayShape(poles.Value(i, j), update=False, color='GREEN')

        BSPLSURF = Geom_BSplineSurface( poles, uknots, vknots, umult, vmult, udeg, vdeg, 0, 0 )
        BSPLSURF.Translate(gp_Vec(0,0,2))

    display.DisplayShape(BSPLSURF.GetHandle(), update=True)
    start_display()

if __name__ == '__main__':
    bezier_surfaces()
