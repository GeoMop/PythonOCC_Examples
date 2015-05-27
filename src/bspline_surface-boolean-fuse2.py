"""
Simple example of bspline surface
"""

from OCC.gp import *
from OCC.Geom import *
from OCC.TColGeom import *
from OCC.TColgp import * 
from OCC.GeomConvert import *
from OCC.BRepBuilderAPI import *
from OCC.TopoDS import *
from OCC.STEPControl import *
from OCC.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.Display.SimpleGui import init_display
from OCC.IGESControl import *
import argparse

display, start_display, add_menu, add_function_to_menu = init_display()


def create_bspline_surface(array):
    """
    Create B-Spline surface from control points of Bezier surface
    """
    bspline_surface = None
    bezier_surface = Geom_BezierSurface(array)
    bezier_array = TColGeom_Array2OfBezierSurface(1, 1, 1, 1)
    bezier_array.SetValue(1, 1, bezier_surface.GetHandle())
    temp = GeomConvert_CompBezierSurfacesToBSplineSurface(bezier_array)
    if temp.IsDone():
        poles = temp.Poles().GetObject().Array2()
        uknots = temp.UKnots().GetObject().Array1()
        vknots = temp.VKnots().GetObject().Array1()
        umult = temp.UMultiplicities().GetObject().Array1()
        vmult = temp.VMultiplicities().GetObject().Array1()
        udeg = temp.UDegree()
        vdeg = temp.VDegree()
        bspline_surface = Geom_BSplineSurface( poles, uknots, vknots, umult, vmult, udeg, vdeg, 0, 0 )
    return bspline_surface


def bezier_surfaces(filename=None):
    """
    Generate and display bspline surface
    """
    display.EraseAll()

    array1 = TColgp_Array2OfPnt(1, 2, 1, 2)
    array1.SetValue(1, 1, gp_Pnt(0, 0, 0))
    array1.SetValue(1, 2, gp_Pnt(0, 1, 0))
    array1.SetValue(2, 1, gp_Pnt(0, 0, 1))
    array1.SetValue(2, 2, gp_Pnt(0, 1, 1))

    bspl_surf1 = create_bspline_surface(array1)

    #display.DisplayShape(bspl_surf1.GetHandle(), update=True)

    array2 = TColgp_Array2OfPnt(1, 2, 1, 2)
    array2.SetValue(1, 1, gp_Pnt( 0.5, 0.75, 0.5))
    array2.SetValue(1, 2, gp_Pnt( 0.5, 1.25, 0.5))
    array2.SetValue(2, 1, gp_Pnt(-0.5, 0.75, 0.5))
    array2.SetValue(2, 2, gp_Pnt(-0.5, 1.25, 0.5))

    bspl_surf2 = create_bspline_surface(array2)

    #display.DisplayShape(bspl_surf2.GetHandle(), update=True)

    error = 1e-6
    face1 = BRepBuilderAPI_MakeFace(bspl_surf1.GetHandle(), error).Shape()
    face2 = BRepBuilderAPI_MakeFace(bspl_surf2.GetHandle(), error).Shape()
    mold = BRepAlgoAPI_Fuse(face1, face2).Shape()

    if filename is not None:
        iges_ctrl  = IGESControl_Controller()
        iges_ctrl.Init()
        iges_writer = IGESControl_Writer()
        iges_writer.AddShape(mold)
        iges_writer.Write(filename)

    display.DisplayShape(mold, update=True)

    start_display()

if __name__ == '__main__':
    # Parse argument
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", type=str,
        help="Write B-Spline surface to IGES file format", default=None)
    args = parser.parse_args()
    # Display and optionaly output surface to file (IGES file format)
    bezier_surfaces(args.filename)