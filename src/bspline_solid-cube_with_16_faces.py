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

from bspline_solid_boolean import remove_duple_face_shapes

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

    # Extruded verticies
    dy = 0.5
    point_20 = gp_Pnt(points[2].X(), points[2].Y() + dy, points[2].Z())
    point_30 = gp_Pnt(points[3].X(), points[3].Y() + dy, points[3].Z())
    point_70 = gp_Pnt(points[7].X(), points[7].Y() + dy, points[7].Z())
    point_60 = gp_Pnt(points[6].X(), points[6].Y() + dy, points[6].Z())
    point_230 = gp_Pnt(point_23.X(), point_23.Y() + dy, point_23.Z())
    point_670 = gp_Pnt(point_67.X(), point_67.Y() + dy, point_67.Z())

    # Extruded faces
    array7 = TColgp_Array2OfPnt(1, 2, 1, 2)
    array7.SetValue(1, 1, points[2])
    array7.SetValue(1, 2, point_20)
    array7.SetValue(2, 1, point_23)
    array7.SetValue(2, 2, point_230)
    bspl_surf7 = create_bspline_surface(array7)

    array8 = TColgp_Array2OfPnt(1, 2, 1, 2)
    array8.SetValue(1, 1, point_23)
    array8.SetValue(1, 2, point_230)
    array8.SetValue(2, 1, points[3])
    array8.SetValue(2, 2, point_30)
    bspl_surf8 = create_bspline_surface(array8)

    array9 = TColgp_Array2OfPnt(1, 2, 1, 2)
    array9.SetValue(1, 1, points[2])
    array9.SetValue(1, 2, points[6])
    array9.SetValue(2, 1, point_20)
    array9.SetValue(2, 2, point_60)
    bspl_surf9 = create_bspline_surface(array9)

    array10 = TColgp_Array2OfPnt(1, 2, 1, 2)
    array10.SetValue(1, 1, point_20)
    array10.SetValue(1, 2, point_60)
    array10.SetValue(2, 1, point_230)
    array10.SetValue(2, 2, point_670)
    bspl_surf10 = create_bspline_surface(array10)

    array11 = TColgp_Array2OfPnt(1, 2, 1, 2)
    array11.SetValue(1, 1, point_230)
    array11.SetValue(1, 2, point_670)
    array11.SetValue(2, 1, point_30)
    array11.SetValue(2, 2, point_70)
    bspl_surf11 = create_bspline_surface(array11)

    array12 = TColgp_Array2OfPnt(1, 2, 1, 2)
    array12.SetValue(1, 1, point_30)
    array12.SetValue(1, 2, point_70)
    array12.SetValue(2, 1, points[3])
    array12.SetValue(2, 2, points[7])
    bspl_surf12 = create_bspline_surface(array12)

    array13 = TColgp_Array2OfPnt(1, 2, 1, 2)
    array13.SetValue(1, 1, point_67)
    array13.SetValue(1, 2, point_670)
    array13.SetValue(2, 1, points[7])
    array13.SetValue(2, 2, point_70)
    bspl_surf13 = create_bspline_surface(array13)

    array14 = TColgp_Array2OfPnt(1, 2, 1, 2)
    array14.SetValue(1, 1, points[6])
    array14.SetValue(1, 2, point_60)
    array14.SetValue(2, 1, point_67)
    array14.SetValue(2, 2, point_670)
    bspl_surf14 = create_bspline_surface(array14)

    array15 = TColgp_Array2OfPnt(1, 2, 1, 2)
    array15.SetValue(1, 1, point_23)
    array15.SetValue(1, 2, point_67)
    array15.SetValue(2, 1, point_230)
    array15.SetValue(2, 2, point_670)
    bspl_surf15 = create_bspline_surface(array15)

    error = 1e-6
    face1 = BRepBuilderAPI_MakeFace(bspl_surf1.GetHandle(), error).Shape()
    face2 = BRepBuilderAPI_MakeFace(bspl_surf2.GetHandle(), error).Shape()
    face3 = BRepBuilderAPI_MakeFace(bspl_surf3.GetHandle(), error).Shape()
    face4 = BRepBuilderAPI_MakeFace(bspl_surf4.GetHandle(), error).Shape()
    face5_a = BRepBuilderAPI_MakeFace(bspl_surf5_a.GetHandle(), error).Shape()
    face5_b = BRepBuilderAPI_MakeFace(bspl_surf5_b.GetHandle(), error).Shape()
    face6 = BRepBuilderAPI_MakeFace(bspl_surf6.GetHandle(), error).Shape()
    face7 = BRepBuilderAPI_MakeFace(bspl_surf7.GetHandle(), error).Shape()
    face8 = BRepBuilderAPI_MakeFace(bspl_surf8.GetHandle(), error).Shape()
    face9 = BRepBuilderAPI_MakeFace(bspl_surf9.GetHandle(), error).Shape()
    face10 = BRepBuilderAPI_MakeFace(bspl_surf10.GetHandle(), error).Shape()
    face11 = BRepBuilderAPI_MakeFace(bspl_surf11.GetHandle(), error).Shape()
    face12 = BRepBuilderAPI_MakeFace(bspl_surf12.GetHandle(), error).Shape()
    face13 = BRepBuilderAPI_MakeFace(bspl_surf13.GetHandle(), error).Shape()
    face14 = BRepBuilderAPI_MakeFace(bspl_surf14.GetHandle(), error).Shape()
    face15 = BRepBuilderAPI_MakeFace(bspl_surf15.GetHandle(), error).Shape()

    # First sewing, shell, volume
    sewing1 = BRepBuilderAPI_Sewing(0.01, True, True, True, False)
    sewing1.SetFloatingEdgesMode(True)
    sewing1.Add(face1)
    sewing1.Add(face2)
    sewing1.Add(face3)
    sewing1.Add(face4)
    sewing1.Add(face5_a)
    sewing1.Add(face5_b)
    sewing1.Add(face6)
    sewing1.Perform()
    sewing1_shape = sewing1.SewedShape()

    try:
        shell1 = topods_Shell(sewing1_shape)
    except RuntimeError:
        return None, (sewing1_shape,)
    else:
        print('!!!!! Huraaaaaaaa !!!!!')

    make_solid1 = BRepBuilderAPI_MakeSolid()
    make_solid1.Add(shell1)
    solid1 = make_solid1.Solid()
    builder.MakeSolid(solid1)
    builder.Add(solid1, shell1)

    # Second sewing, shell, volume
    sewing2 = BRepBuilderAPI_Sewing(0.01, True, True, True, False)
    sewing2.SetFloatingEdgesMode(True)
    sewing2.Add(face7)
    sewing2.Add(face5_a)
    sewing2.Add(face9)
    sewing2.Add(face10)
    sewing2.Add(face15)
    sewing2.Add(face14)
    sewing2.Perform()
    sewing2_shape = sewing2.SewedShape()

    try:
        shell2 = topods_Shell(sewing2_shape)
    except RuntimeError:
        return None, (sewing2_shape,)
    else:
        print('!!!!! Huraaaaaaaa !!!!!')

    make_solid2 = BRepBuilderAPI_MakeSolid()
    make_solid2.Add(shell2)
    solid2 = make_solid2.Solid()
    builder.MakeSolid(solid2)
    builder.Add(solid2, shell2)

    # Third sewing, shell, volume
    sewing3 = BRepBuilderAPI_Sewing(0.01, True, True, True, False)
    sewing3.SetFloatingEdgesMode(True)
    sewing3.Add(face8)
    sewing3.Add(face5_b)
    sewing3.Add(face15)
    sewing3.Add(face11)
    sewing3.Add(face12)
    sewing3.Add(face13)
    sewing3.Perform()
    sewing3_shape = sewing3.SewedShape()

    try:
        shell3 = topods_Shell(sewing3_shape)
    except RuntimeError:
        return None, (sewing3_shape,)
    else:
        print('!!!!! Huraaaaaaaa !!!!!')

    make_solid3 = BRepBuilderAPI_MakeSolid()
    make_solid3.Add(shell3)
    solid3 = make_solid3.Solid()
    builder.MakeSolid(solid3)
    builder.Add(solid3, shell3)

    return (solid1, solid2, solid3), (sewing1_shape, sewing2_shape, sewing3_shape)

def solid_compound(filename=None):
    """
    Generate and display solid object created from bspline surface.
    """
    display.EraseAll()

    # Create Builder first
    builder = BRep_Builder()

    points_1 = [
        gp_Pnt(0.0, 0.0, 0.0),  # 0
        gp_Pnt(1.0, 0.0, 0.0),  # 1
        gp_Pnt(1.0, 0.5, 0.0),  # 2
        gp_Pnt(0.0, 0.5, 0.0),  # 3
        gp_Pnt(0.0, 0.0, 1.0),  # 4
        gp_Pnt(1.0, 0.0, 1.0),  # 5
        gp_Pnt(1.0, 0.5, 1.0),  # 6
        gp_Pnt(0.0, 0.5, 1.0),  # 8
    ]
    solids, shapes = make_box(builder, points_1)

    if solids is not None:
        compound = TopoDS_Compound()
        builder.MakeCompound(compound)

        solids, dup_faces, dup_edges = remove_duple_face_shapes(solids[0], solids[1])
        # solid_0, solid_2, dup_face = remove_duple_face_shapes(solid_0, solids[2])
        # solid_1, solid_2, dup_face = remove_duple_face_shapes(solid_1, solid_2)
        builder.Add(compound, solids[0])
        builder.Add(compound, solids[1])
        # builder.Add(compound, solid_2)
        # builder.Add(compound, solids[0])
        # builder.Add(compound, solids[1])
        # builder.Add(compound, solids[2])

        print('Final compound')
        stat = brep_explorer.create_shape_stat(compound)
        brep_explorer.print_stat(stat)

        if filename is not None:
             breptools_Write(compound, filename)

    # display.DisplayShape(solids[0], color='red', update=True)
    # display.DisplayShape(solids[1], color='blue', update=True)
    # display.DisplayShape(solid_2, color='green', update=True)

    # start_display()

if __name__ == '__main__':
    # Parse argument
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", type=str,
        help="Write Solid created form B-Spline surfaces to BREP file format", default=None)
    args = parser.parse_args()
    # Display and optionaly output surface to file (IGES file format)
    solid_compound(args.filename)