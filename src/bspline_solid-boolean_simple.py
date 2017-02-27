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
import core_topology_traverse as traverse

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

    array5 = TColgp_Array2OfPnt(1, 2, 1, 2)
    array5.SetValue(1, 1, points[2])
    array5.SetValue(1, 2, points[6])
    array5.SetValue(2, 1, points[3])
    array5.SetValue(2, 2, points[7])
    bspl_surf5 = create_bspline_surface(array5)

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

    sewing_shape = sewing.SewedShape()

    shell = topods_Shell(sewing_shape)

    make_solid = BRepBuilderAPI_MakeSolid()
    make_solid.Add(shell)

    solid = make_solid.Solid()

    builder.MakeSolid(solid)
    builder.Add(solid, shell)

    return solid


def compare_quads(face1, face2):
    """
    Compate two faces
    """

    for vert in face1:
        if vert not in face2:
            return False

    return True


def remove_duple_faces(reshape, faces, new_face, face_shape):
    """
    """
    for face in faces.keys():
        if compare_quads(face, new_face) is True:
            original_face = faces[new_face]
            print('Duplicity of: ', original_face)
            print('Removing this face ...')
            reshape.Replace(face_shape, original_face.Reversed())
            return True
    return False


def find_slitted_face():
    """
    """


def solid_compound(filename=None):
    """
    Generate and display solid object created from bspline surface.
    """

    # Create Builder first
    builder = BRep_Builder()

    # Base box
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
    solid_box1 = make_box(builder, points_1)

    # Definition of boxes usd for spliting base box
    dx = 0.4
    dy = 0.01
    dz = 0.01
    points_2 = [
        gp_Pnt(0.0+dx, 0.0-dy, 0.0-dz),
        gp_Pnt(1.0+dx, 0.0-dy, 0.0-dz),
        gp_Pnt(1.0+dx, 1.0+dy, 0.0-dz),
        gp_Pnt(0.0+dx, 1.0+dy, 0.0-dz),
        gp_Pnt(0.0+dx, 0.0-dy, 1.0+dz),
        gp_Pnt(1.0+dx, 0.0-dy, 1.0+dz),
        gp_Pnt(1.0+dx, 1.0+dy, 1.0+dz),
        gp_Pnt(0.0+dx, 1.0+dy, 1.0+dz)
    ]
    solid_box2 = make_box(builder, points_2)
    dx = 1 - 0.4
    points_3 = [
        gp_Pnt(0.0-dx, 0.0-dy, 0.0-dz),
        gp_Pnt(1.0-dx, 0.0-dy, 0.0-dz),
        gp_Pnt(1.0-dx, 1.0+dy, 0.0-dz),
        gp_Pnt(0.0-dx, 1.0+dy, 0.0-dz),
        gp_Pnt(0.0-dx, 0.0-dy, 1.0+dz),
        gp_Pnt(1.0-dx, 0.0-dy, 1.0+dz),
        gp_Pnt(1.0-dx, 1.0+dy, 1.0+dz),
        gp_Pnt(0.0-dx, 1.0+dy, 1.0+dz)
    ]
    solid_box3 = make_box(builder, points_3)

    mold1 = BRepAlgoAPI_Cut(solid_box1, solid_box2)
    mold2 = BRepAlgoAPI_Cut(solid_box1, solid_box3)

    print('Mold1')
    stat = brep_explorer.create_shape_stat(mold1.Shape())
    brep_explorer.print_stat(stat)
    # print('Mold2')
    # stat = brep_explorer.create_shape_stat(mold2.Shape())
    # brep_explorer.print_stat(stat)

    # sewing = BRepBuilderAPI_Sewing(0.01, True, True, True, True)
    # sewing.SetFloatingEdgesMode(True)
    # sewing.SetNonManifoldMode(True)
    # sewing.SetFaceMode(True)
    # sewing.Add(mold1.Shape())
    # sewing.Add(mold2.Shape())
    # sewing.Perform()

    # sewing_shape = sewing.SewedShape()

    # print('Sewing')
    # stat = brep_explorer.create_shape_stat(sewing_shape)
    # brep_explorer.print_stat(stat)

    primitives = brep_explorer.shapes_disassembly((mold1.Shape(), mold2.Shape()))
    print(primitives)
    faces = {}
    brt = BRep_Tool()
    reshape = BRepTools_ReShape()
    for face_shape in primitives[4].values():
        print(face_shape)
        face_traverse = traverse.Topo(face_shape)
        vertices = face_traverse.vertices_from_face(face_shape)
        points = []
        for idx,vert in enumerate(vertices):
            pnt = brt.Pnt(topods_Vertex(vert))
            # print(idx, pnt.X(), pnt.Y(), pnt.Z())
            points.append((pnt.X(), pnt.Y(), pnt.Z()))
        new_face = tuple(sorted(points))
        if remove_duple_faces(reshape, faces, new_face, face_shape) is False:
            faces[new_face] = face_shape
    for key in faces.keys():
        print(key)

    # Reshaping sewing object
    #new_shape = reshape.Apply(sewing_shape)
    new_mold1 = reshape.Apply(mold1.Shape())
    new_mold2 = reshape.Apply(mold2.Shape())

    shape_type = new_mold1.ShapeType()
    print(shape_type, brep_explorer.SHAPE_NAMES[shape_type])

    print('Reshaped Mol1')
    stat1 = brep_explorer.create_shape_stat(new_mold1)
    brep_explorer.print_stat(stat1)

    print('Reshaped Mol2')
    stat2 = brep_explorer.create_shape_stat(new_mold2)
    brep_explorer.print_stat(stat2)

    compound = TopoDS_Compound()
    builder.MakeCompound(compound)
    builder.Add(compound, new_mold1)
    builder.Add(compound, new_mold2)

    print('Final compound')
    stat = brep_explorer.create_shape_stat(compound)
    brep_explorer.print_stat(stat)

    if filename is not None:
         breptools_Write(compound, filename)

    display, start_display, add_menu, add_function_to_menu = init_display()
    display.EraseAll()

    display.DisplayShape(mold1.Shape(), color='red', update=True)
    display.DisplayShape(mold2.Shape(), color='blue', update=True)

    start_display()

if __name__ == '__main__':
    # Parse argument
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", type=str,
        help="Write Solid created form B-Spline surfaces to BREP file format", default=None)
    args = parser.parse_args()
    # Display and optionaly output surface to file (IGES file format)
    solid_compound(args.filename)