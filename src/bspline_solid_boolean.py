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
from OCC.TopoDS import topods_Edge, topods_Vertex
from OCC.GeomAPI import GeomAPI_ProjectPointOnCurve
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
        bspline_surface = Geom_BSplineSurface( poles, uknots, vknots, umult, vmult, udeg, vdeg, False, False )
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


def compare_faces(face1, face2):
    """
    Compare two faces
    """

    for vert in face1:
        if vert not in face2:
            return False

    return True


def wires_of_face(face_shape):
    """
    Return tuple of face wires
    """
    face_traverse = traverse.Topo(face_shape)
    return tuple(face_traverse.wires_from_face(face_shape))


def edges_of_wire(wire_shape):
    """
    Return tuple of wire edges
    """
    wire_traverse = traverse.Topo(wire_shape)
    return tuple(wire_traverse.edges_from_wire(wire_shape))


def verts_of_edge(edge_shape):
    """
    Return tuple of edge verticies
    """
    edge_traverse = traverse.Topo(edge_shape)
    return tuple(edge_traverse.vertices_from_edge(edge_shape))


def coords_from_vert(vert_shape):
    """
    Return tuple representing coordinates of one vertex
    """
    brt = BRep_Tool()
    pnt = brt.Pnt(topods_Vertex(vert_shape))
    return (pnt.X(), pnt.Y(), pnt.Z())


def points_of_wire(wire_shapes):
    """
    Return two dictionaries of wires and edges, keys of these two dictionaries
    are coordinates of verticies
    """
    wires = {}
    edges = {}
    for wire_shape in wire_shapes:
        print(wire_shape)
        edge_shapes = edges_of_wire(wire_shape)
        edges_points = []
        for edge_shape in edge_shapes:
            verts = verts_of_edge(edge_shape)
            points = tuple(sorted(coords_from_vert(vert) for vert in verts))
            edges[points] = edge_shape
            edges_points.append(points)
        wires[tuple(edges_points)] = wire_shape
    return wires, edges


def remove_duple_wires_and_edges(reshape, new_wire_shapes, old_wire_shapes):
    """
    """
    new_wires, new_edges = points_of_wire(new_wire_shapes)
    old_wires, old_edges = points_of_wire(old_wire_shapes)

    for new_wire_key, new_wire_shape in new_wires.items():
        old_wire_shape = old_wires[new_wire_key]
        reshape.Replace(old_wire_shape, new_wire_shape)

    for new_edge_key, new_edge_shape in new_edges.items():
        old_edge_shape = old_edges[new_edge_key]
        reshape.Replace(old_edge_shape, new_edge_shape)


def remove_duple_faces(reshape, faces, face_points, face_shape):
    """
    Try to remove duplicity faces from two boolean operations
    """
    for face in faces.keys():
        if compare_faces(face, face_points) is True:
            new_face_shape = faces[face_points]
            print('Duplicity of: ', new_face_shape)
            print('Removing this face ...')
            reshape.Replace(face_shape, new_face_shape.Reversed())

            new_wires = wires_of_face(new_face_shape)
            old_wires = wires_of_face(face_shape)

            remove_duple_wires_and_edges(reshape, new_wires, old_wires)
            
            return True
    return False


def points_of_face(face_shape):
    """
    Return sorted tuple of face points
    """
    face_traverse = traverse.Topo(face_shape)
    vertices = face_traverse.vertices_from_face(face_shape)
    points = []
    brt = BRep_Tool()
    for vert in vertices:
        pnt = brt.Pnt(topods_Vertex(vert))
        points.append((pnt.X(), pnt.Y(), pnt.Z()))
    return tuple(sorted(points))


def compare_edges(edge1, edge2):
    """
    Compare two faces. Return 1, when edges are same. Return -1, when
    edges are same, but reversed. Othwerwise return 0.
    """
    if edge1[0] == edge2[0] and edge1[1] == edge2[1]:
        return 1
    elif edge1[0] == edge2[1] and edge1[1] == edge2[0]:
        return -1
    else:
        return 0


def remove_duple_edges(reshape, edges, new_edge, edge_shape):
    """
    Try to remove duplicity edges from two boolean operations
    """
    for edge in edges.keys():
        ret = compare_edges(edge, new_edge)
        if ret != 0:
            original_edge = edges[tuple(sorted(new_edge))]
            print('Duplicity of: ', original_edge)
            if ret == 1:
                print('Removing this edge ...')
                reshape.Replace(edge_shape, original_edge)
            elif ret == -1:
                print('Removing this edge reversed ...')
                reshape.Replace(edge_shape, original_edge.Reversed())
            return True
    return False


def points_of_edge(edge_shape):
    """
    Return sorted tuple of edge points
    """
    edge_traverse = traverse.Topo(edge_shape)
    vertices = edge_traverse.vertices_from_edge(edge_shape)
    points = []
    brt = BRep_Tool()
    for vert in vertices:
        pnt = brt.Pnt(topods_Vertex(vert))
        points.append((pnt.X(), pnt.Y(), pnt.Z()))
    return tuple(points)


def remove_duple_face_shapes(*shapes):
    """
    Try to remove duplicated faces in two shapes
    """
    primitives = brep_explorer.shapes_disassembly(shapes)
    # print(primitives)
    faces = {}
    edges = {}
    dupli_edges = []
    dupli_wires = []
    dupli_faces = []

    brt = BRep_Tool()
    reshape = BRepTools_ReShape()

    # print("Dupli edges:", dupli_edges)

    # Faces
    for face_shape in primitives[4].values():
        # Debug print
        print(face_shape)
        points = points_of_face(face_shape)
        if remove_duple_faces(reshape, faces, points, face_shape) is False:
            faces[points] = face_shape
        else:
            dupli_faces.append(face_shape)

    print("Dupli faces:", dupli_faces)

    # Wires
    # for wire_shape in primitives[5].values():
    #     print(wire_shape)
    #     edges = edges_of_wire(wire_shape)

    # Edges
    # for edge_shape in primitives[6].values():
    #     print(edge_shape)
    #     points = points_of_edge(edge_shape)
    #     if remove_duple_edges(reshape, edges, points, edge_shape) is False:
    #         edges[tuple(sorted(points))] = edge_shape
    #     else:
    #         dupli_edges.append(edge_shape)

    # # Vertices
    # dupli_verts = []
    # for vert_shape in primitives[7].values():
    #     print(vert_shape)
    #     point = brt.Pnt(topods_Vertex(vert_shape))
    #     if point in dupli_verts:
    #         points[point] = vert_shape
    #     else:
    #         dupli_edges.append(vert_shape)

    # print("Dupli edges:", dupli_verts)

    # Reshaping all shapes
    new_shapes = []
    for shape in shapes:
        new_shape = reshape.Apply(shape)
        new_shapes.append(new_shape)

    return new_shapes, dupli_faces, dupli_edges


def find_intersected_bordering_faces(face, volume1, volume2, hint_face, tolerance=0.00001):
    """
    Try to find bordering faces
    """

    # Get bordering points from face
    primitives0 = brep_explorer.shape_disassembly(face)
    print('>>> Verts:')
    brt = BRep_Tool()
    border_points = []
    for vert_shape in primitives0[7].values():
        vert = topods_Vertex(vert_shape)
        pnt = brt.Pnt(topods_Vertex(vert))
        border_points.append(pnt)

    primitives1 = brep_explorer.shape_disassembly(face)
    # print('>>>> Disassembly face:')
    # stat = brep_explorer.create_shape_stat(face)
    # brep_explorer.print_stat(stat)

    brt = BRep_Tool()
    curves = []
    for edge_shape in primitives1[6].values():
        edge = topods_Edge(edge_shape)
        curve_handle = brt.Curve(edge)[0]
        curve = curve_handle.GetObject()
        curves.append(curve)
        # edge_traverse = traverse.Topo(edge_shape)
        # vertices = edge_traverse.vertices_from_edge(edge_shape)
        # for idx,vert in enumerate(vertices):
        #     pnt = brt.Pnt(topods_Vertex(vert))
        #     print(idx, pnt.X(), pnt.Y(), pnt.Z())

    # Get candidate points from hint_face
    primitives2 = brep_explorer.shape_disassembly(hint_face)
    brt = BRep_Tool()
    cand_points = []
    for vert_shape in primitives2[7].values():
        vert = topods_Vertex(vert_shape)
        pnt = brt.Pnt(topods_Vertex(vert))
        # print('Vertex:', pnt.X(), pnt.Y(), pnt.Z())
        cand_points.append(pnt)

    # Iterate over all curves and try to find intersection points
    inter_points = []
    for curve in curves:
        distances = {}
        # Compute distances between candidate points and curve
        for point in cand_points:
            proj = GeomAPI_ProjectPointOnCurve(point, curve.GetHandle())
            # print(point.X(), point.Y(), point.Z(), proj.LowerDistance())
            distances[proj.LowerDistance()] = point
        # Get candidate with lowest distance
        min_dist = min(distances.keys())
        # When distance is lower then tolerance, then we found point at intersection
        if min_dist <= tolerance:
            inter_points.append(distances[min_dist])

    if len(inter_points) == 0:
        return []

    # When some intersection points was found, then extend list of border points
    # with these intersection points
    border_points.extend(inter_points)

    border_coords = [(pnt.X(), pnt.Y(), pnt.Z()) for pnt in border_points]

    # Get list of all faces in volumes
    primitives3 = brep_explorer.shapes_disassembly((volume1, volume2))
    brt = BRep_Tool()
    border_faces = []
    for face_shape in primitives3[4].values():
        face_traverse = traverse.Topo(face_shape)
        vertices = face_traverse.vertices_from_face(face_shape)
        face_coords = []
        for idx,vert in enumerate(vertices):
            pnt = brt.Pnt(topods_Vertex(vert))
            # print(idx, pnt.X(), pnt.Y(), pnt.Z())
            face_coords.append((pnt.X(), pnt.Y(), pnt.Z()))
        
        # TODO: use better check in coordinates matches then: `coo in border_coords`
        # e.g.: use some distance and tolerance
        res = [coo in border_coords for coo in face_coords]
        if all(res) is True:
            border_faces.append(face_shape)

    print('>>>>>> Border faces: ', border_faces)
    # TODO: Check if these faces covers original face completely

    return border_faces


def replace_face_with_splitted_faces(builder, shape, face, splitted_faces):
    """
    Try to create new shape that does not include face, but it
    includes instead splitted_faces
    """
    points = points_of_face(face)

    sewing = BRepBuilderAPI_Sewing(0.01, True, True, True, False)
    sewing.SetFloatingEdgesMode(True)
    # Get list of all faces in shape
    primitives = brep_explorer.shape_disassembly(shape)    
    brt = BRep_Tool()
    border_faces = []
    for face_shape in primitives[4].values():
        if points_of_face(face_shape) != points:
            face = topods_Face(face_shape)
            sewing.Add(face)
        else:
            print('>>>> NOT INCLUDING FACE:', face_shape)
    for face_shape in splitted_faces:
        face = topods_Face(face_shape)
        sewing.Add(face)
    sewing.Perform()
    sewing_shape = sewing.SewedShape()
    try:
        shell = topods_Shell(sewing_shape)
    except RuntimeError:
        return None
    else:
        print('Huraaaa!!!!')
    make_solid = BRepBuilderAPI_MakeSolid()
    make_solid.Add(shell)

    solid = make_solid.Solid()

    builder.MakeSolid(solid)
    builder.Add(solid, shell)

    return solid


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

    new_molds, dup_faces, dup_edges = remove_duple_face_shapes(mold1.Shape(), mold2.Shape())
    dup_face1 = dup_faces[0]

    # shape_type = new_mold1.ShapeType()
    # print(shape_type, brep_explorer.SHAPE_NAMES[shape_type])

    print('Reshaped Mol1')
    stat1 = brep_explorer.create_shape_stat(new_molds[0])
    brep_explorer.print_stat(stat1)

    print('Reshaped Mol2')
    stat2 = brep_explorer.create_shape_stat(new_molds[1])
    brep_explorer.print_stat(stat2)

    # Important note: it is necessary to do "cutting" on shape without removed
    # doubles. In this case you have to use mold2, NOT new_mold. Otherwise it
    # will create strange results
    mold3 = BRepAlgoAPI_Cut(molds[1].Shape(), solid_box4)
    mold4 = BRepAlgoAPI_Cut(molds[1].Shape(), solid_box5)

    _new_molds, _dup_faces, _dup_edges = remove_duple_face_shapes(mold3.Shape(), mold4.Shape())
    dup_face2 = _dup_faces[0]

    new_molds.extend(_new_molds)

    print('Reshaped Mol3')
    stat3 = brep_explorer.create_shape_stat(new_molds[2])
    brep_explorer.print_stat(stat3)

    print('Reshaped Mol4')
    stat4 = brep_explorer.create_shape_stat(new_molds[3])
    brep_explorer.print_stat(stat4)

    # Try to find two intersection points
    inter_faces = find_intersected_bordering_faces(dup_face1, new_molds[2], new_molds[3], dup_face2)

    new_mold = replace_face_with_splitted_faces(builder, new_molds[0], dup_face1, inter_faces)
    new_molds[0] = new_mold

    # Remove duplicities in faces
    new_molds, dup_faces, dup_edges = remove_duple_face_shapes(new_molds[0], new_molds[2], new_molds[3])

    compound = TopoDS_Compound()
    builder.MakeCompound(compound)
    for modl in new_molds:
        builder.Add(compound, mold)

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
    ais_shell = display.DisplayShape(mold4.Shape(), color='yellow', update=True)
    # display.Context.SetTransparency(ais_shell, 0.7)
    # display.DisplayShape(dup_face1, color='green')
    # display.DisplayShape(dup_face2, color='orange')
    # for face in inter_faces:
    #     display.DisplayShape(face, color='green')
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