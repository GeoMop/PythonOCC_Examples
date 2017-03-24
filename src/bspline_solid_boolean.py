"""
This module is able to create complicated compound object (cube) created from
several solid objects. Each side of solid is b-spline surface. Final compound
object can be exported to BREP file. Purpose of this module is to create
object that can be meshed in GMSH/Netgen and create compatible mesh network.
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
from OCC.TopoDS import topods_Wire, topods_Edge, topods_Vertex
from OCC.GeomAPI import GeomAPI_ProjectPointOnCurve
from OCC.BRepTools import BRepTools_WireExplorer
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

    # Definition of box used for splitting base box
    dx = 0.4
    dy = 0.01
    dz = 0.01
    points_2 = [
        gp_Pnt(0.0+dx, 0.5-dy, 0.5-dz),
        gp_Pnt(1.0+dx, 0.5-dy, 0.5-dz),
        gp_Pnt(1.0+dx, 1.5+dy, 0.5-dz),
        gp_Pnt(0.0+dx, 1.5+dy, 0.5-dz),
        gp_Pnt(0.0+dx, 0.5-dy, 1.5+dz),
        gp_Pnt(1.0+dx, 0.5-dy, 1.5+dz),
        gp_Pnt(1.0+dx, 1.5+dy, 1.5+dz),
        gp_Pnt(0.0+dx, 1.5+dy, 1.5+dz)
    ]
    solid_box2 = make_box(builder, points_2)

    # Definition of box used for splitting one part of slitted box
    dx = 0.01
    dy = 0.7
    dz = 0.01
    points_3 = [
        gp_Pnt(0.0-dx, 0.0+dy, 0.0-dz),
        gp_Pnt(1.0+dx, 0.0+dy, 0.0-dz),
        gp_Pnt(1.0+dx, 1.0+dy, 0.0-dz),
        gp_Pnt(0.0-dx, 1.0+dy, 0.0-dz),
        gp_Pnt(0.0-dx, 0.0+dy, 1.0+dz),
        gp_Pnt(1.0+dx, 0.0+dy, 1.0+dz),
        gp_Pnt(1.0+dx, 1.0+dy, 1.0+dz),
        gp_Pnt(0.0-dx, 1.0+dy, 1.0+dz)
    ]
    solid_box3 = make_box(builder, points_3)

    return solid_box1, solid_box2, solid_box3


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


def entities_of_wires(wire_shapes):
    """
    Return two dictionaries of wires and edges, keys of these two dictionaries
    are coordinates of verticies
    """
    wires = {}
    edges = {}
    verts = {}
    for wire_shape in wire_shapes:
        edge_shapes = edges_of_wire(wire_shape)
        edges_points = []
        for edge_shape in edge_shapes:
            edge_verts = verts_of_edge(edge_shape)
            for vert in edge_verts:
                vert_coords = coords_from_vert(vert)
                if vert_coords not in verts:
                    verts[vert_coords] = vert
            points = tuple(coords_from_vert(vert) for vert in edge_verts)
            points = tuple(sorted(points))
            edges[points] = edge_shape
            edges_points.append(points)
        wires[tuple(sorted(edges_points))] = wire_shape
    return wires, edges, verts


def bordering_wires_of_face(shape, face_shape):
    """
    Return dictionary of bordering wires with face shape. This function also
    returns list of common edges of bordering wires. Definition of
    bordering wire is following: such wire shares at least one edge
    with face_shape, but it does not create face_shape.
    """

    primitives = brep_explorer.shape_disassembly(shape)

    # Create list of wires "to be fixed" (potentially)
    wire_shapes_tbf = []
    for old_wire_shape in primitives[5].values():
        wire_shapes_tbf.append(topods_Wire(old_wire_shape))
    old_wires, old_edges, old_verts = entities_of_wires(wire_shapes_tbf)

    # Get list of wires at border of shape
    new_wire_shapes = wires_of_face(face_shape)
    new_wires, new_edges, new_verts = entities_of_wires(new_wire_shapes)

    # Dictionary of bordering wires
    bordering_wires = {}

    # Go through all wires of face_shape (usually only one wire)
    for new_wire_key, new_wire_shape in new_wires.items():
        print('>>>> Wire of face_shape:', new_wire_shape)
        # Go through all edges of bordering wire
        for edge_coords in new_wire_key:
            new_edge_coords = tuple(sorted(edge_coords))
            new_edge = new_edges[new_edge_coords]
            print('@@@@ Bordering edge:', new_edge_coords, new_edge)
            # Try to find this edge in other wires
            for old_wire_key, old_wire in old_wires.items():
                # Old wire can't be same as wire from bordering face
                # This wire is all right and there is no need to fix it
                if new_wire_key == old_wire_key:
                    continue
                # Try to find the edge in all edges of old wire
                for old_edge_coord in old_wire_key:
                    # Is it the edge with same verticies?
                    if tuple(sorted(old_edge_coord)) == new_edge_coords:
                        # Old wire containing edge from face_shape was found
                        print('#### Old Wire to be fixed:', old_wire_key, old_wire)
                        bordering_wires[old_wire_key] = old_wire
                        break

    print('<<<< Bordering wires:', bordering_wires)

    # Try to get list of common edges of bordering wires
    all_edges = []
    common_edges = {}
    for old_wire_key, old_wire in old_wires.items():
        if old_wire_key in bordering_wires.keys():
            print('^^^^ Edges of wrong wire:', old_wire_key)
            if len(all_edges) > 0:
                for edge in old_wire_key:
                    if edge in all_edges:
                        common_edges[edge] = old_edges[edge]
            all_edges.extend(old_wire_key)
            all_edges = list(set(all_edges))

    print('<<<< Common edges:', common_edges)

    return bordering_wires, common_edges


# Note: it is magic that following function works. It probably can't be done
# in one single replace, but you have to do several particular replaces. Big
# disadvantage of reshape.Apply() is following: it returns new shape instead
# of modification old shape.
def remove_duple_wires_edges_verts(reshape, new_wire_shapes, old_wire_shapes):
    """
    Try to remove duple wires, edges and verticies
    """
    new_wires, new_edges, new_verts = entities_of_wires(new_wire_shapes)
    old_wires, old_edges, old_verts = entities_of_wires(old_wire_shapes)

    for new_vert_key, new_vert_shape in new_verts.items():
        old_vert_shape = old_verts[new_vert_key]

        # Switch orientation of new vertex to match old vertex
        if old_vert_shape.Orientation() != new_vert_shape.Orientation():
            reshape.Replace(old_vert_shape, new_vert_shape.Reversed())
        else:
            reshape.Replace(old_vert_shape, new_vert_shape)
        # FIXME: Note: previous code probably will not work in all cases. What
        # you need to do is to go through all wires using this vertex and replace
        # this vertex in all edges using this vertex. Replaced vertex has to
        # have same orientation as old one.

    for new_edge_key, new_edge_shape in new_edges.items():
        old_edge_shape = old_edges[new_edge_key]

        # Always switch orientation of edge
        reshape.Replace(old_edge_shape, new_edge_shape.Reversed())
        # FIXME: previous code probably will not work in all cases too. You will
        # have to go through all wires using this edge and replace this edge
        # with new one. Replaced edge has to have same orientation as old one too.

    for new_wire_key, new_wire_shape in new_wires.items():
        old_wire_shape = old_wires[new_wire_key]

        # Never switch orientation of wire. It is right. There is probably
        # no need to switch direction of new wire.
        reshape.Replace(old_wire_shape, old_wire_shape)


def remove_duple_faces(reshape, faces, face_points, old_face_shape):
    """
    Try to remove duplicity of old_face_shape
    """
    for face in faces.keys():
        if compare_faces(face, face_points) is True:
            new_face_shape = faces[face_points]

            new_wires = wires_of_face(new_face_shape)
            old_wires = wires_of_face(old_face_shape)

            remove_duple_wires_edges_verts(reshape, new_wires, old_wires)

            # Always switch orientation of face
            reshape.Replace(old_face_shape, new_face_shape.Reversed())

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


def remove_duple_face_shapes(base_shape, shapes):
    """
    Try to remove duplicated faces in two shapes
    """
    base_primitives = brep_explorer.shape_disassembly(base_shape)

    faces = {}
    dupli_faces = []

    brt = BRep_Tool()
    reshape = BRepTools_ReShape()

    # This for loop is only for filling dictionary of faces
    # with faces from first shape
    for face_shape in base_primitives[4].values():
        points = points_of_face(face_shape)
        if remove_duple_faces(reshape, faces, points, face_shape) is False:
            faces[points] = face_shape
        else:
            # This line of code should not be never called for properly
            # created shapes.
            dupli_faces.append(face_shape)

    for shape in shapes:
        primitives = brep_explorer.shape_disassembly(shape)
        # This for loop remove duplicities in remaining shapes
        for face_shape in primitives[4].values():
            points = points_of_face(face_shape)
            if remove_duple_faces(reshape, faces, points, face_shape) is False:
                faces[points] = face_shape
            else:
                # Debug code ... it can help you to implement glue two solids
                # together in right way.
                # bordering_wires_of_face(shape, face_shape)
                dupli_faces.append(face_shape)

    # Reshaping all shapes
    new_shapes = [base_shape,]
    for new_shape in shapes:
        _new_shape = reshape.Apply(new_shape)
        new_shapes.append(_new_shape)

    return new_shapes, dupli_faces


def find_intersected_bordering_faces(face, volume1, volume2, hint_face, tolerance=0.00001):
    """
    Try to find bordering faces
    """

    # Get bordering points from face
    primitives0 = brep_explorer.shape_disassembly(face)
    brt = BRep_Tool()
    border_points = []
    for vert_shape in primitives0[7].values():
        vert = topods_Vertex(vert_shape)
        pnt = brt.Pnt(topods_Vertex(vert))
        border_points.append(pnt)

    primitives1 = brep_explorer.shape_disassembly(face)
    brt = BRep_Tool()
    curves = []
    for edge_shape in primitives1[6].values():
        edge = topods_Edge(edge_shape)
        curve_handle = brt.Curve(edge)[0]
        curve = curve_handle.GetObject()
        curves.append(curve)

    # Get candidate points from hint_face
    primitives2 = brep_explorer.shape_disassembly(hint_face)
    brt = BRep_Tool()
    cand_points = []
    for vert_shape in primitives2[7].values():
        vert = topods_Vertex(vert_shape)
        pnt = brt.Pnt(topods_Vertex(vert))
        cand_points.append(pnt)

    # Iterate over all curves and try to find intersection points
    inter_points = []
    for curve in curves:
        distances = {}
        # Compute distances between candidate points and curve
        for point in cand_points:
            proj = GeomAPI_ProjectPointOnCurve(point, curve.GetHandle())
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
            face_coords.append((pnt.X(), pnt.Y(), pnt.Z()))
        
        # TODO: use better check in coordinates matches then: `coo in border_coords`
        # e.g.: use some distance and tolerance
        res = [coo in border_coords for coo in face_coords]
        if all(res) is True:
            border_faces.append(face_shape)

    # TODO: Check if these faces covers original face completely

    return border_faces


def display_points(display, points_coords):
    """
    Display points as yellow crosses
    """
    presentation = OCC.Prs3d.Prs3d_Presentation(display._struc_mgr)
    group = OCC.Prs3d.Prs3d_Root_CurrentGroup(presentation.GetHandle()).GetObject()
    black = OCC.Quantity.Quantity_Color(OCC.Quantity.Quantity_NOC_BLACK)
    asp = OCC.Graphic3d.Graphic3d_AspectLine3d(black, OCC.Aspect.Aspect_TOL_SOLID, 1)
    pnt_array = OCC.Graphic3d.Graphic3d_ArrayOfPoints(len(points_coords),
                                                      False,  # hasVColors
                                                      )
    for point in points_coords:
        pnt = OCC.gp.gp_Pnt(point[0], point[1], point[2])
        pnt_array.AddVertex(pnt)
    group.SetPrimitivesAspect(asp.GetHandle())
    group.AddPrimitiveArray(pnt_array.GetHandle())
    presentation.Display()


def replace_face_with_splitted_faces(builder, shape, old_face, splitted_faces):
    """
    Try to create new shape that does not include old_face, but it
    includes instead splitted_faces
    """
    old_points = points_of_face(old_face)

    sewing = BRepBuilderAPI_Sewing(0.01, True, True, True, False)
    sewing.SetFloatingEdgesMode(True)

    # Get list of all faces in shape
    primitives = brep_explorer.shape_disassembly(shape)    

    brt = BRep_Tool()
    border_faces = []

    # This loop tries to add original not-splitted faces to sewing
    for face_shape in primitives[4].values():
        new_points = points_of_face(face_shape)
        # Quick Python trick using sets: all points in new_points
        # has to be included in old_points.
        # Note: may be, it is not 100% reliable, but for all uses cases it just works.
        old_set = set(old_points)
        new_set = set(new_points)
        if not old_set <= new_set:
            old_face = topods_Face(face_shape)
            sewing.Add(old_face)
    # This loop adds splitted faces to sewing
    for face_shape in splitted_faces:
        old_face = topods_Face(face_shape)
        sewing.Add(old_face)

    # Sew all faces together
    sewing.Perform()
    sewing_shape = sewing.SewedShape()

    # When there is no hole in sewing, then following function call will not call
    # Do not use try-except to solve problems here!
    shell = topods_Shell(sewing_shape)

    # Make solid from shell and return result
    make_solid = BRepBuilderAPI_MakeSolid()
    make_solid.Add(shell)
    solid = make_solid.Solid()
    builder.MakeSolid(solid)
    builder.Add(solid, shell)
    return solid


def create_replace_dictionary(old_dup_faces, old_shapes, new_shapes, new_hint_faces):
    """
    This function tries to create dictionary of face replacements.
    """
    replacements = {}
    for old_dup_face in old_dup_faces:
        border_faces = []
        for new_hint_face in new_hint_faces:
            # Try to find bordering faces
            tmp_faces = find_intersected_bordering_faces(old_dup_face, old_shapes, new_shapes, new_hint_face)
            # When some faces were found, then add them to list.
            # Note: this is usually happened only once in this loop, but this tries to be robust
            if len(tmp_faces) > 0:
                border_faces.extend(tmp_faces)
        # This should not happen
        if len(border_faces) == 1:
            raise ValueError('When some intersections are found, then at least two have to be found. Not only one!')
        # When at least two border faces were found, then add them to the dictionary
        elif len(border_faces) >= 2:
            replacements[old_dup_face] = border_faces
    return replacements


def solid_compound(filename=None):
    """
    Generate and display several solid object created from b-spline surface and
    sharing some b-spline surfaces.
    """

    display, start_display, add_menu, add_function_to_menu = init_display()
    display.EraseAll()

    # Create Builder first
    builder = BRep_Builder()

    solid_box1, solid_box2, solid_box3 = create_test_boxes(builder)

    # Split solid_box into two molds
    mold1 = BRepAlgoAPI_Cut(solid_box1, solid_box2)
    mold2 = BRepAlgoAPI_Common(solid_box1, solid_box2)

    # Try to remove face from second mold and share common one face.
    # It is like glue two shapes together
    new_molds, dup_faces = remove_duple_face_shapes(mold1.Shape(), (mold2.Shape(),))
    dup_face1 = dup_faces[0]

    # Split second mold into yet other two molds
    mold3 = BRepAlgoAPI_Cut(new_molds[1], solid_box3)
    mold4 = BRepAlgoAPI_Common(new_molds[1], solid_box3)

    # Again remove common face
    _new_molds, _dup_faces = remove_duple_face_shapes(mold3.Shape(), (mold4.Shape(),))
    dup_face2 = _dup_faces[0]

    # Create dictionary with replacements. Keys are original faces and corresponding values are
    # splitted faces ... it is used in next step
    replacements = create_replace_dictionary(dup_faces, _new_molds[0], _new_molds[1], _dup_faces)

    # Apply replacement for all item of dictionary
    for dup_face, inter_faces in replacements.items():
        # Replace original face with bordering faces
        new_mold = replace_face_with_splitted_faces(builder, new_molds[0], dup_face, inter_faces)
        new_molds[0] = new_mold

    # Remove duplicities in faces
    __new_molds, dup_faces = remove_duple_face_shapes(new_molds[0], _new_molds)

    colors = ['red', 'green', 'blue', 'yellow', 'orange']

    # Create final compound
    compound = TopoDS_Compound()
    builder.MakeCompound(compound)
    for color_id, mold in enumerate(__new_molds):
        builder.Add(compound, mold)

        
    # Print statistics about final compound
    print('Final compound')
    stat = brep_explorer.create_shape_stat(compound)
    brep_explorer.print_stat(stat)

    # Write compound to the BREP file
    if filename is not None:
         breptools_Write(compound, filename)

    # Display results
    col_len = len(colors)
    for color_id, mold in enumerate(__new_molds):
        builder.Add(compound, mold)
        _color_id = color_id % col_len
        ais_shell = display.DisplayShape(mold, color=colors[_color_id], update=True)
        # display.Context.SetTransparency(ais_shell, 0.7)
    start_display()


if __name__ == '__main__':
    # Parse argument
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", type=str,
        help="Write Solid created form B-Spline surfaces to BREP file format", default=None)
    args = parser.parse_args()
    solid_compound(args.filename)