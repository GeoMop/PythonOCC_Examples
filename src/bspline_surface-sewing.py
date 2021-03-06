"""
This module is able to create simple solid object (cube). Each side of
cube is bspline surface. This solid object can be exported to BREP file.
"""

from OCC.gp import *
from OCC.Geom import *
from OCC.TColGeom import *
from OCC.TColgp import * 
from OCC.GeomConvert import *
from OCC.BRepBuilderAPI import *
from OCC.BRepFill import *
from OCC.BRep import *
from OCC.BRepPrimAPI import *
from OCC.BRepAlgoAPI import *
from OCC.TopoDS import *
from OCC.STEPControl import *
from OCC.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.BRepTools import breptools_Write
from OCC.Display.SimpleGui import init_display
from OCC.TopExp import TopExp_Explorer
from OCC.TopAbs import TopAbs_SHELL
from OCC.TopAbs import TopAbs_VERTEX
from OCC.TopAbs import TopAbs_EDGE
from OCC.TopAbs import TopAbs_WIRE
from OCC.ShapeFix import ShapeFix_Shell
from OCC.TopOpeBRepTool import TopOpeBRepTool_FuseEdges
from OCC.BRepBuilderAPI import BRepBuilderAPI_Sewing
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
    Generate and display solid object created from bspline surface.
    """
    display.EraseAll()

    # Create Builder first
    builder = BRep_Builder()

    point1 = gp_Pnt(0.0, 0.0, 0.0)
    point2 = gp_Pnt(1.0, 0.0, 0.0)
    point3 = gp_Pnt(1.0, 1.0, 0.0)
    point4 = gp_Pnt(0.0, 1.0, 0.0)
    point5 = gp_Pnt(0.0, 0.0, 1.0)
    point6 = gp_Pnt(1.0, 0.0, 1.0)
    point7 = gp_Pnt(1.0, 1.0, 1.0)
    point8 = gp_Pnt(0.0, 1.0, 1.0)

    array1 = TColgp_Array2OfPnt(1, 2, 1, 2)
    array1.SetValue(1, 1, point1)
    array1.SetValue(1, 2, point2)
    array1.SetValue(2, 1, point4)
    array1.SetValue(2, 2, point3)
    bspl_surf1 = create_bspline_surface(array1)

    array2 = TColgp_Array2OfPnt(1, 2, 1, 2)
    array2.SetValue(1, 1, point1)
    array2.SetValue(1, 2, point5)
    array2.SetValue(2, 1, point4)
    array2.SetValue(2, 2, point8)
    bspl_surf2 = create_bspline_surface(array2)

    array3 = TColgp_Array2OfPnt(1, 2, 1, 2)
    array3.SetValue(1, 1, point1)
    array3.SetValue(1, 2, point5)
    array3.SetValue(2, 1, point2)
    array3.SetValue(2, 2, point6)
    bspl_surf3 = create_bspline_surface(array3)

    array4 = TColgp_Array2OfPnt(1, 2, 1, 2)
    array4.SetValue(1, 1, point2)
    array4.SetValue(1, 2, point6)
    array4.SetValue(2, 1, point3)
    array4.SetValue(2, 2, point7)
    bspl_surf4 = create_bspline_surface(array4)

    array5 = TColgp_Array2OfPnt(1, 2, 1, 2)
    array5.SetValue(1, 1, point3)
    array5.SetValue(1, 2, point7)
    array5.SetValue(2, 1, point4)
    array5.SetValue(2, 2, point8)
    bspl_surf5 = create_bspline_surface(array5)

    array6 = TColgp_Array2OfPnt(1, 2, 1, 2)
    array6.SetValue(1, 1, point5)
    array6.SetValue(1, 2, point6)
    array6.SetValue(2, 1, point8)
    array6.SetValue(2, 2, point7)
    bspl_surf6 = create_bspline_surface(array6)

    error = 1e-6
    face1 = BRepBuilderAPI_MakeFace(bspl_surf1.GetHandle(), error).Shape()
    face2 = BRepBuilderAPI_MakeFace(bspl_surf2.GetHandle(), error).Shape()
    face3 = BRepBuilderAPI_MakeFace(bspl_surf3.GetHandle(), error).Shape()
    face4 = BRepBuilderAPI_MakeFace(bspl_surf4.GetHandle(), error).Shape()
    face5 = BRepBuilderAPI_MakeFace(bspl_surf5.GetHandle(), error).Shape()
    face6 = BRepBuilderAPI_MakeFace(bspl_surf6.GetHandle(), error).Shape()

    sewing = BRepBuilderAPI_Sewing(0.01, True, True, True, False)
    sewing.SetFloatingEdgesMode(True)

    sewing.Add(face1)
    sewing.Add(face2)
    sewing.Add(face3)
    sewing.Add(face4)
    sewing.Add(face5)
    sewing.Add(face6)

    sewing.Perform()
    print 'max tolerance:', sewing.MaxTolerance()
    print 'max tolerance:', sewing.Tolerance()
    print 'min tolerance:', sewing.MinTolerance()
    print 'n degenerated shapes:', sewing.NbDegeneratedShapes()
    print 'n deleted faces:', sewing.NbDeletedFaces()
    print 'n free edges:', sewing.NbFreeEdges()
    print 'n multiple edges:', sewing.NbMultipleEdges()

    sewing_shape = sewing.SewedShape()

    shell = topods_Shell(sewing_shape)

    make_solid = BRepBuilderAPI_MakeSolid()
    make_solid.Add(shell)

    solid = make_solid.Solid()

    builder.MakeSolid(solid)
    builder.Add(solid, shell)

    compound = TopoDS_Compound()

    builder.MakeCompound(compound)
    builder.Add(compound, solid)

    if filename is not None:
        breptools_Write(compound, filename)

    display.DisplayShape(shell, update=True)

    start_display()

if __name__ == '__main__':
    # Parse argument
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", type=str,
        help="Write Solid created form B-Spline surfaces to BREP file format", default=None)
    args = parser.parse_args()
    # Display and optionaly output surface to file (IGES file format)
    bezier_surfaces(args.filename)