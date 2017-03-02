"""
This module is able to create simple solid object (cube). Each side of
cube is bspline surface. This solid object can be exported to BREP file.
"""

from __future__ import print_function

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
from OCC.BRepTools import BRepTools_ReShape
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

import brep_explorer

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
        bspline_surface = Geom_BSplineSurface( poles, uknots, vknots, umult, vmult, udeg, vdeg, False, False )
    return bspline_surface


def print_point(idx, point):
    print(idx, '->', point.X(), point.Y(), point.Z())


def make_box(builder, points):
    """
    Make box from 8 points
    """

    array1 = TColgp_Array2OfPnt(1, 2, 1, 2)
    array1.SetValue(1, 1, points[0])
    array1.SetValue(1, 2, points[1])
    array1.SetValue(2, 1, points[3])
    array1.SetValue(2, 2, points[2])
    bspl_surf1 = create_bspline_surface(array1)

    array2 = TColgp_Array2OfPnt(1, 2, 1, 2)
    array2.SetValue(1, 1, points[0])
    array2.SetValue(1, 2, points[4])
    array2.SetValue(2, 1, points[3])
    array2.SetValue(2, 2, points[7])
    bspl_surf2 = create_bspline_surface(array2)

    array3 = TColgp_Array2OfPnt(1, 2, 1, 2)
    array3.SetValue(1, 1, points[0])
    array3.SetValue(1, 2, points[4])
    array3.SetValue(2, 1, points[1])
    array3.SetValue(2, 2, points[5])
    bspl_surf3 = create_bspline_surface(array3)

    array4 = TColgp_Array2OfPnt(1, 2, 1, 2)
    array4.SetValue(1, 1, points[1])
    array4.SetValue(1, 2, points[5])
    array4.SetValue(2, 1, points[2])
    array4.SetValue(2, 2, points[6])
    bspl_surf4 = create_bspline_surface(array4)

    # One face split into the two faces

    # Wen need two new points somewhere inbetween
    point_23 = gp_Pnt(0.4 * points[2].X() + 0.6 * points[3].X(), points[2].Y(), points[2].Z())
    point_67 = gp_Pnt(0.4 * points[6].X() + 0.6 * points[7].X(), points[6].Y(), points[6].Z())

    print('Origin')
    for idx, point in enumerate(points):
        print_point(idx, point)

    print('Inbetween')
    print_point('23', point_23)
    print_point('67', point_67)

    # First splitted face
    array5_a = TColgp_Array2OfPnt(1, 2, 1, 2)
    array5_a.SetValue(1, 1, points[2])
    array5_a.SetValue(1, 2, points[6])
    array5_a.SetValue(2, 1, point_23)
    array5_a.SetValue(2, 2, point_67)
    bspl_surf5_a = create_bspline_surface(array5_a)

    # Second splitted face
    array5_b = TColgp_Array2OfPnt(1, 2, 1, 2)
    array5_b.SetValue(1, 1, point_23)
    array5_b.SetValue(1, 2, point_67)
    array5_b.SetValue(2, 1, points[3])
    array5_b.SetValue(2, 2, points[7])
    bspl_surf5_b = create_bspline_surface(array5_b)

    array6 = TColgp_Array2OfPnt(1, 2, 1, 2)
    array6.SetValue(1, 1, points[4])
    array6.SetValue(1, 2, points[5])
    array6.SetValue(2, 1, points[7])
    array6.SetValue(2, 2, points[6])
    bspl_surf6 = create_bspline_surface(array6)

    error = 1e-6
    face1 = BRepBuilderAPI_MakeFace(bspl_surf1.GetHandle(), error).Shape()
    face2 = BRepBuilderAPI_MakeFace(bspl_surf2.GetHandle(), error).Shape()
    face3 = BRepBuilderAPI_MakeFace(bspl_surf3.GetHandle(), error).Shape()
    face4 = BRepBuilderAPI_MakeFace(bspl_surf4.GetHandle(), error).Shape()
    face5_a = BRepBuilderAPI_MakeFace(bspl_surf5_a.GetHandle(), error).Shape()
    face5_b = BRepBuilderAPI_MakeFace(bspl_surf5_b.GetHandle(), error).Shape()
    face6 = BRepBuilderAPI_MakeFace(bspl_surf6.GetHandle(), error).Shape()

    sewing = BRepBuilderAPI_Sewing(0.01, True, True, True, False)
    sewing.SetFloatingEdgesMode(True)

    sewing.Add(face1)
    sewing.Add(face2)
    sewing.Add(face3)
    sewing.Add(face4)
    sewing.Add(face5_a)
    sewing.Add(face5_b)
    sewing.Add(face6)

    sewing.Perform()

    sewing_shape = sewing.SewedShape()

    print('>>>>',  sewing_shape)

    try:
        shell = topods_Shell(sewing_shape)
    except RuntimeError:
        return None, sewing_shape
    else:
        print('!!!!! Huraaaaaaaa !!!!!')

    make_solid = BRepBuilderAPI_MakeSolid()
    make_solid.Add(shell)

    solid = make_solid.Solid()

    builder.MakeSolid(solid)
    builder.Add(solid, shell)

    return solid, sewing_shape

def solid_compound(filename=None):
    """
    Generate and display solid object created from bspline surface.
    """
    display.EraseAll()

    # Create Builder first
    builder = BRep_Builder()

    points_1 = [
        gp_Pnt(0.0, 0.0, 0.0),
        gp_Pnt(1.0, 0.0, 0.0),
        gp_Pnt(1.0, 1.0, 0.0),
        gp_Pnt(0.0, 1.0, 0.0),
        gp_Pnt(0.0, 0.0, 1.0),
        gp_Pnt(1.0, 0.0, 1.0),
        gp_Pnt(1.0, 1.0, 1.0),
        gp_Pnt(0.0, 1.0, 1.0)
    ]
    solid_box, shape = make_box(builder, points_1)

    if solid_box is not None:
        compound = TopoDS_Compound()
        builder.MakeCompound(compound)

        builder.Add(compound, solid_box)

        print('Final compound')
        stat = brep_explorer.create_shape_stat(compound)
        brep_explorer.print_stat(stat)

        if filename is not None:
             breptools_Write(compound, filename)

    display.DisplayShape(shape, color='red', update=True)

    start_display()

if __name__ == '__main__':
    # Parse argument
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", type=str,
        help="Write Solid created form B-Spline surfaces to BREP file format", default=None)
    args = parser.parse_args()
    # Display and optionaly output surface to file (IGES file format)
    solid_compound(args.filename)