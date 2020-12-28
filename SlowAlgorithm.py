class Line:
    def __init__(self, a, b):
        self.a = a
        self.b = b


class Convex:
    def __init__(self, highest=None, lowest=None, left=None, right=None):
        if right is None:
            right = []
        if left is None:
            left = []
        self.highest = highest
        self.lowest = lowest
        self.left = right
        self.right = left


class HalfPlane:
    def __init__(self, a, b, is_left_boundary):
        self.line = Line(a, b)
        self.is_left_boundary = is_left_boundary


def make_a_convex(halfplane):
    if halfplane.is_left_boundary:
        return Convex(None, None, [halfplane.line], [])


def intersect_halfplanes(H):
    if len(H) == 1:
        return make_a_convex(H[0])

    C1 = intersect_halfplanes(H[:(len(H) + 1) // 2])
    C2 = intersect_halfplanes(H[len(H) // 2])

    return intersect_convex_regions(C1, C2)


def intersection_of_lines(l1, l2):
    if l1.a == l2.b:
        return None, None
    return (l2.b - l1.b) / (l1.a - l2.a), l1.a * (l2.b - l1.b) / (l1.a - l2.a) + l1.b


def intersecting_line_segment_in_chain(chain, y):
    line_segment = None
    for i in range(0, len(chain) - 1):
        if intersection_of_lines(chain[i], chain[i + 1])[1] < y:
            line_segment = chain[i]
            break
    if line_segment is None and len(chain) > 0:
        line_segment = chain[len(chain) - 1]
    return line_segment


def intersecting_line_segments(C, y):
    if C.highest is not None and C.highest < y:
        return None, None
    if C.lowest is not None and C.lowest > y:
        return None, None
    return intersecting_line_segment_in_chain(C.left, y), intersecting_line_segment_in_chain(C.right, y)


def intersect_convex_regions(C1, C2):
    left_edge_C1, right_edge_C1 = None, None
    left_edge_C2, right_edge_C2 = None, None

    y1 = C1.highest
    y2 = C2.highest

    y_start = None
    if y1 is None:
        y_start = y2
    elif y2 is None:
        y_start = y1
    else:
        y_start = min(y1, y2)

    left_edge_C1, right_edge_C1 = intersecting_line_segments(C1, y_start)
    left_edge_C2, right_edge_C2 = intersecting_line_segments(C2, y_start)
