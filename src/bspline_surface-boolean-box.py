"""
Simple example of bspline surface, with output to IGES filename
and meshing using GMSH.
"""

from OCC.gp import *
from OCC.Geom import *
from OCC.TColGeom import *
from OCC.TColgp import * 
from OCC.GeomConvert import *
from OCC.BRepBuilderAPI import *
from OCC.TopoDS import *
from OCC.STEPControl import *
from OCC.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Display.SimpleGui import init_display
from OCC.IGESControl import *
import argparse
from subprocess import call


display, start_display, add_menu, add_function_to_menu = init_display()


GMSH_BIN="/home/jiri/Software/GMSH/gmsh-2.9.3-Linux/bin/gmsh"


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


def bezier_surfaces(filename=None, output=None):
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

    trns = gp_Trsf()
    trns.SetTranslation(gp_Vec(0, 0.25, 0.5))
    my_box = BRepPrimAPI_MakeBox(0.5, 0.5, 0.001).Shape()
    mold_basis = BRepBuilderAPI_Transform(my_box, trns).Shape()

    error = 1e-6
    face1 = BRepBuilderAPI_MakeFace(bspl_surf1.GetHandle(), error).Shape()
    mold = BRepAlgoAPI_Cut(face1, mold_basis).Shape()

    if filename is not None:
        iges_ctrl  = IGESControl_Controller()
        iges_ctrl.Init()
        iges_writer = IGESControl_Writer()
        iges_writer.AddShape(mold)
        iges_writer.Write(filename)
        # Meshing using GMSH
        if output is not None:
            call([GMSH_BIN, "-2", "-o", output, filename])

    display.DisplayShape(mold, update=True)

    start_display()

if __name__ == '__main__':
    # Parse argument
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", type=str,
        help="Write B-Spline surface to IGES file format", default=None)
    parser.add_argument("-o", "--output", type=str,
        help="Output file for meshing", default="output.msh")
    args = parser.parse_args()
    # Display and optionaly output surface to file (IGES file format)
    bezier_surfaces(args.filename, args.output)