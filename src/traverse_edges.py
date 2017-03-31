"""
Example of shape traversals
"""

from __future__ import print_function

from OCC.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.TopExp import TopExp_Explorer

from OCC.TopoDS import topods_Face, topods_Edge

from OCC.TopAbs import TopAbs_FACE
from OCC.TopAbs import TopAbs_EDGE


def get_faces(_shape):
    """ return the faces from `_shape`

    :param _shape: TopoDS_Shape, or a subclass like TopoDS_Solid
    :return: a list of faces found in `_shape`
    """
    topExp = TopExp_Explorer()
    topExp.Init(_shape, TopAbs_FACE)
    _faces = []

    while topExp.More():
        fc = topods_Face(topExp.Current())
        _faces.append(fc)
        topExp.Next()

    return _faces

def get_edges(_shape):
    """ return the edges from `_shape`

    :param _shape: TopoDS_Shape, or a subclass like TopoDS_Solid
    :return: a list of edges found in `_shape`
    """
    topExp = TopExp_Explorer()
    topExp.Init(_shape, TopAbs_EDGE)
    _edges = []

    while topExp.More():
        edge = topods_Edge(topExp.Current())
        _edges.append(edge)
        topExp.Next()

    return _edges


def main():
    """ main function for testing purpose """
    box = BRepPrimAPI_MakeBox(500., 400., 300.).Shape()
    faces = get_faces(box)
    print(faces)
    edges = get_edges(box)
    print(edges)


if __name__ == '__main__':
    main()
