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


def create_test_boxes(builder):
    """
    Create several boxes for testing purpose
    """

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

    # Definition of boxes used for spliting base box
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

    # Definition of boxes used for spliting one part of slitted box
    dx = 0.01
    dy = 0.7
    dz = 0.01
    points_4 = [
        gp_Pnt(0.0-dx, 0.0+dy, 0.0-dz),
        gp_Pnt(1.0+dx, 0.0+dy, 0.0-dz),
        gp_Pnt(1.0+dx, 1.0+dy, 0.0-dz),
        gp_Pnt(0.0-dx, 1.0+dy, 0.0-dz),
        gp_Pnt(0.0-dx, 0.0+dy, 1.0+dz),
        gp_Pnt(1.0+dx, 0.0+dy, 1.0+dz),
        gp_Pnt(1.0+dx, 1.0+dy, 1.0+dz),
        gp_Pnt(0.0-dx, 1.0+dy, 1.0+dz)
    ]
    solid_box4 = make_box(builder, points_4)

    dy = 1.0 - dy
    points_5 = [
        gp_Pnt(0.0-dx, 0.0-dy, 0.0-dz),
        gp_Pnt(1.0+dx, 0.0-dy, 0.0-dz),
        gp_Pnt(1.0+dx, 1.0-dy, 0.0-dz),
        gp_Pnt(0.0-dx, 1.0-dy, 0.0-dz),
        gp_Pnt(0.0-dx, 0.0-dy, 1.0+dz),
        gp_Pnt(1.0+dx, 0.0-dy, 1.0+dz),
        gp_Pnt(1.0+dx, 1.0-dy, 1.0+dz),
        gp_Pnt(0.0-dx, 1.0-dy, 1.0+dz)
    ]
    solid_box5 = make_box(builder, points_5)

    return solid_box1, solid_box2, solid_box3, solid_box4, solid_box5


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
    Try to remove duplicity faces from two boolean operations
    """
    for face in faces.keys():
        if compare_quads(face, new_face) is True:
            original_face = faces[new_face]
            print('Duplicity of: ', original_face)
            print('Removing this face ...')
            reshape.Replace(face_shape, original_face.Reversed())
            return True
    return False


def remove_duple_face_shapes(shape1, shape2):
    """
    Try to remove duplicated faces in two shapes
    """
    primitives = brep_explorer.shapes_disassembly((shape1, shape2))
    # print(primitives)
    faces = {}
    brt = BRep_Tool()
    reshape = BRepTools_ReShape()
    dupli_faces = []
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
        else:
            dupli_faces.append(face_shape)
    # for key in faces.keys():
    #     print(key)

    print("Dupli faces:", dupli_faces)
    dup_face = dupli_faces[0]

    # Reshaping sewing object
    new_shape1 = reshape.Apply(shape1)
    new_shape2 = reshape.Apply(shape2)

    return new_shape1, new_shape2, dup_face


def find_intersected_bordering_faces(face, volume1, volume2, hint_face):
    """
    Try to find bordering faces
    """
    primitives = brep_explorer.shape_disassembly(face)
    # print('>>>> Disassembly face:')
    # stat = brep_explorer.create_shape_stat(face)
    # brep_explorer.print_stat(stat)
    from OCC.TopoDS import topods_Edge
    print('>>> Edges:')
    brt = BRep_Tool()
    for edge_shape in primitives[6].values():
        edge = TopoDS_Edge(edge_shape)
        print('>>> TopoDS_Edge:', edge)
        print(dir(edge))
        print('>>>>>> edge_shape:', edge_shape)
        print(edge_shape.ShapeType(), edge_shape.TShape())
        # print(dir(edge_shape.TShape()))
        # print(edge_shape.TShape().DownCast(TopoDS_Edge))
        print(dir(edge_shape))
        curve_handle = brt.Curve(edge_shape)[0]
        print(curve_handle)
        curve = curve_handle.GetObject()
        print(curve)
        # edge_traverse = traverse.Topo(edge_shape)
        # vertices = edge_traverse.vertices_from_edge(edge_shape)
        # for idx,vert in enumerate(vertices):
        #     pnt = brt.Pnt(topods_Vertex(vert))
        #     print(idx, pnt.X(), pnt.Y(), pnt.Z())
    return None, None



def solid_compound(filename=None):
    """
    Generate and display solid object created from bspline surface.
    """

    # Create Builder first
    builder = BRep_Builder()

    solid_box1, solid_box2, solid_box3, solid_box4, solid_box5 = create_test_boxes(builder)

    mold1 = BRepAlgoAPI_Cut(solid_box1, solid_box2)
    mold2 = BRepAlgoAPI_Cut(solid_box1, solid_box3)

    # print('Mold1')
    # stat = brep_explorer.create_shape_stat(mold1.Shape())
    # brep_explorer.print_stat(stat)
    # print('Mold2')
    # stat = brep_explorer.create_shape_stat(mold2.Shape())
    # brep_explorer.print_stat(stat)

    new_mold1, new_mold2, dup_face1 = remove_duple_face_shapes(mold1.Shape(), mold2.Shape())

    # shape_type = new_mold1.ShapeType()
    # print(shape_type, brep_explorer.SHAPE_NAMES[shape_type])

    print('Reshaped Mol1')
    stat1 = brep_explorer.create_shape_stat(new_mold1)
    brep_explorer.print_stat(stat1)

    print('Reshaped Mol2')
    stat2 = brep_explorer.create_shape_stat(new_mold2)
    brep_explorer.print_stat(stat2)

    # Important note: it is necessary to do "cutting" on shape without removed
    # doubles. In this case you have to use mold2, NOT new_mold. Otherwise it
    # will create strange results
    mold3 = BRepAlgoAPI_Cut(mold2.Shape(), solid_box4)
    mold4 = BRepAlgoAPI_Cut(mold2.Shape(), solid_box5)

    new_mold3, new_mold4, dup_face2 = remove_duple_face_shapes(mold3.Shape(), mold4.Shape())

    print('Reshaped Mol3')
    stat3 = brep_explorer.create_shape_stat(new_mold3)
    brep_explorer.print_stat(stat3)

    print('Reshaped Mol4')
    stat4 = brep_explorer.create_shape_stat(new_mold4)
    brep_explorer.print_stat(stat4)

    compound = TopoDS_Compound()
    builder.MakeCompound(compound)
    builder.Add(compound, new_mold1)
    # builder.Add(compound, new_mold2) ... replaced by modl3 and mold4
    builder.Add(compound, new_mold3)
    builder.Add(compound, new_mold4)

    # Try to find two intersection points
    # iface1, iface2 = find_intersected_bordering_faces(dup_face1, new_mold3, new_mold4, dup_face2)

    print('Final compound')
    stat = brep_explorer.create_shape_stat(compound)
    brep_explorer.print_stat(stat)

    if filename is not None:
         breptools_Write(compound, filename)

    display, start_display, add_menu, add_function_to_menu = init_display()
    display.EraseAll()

    ais_shell = display.DisplayShape(new_mold1, color='red', update=True)
    display.Context.SetTransparency(ais_shell, 0.7)
    # ais_shell = display.DisplayShape(new_mold2, color='blue', update=True)
    # display.Context.SetTransparency(ais_shell, 0.7)
    ais_shell = display.DisplayShape(new_mold3, color='blue', update=True)
    display.Context.SetTransparency(ais_shell, 0.7)
    ais_shell = display.DisplayShape(new_mold4, color='yellow', update=True)
    display.Context.SetTransparency(ais_shell, 0.7)
    # ais_shell = display.DisplayShape(mold4.Shape(), color='yellow', update=True)
    # display.Context.SetTransparency(ais_shell, 0.7)
    display.DisplayShape(dup_face1, color='green')
    display.DisplayShape(dup_face2, color='orange')
    # display.DisplayShape(mold3.Shape(), color='green', update=True)
    # display.DisplayShape(mold4.Shape(), color='yellow', update=True)

    start_display()

if __name__ == '__main__':
    # Parse argument
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", type=str,
        help="Write Solid created form B-Spline surfaces to BREP file format", default=None)
    args = parser.parse_args()
    # Display and optionaly output surface to file (IGES file format)
    solid_compound(args.filename)