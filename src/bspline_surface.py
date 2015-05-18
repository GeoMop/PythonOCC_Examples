"""
Small Modification of src/examples/Geometry/geometry_demos.py
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


def bezier_surfaces(event=None):
    display.EraseAll()
    array1 = TColgp_Array2OfPnt(1, 3, 1, 3)                              
    array2 = TColgp_Array2OfPnt(1, 3, 1, 3)                              
    array3 = TColgp_Array2OfPnt(1, 3, 1, 3)                            
    array4 = TColgp_Array2OfPnt(1, 3, 1, 3)                              

    array1.SetValue(1, 1, gp_Pnt(1, 1, 1))
    array1.SetValue(1, 2, gp_Pnt(2, 1, 2))
    array1.SetValue(1, 3, gp_Pnt(3, 1, 1))
    array1.SetValue(2, 1, gp_Pnt(1, 2, 1))
    array1.SetValue(2, 2, gp_Pnt(2, 2, 2))
    array1.SetValue(2, 3, gp_Pnt(3, 2, 0))
    array1.SetValue(3, 1, gp_Pnt(1, 3, 2))
    array1.SetValue(3, 2, gp_Pnt(2, 3, 1))
    array1.SetValue(3, 3, gp_Pnt(3, 3, 0))

    array2.SetValue(1, 1, gp_Pnt(3, 1, 1))
    array2.SetValue(1, 2, gp_Pnt(4, 1, 1))
    array2.SetValue(1, 3, gp_Pnt(5, 1, 2))
    array2.SetValue(2, 1, gp_Pnt(3, 2, 0))
    array2.SetValue(2, 2, gp_Pnt(4, 2, 1))
    array2.SetValue(2, 3, gp_Pnt(5, 2, 2))
    array2.SetValue(3, 1, gp_Pnt(3, 3, 0))
    array2.SetValue(3, 2, gp_Pnt(4, 3, 0))
    array2.SetValue(3, 3, gp_Pnt(5, 3, 1))

    array3.SetValue(1, 1, gp_Pnt(1, 3, 2))
    array3.SetValue(1, 2, gp_Pnt(2, 3, 1))
    array3.SetValue(1, 3, gp_Pnt(3, 3, 0))
    array3.SetValue(2, 1, gp_Pnt(1, 4, 1))
    array3.SetValue(2, 2, gp_Pnt(2, 4, 0))
    array3.SetValue(2, 3, gp_Pnt(3, 4, 1))
    array3.SetValue(3, 1, gp_Pnt(1, 5, 1))
    array3.SetValue(3, 2, gp_Pnt(2, 5, 1))
    array3.SetValue(3, 3, gp_Pnt(3, 5, 2))

    array4.SetValue(1, 1, gp_Pnt(3, 3, 0))
    array4.SetValue(1, 2, gp_Pnt(4, 3, 0))
    array4.SetValue(1, 3, gp_Pnt(5, 3, 1))
    array4.SetValue(2, 1, gp_Pnt(3, 4, 1))
    array4.SetValue(2, 2, gp_Pnt(4, 4, 1))
    array4.SetValue(2, 3, gp_Pnt(5, 4, 1))
    array4.SetValue(3, 1, gp_Pnt(3, 5, 2))
    array4.SetValue(3, 2, gp_Pnt(4, 5, 2))
    array4.SetValue(3, 3, gp_Pnt(5, 5, 1))

    BZ1 = Geom_BezierSurface(array1)
    BZ2 = Geom_BezierSurface(array2)
    BZ3 = Geom_BezierSurface(array3)
    BZ4 = Geom_BezierSurface(array4)

    bezierarray = TColGeom_Array2OfBezierSurface(1, 2, 1, 2)
    bezierarray.SetValue(1, 1, BZ1.GetHandle())
    bezierarray.SetValue(1, 2, BZ2.GetHandle())
    bezierarray.SetValue(2, 1, BZ3.GetHandle())
    bezierarray.SetValue(2, 2, BZ4.GetHandle())

    BB = GeomConvert_CompBezierSurfacesToBSplineSurface(bezierarray)
    if BB.IsDone():
        poles = BB.Poles().GetObject().Array2()
        uknots = BB.UKnots().GetObject().Array1()
        vknots = BB.VKnots().GetObject().Array1()
        umult = BB.UMultiplicities().GetObject().Array1()
        vmult = BB.VMultiplicities().GetObject().Array1()
        udeg = BB.UDegree()
        vdeg = BB.VDegree()

        BSPLSURF = Geom_BSplineSurface( poles, uknots, vknots, umult, vmult, udeg, vdeg, 0, 0 )
        BSPLSURF.Translate(gp_Vec(0,0,2))

    display.DisplayShape(BSPLSURF.GetHandle(), update=True)
    start_display()

if __name__ == '__main__':
    bezier_surfaces()