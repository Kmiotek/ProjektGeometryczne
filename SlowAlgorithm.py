class Line:
    def __init__(self, a, b):
        self.a = a
        self.b = b


print("hello world")

print([1, 4, 5][:1])


class Convex:
    def __init__(self, left=None, right=None):
        if right is None:
            right = []
        if left is None:
            left = []
        self.left = right
        self.right = left

    def highest(self):
        if len(self.left) < 1 or len(self.right) < 1:
            return None
        return intersection_of_lines(self.left[0], self.right[0])

    def lowest(self):
        if len(self.left) < 1 or len(self.right) < 1:
            return None
        return intersection_of_lines(self.left[-1], self.right[-1])


class HalfPlane:
    def __init__(self, a, b, is_left_boundary):
        self.line = Line(a, b)
        self.is_left_boundary = is_left_boundary


def make_a_convex(halfplane):
    if halfplane.is_left_boundary:
        return Convex([halfplane.line], [])
    else:
        return Convex([], [halfplane.line])


def intersect_halfplanes(H):
    if len(H) == 1:
        return make_a_convex(H[0])

    C1 = intersect_halfplanes(H[:(len(H) + 1) // 2])
    C2 = intersect_halfplanes(H[len(H) // 2:])

    return intersect_convex_regions(C1, C2)


def intersection_of_lines(l1, l2):
    if l1 is None or l2 is None:
        return None
    if l1.a == l2.a:
        return None
    return (l2.b - l1.b) / (l1.a - l2.a), l1.a * (l2.b - l1.b) / (l1.a - l2.a) + l1.b


def intersecting_line_segment_in_chain(chain, y):
    line_segment_index = None
    for i in range(0, len(chain) - 1):
        if intersection_of_lines(chain[i], chain[i + 1])[1] < y:
            line_segment_index = i
            break
    if line_segment_index is None and len(chain) > 0:
        line_segment_index = len(chain) - 1
    return line_segment_index


def intersecting_line_segments(C, y):
    if C.highest() is not None and C.highest() < y:
        return None, None
    if C.lowest() is not None and C.lowest() > y:
        return None, None
    return intersecting_line_segment_in_chain(C.left, y), intersecting_line_segment_in_chain(C.right, y)


def x_from_y(line, y):
    return (y - line.b) / line.a


def is_between(point, l1, l2):
    if l1 is None:
        if l2 is None:
            return True
        if x_from_y(l2, point[1]) > point[0]:
            return True
        return False
    if l2 is None:
        if x_from_y(l1, point[1]) < point[0]:
            return True
        return False
    if x_from_y(l1, point[1]) < point[0] < x_from_y(l2, point[1]):
        return True
    return False


def is_to_left(point, line):
    if point[0] < x_from_y(line, point[1]):
        return True
    return False


def lower_endpoint(C, chain_is_left, line_segment_index):
    if line_segment_index is None:
        return None
    if chain_is_left:
        if line_segment_index > len(C.left) - 1:
            return None
        elif line_segment_index == len(C.left) - 1:
            return C.lowest()
        return intersection_of_lines(C.left[line_segment_index], C.left[line_segment_index + 1])
    else:
        if line_segment_index > len(C.right) - 1:
            return None
        elif line_segment_index == len(C.right) - 1:
            return C.lowest()
        return intersection_of_lines(C.right[line_segment_index], C.right[line_segment_index + 1])


def intersect_convex_regions(C1, C2):
    C = Convex()

    y1 = C1.highest()
    y2 = C2.highest()

    if y1 is None:
        y_start = y2
    elif y2 is None:
        y_start = y1
    else:
        y_start = min(y1, y2)

    left_edge_C1_index, right_edge_C1_index = intersecting_line_segments(C1, y_start)
    left_edge_C2_index, right_edge_C2_index = intersecting_line_segments(C2, y_start)

    while True:
        lower_endpoint_left_C1 = lower_endpoint(C1, True, left_edge_C1_index)
        lower_endpoint_right_C1 = lower_endpoint(C1, False, right_edge_C1_index)
        lower_endpoint_left_C2 = lower_endpoint(C2, True, left_edge_C2_index)
        lower_endpoint_right_C2 = lower_endpoint(C2, False, right_edge_C2_index)

        if lower_endpoint_right_C2 is None and lower_endpoint_right_C1 is None and lower_endpoint_left_C2 is None and \
                lower_endpoint_left_C1 is None:
            break

        current = max(lower_endpoint_left_C1, lower_endpoint_left_C2, lower_endpoint_right_C1, lower_endpoint_right_C2,
                      key=lambda t: t[1])
        if current == lower_endpoint_left_C1:
            handle_event(C, C2, left_edge_C2_index, right_edge_C2_index, C1.left[left_edge_C1_index],
                         current, True)
            left_edge_C1_index += 1
            if left_edge_C1_index >= len(C1.left):
                break
        elif current == lower_endpoint_right_C1:
            handle_event(C, C2, left_edge_C2_index, right_edge_C2_index, C1.right[right_edge_C1_index],
                         current, True)
            right_edge_C1_index += 1
            if right_edge_C1_index >= len(C1.right):
                break
        elif current == lower_endpoint_left_C2:
            handle_event(C, C1, left_edge_C1_index, right_edge_C1_index, C2.left[left_edge_C2_index],
                         current, True)
            left_edge_C2_index += 1
            if left_edge_C2_index >= len(C2.left):
                break
        elif current == lower_endpoint_right_C2:
            handle_event(C, C1, left_edge_C1_index, right_edge_C1_index, C2.right[right_edge_C2_index],
                         current, True)
            right_edge_C2_index += 1
            if right_edge_C2_index >= len(C2.right):
                break
    return C


def append_to_correct_chain(C, current, is_left):
    if is_left:
        C.left.append(current)
    else:
        C.right.append(current)


def handle_event(C, C3, left_edge_C3_index, right_edge_C3_index, current, point, is_left):
    if left_edge_C3_index is None:
        left_edge_C3 = None
    else:
        left_edge_C3 = C3.left[left_edge_C3_index]
    if right_edge_C3_index is None:
        right_edge_C3 = None
    else:
        right_edge_C3 = C3.right[right_edge_C3_index]
    if is_between(point, left_edge_C3, right_edge_C3):
        append_to_correct_chain(C, current, is_left)
    intersection = intersection_of_lines(current, right_edge_C3)
    if intersection is not None:
        if not is_to_left(point, right_edge_C3):
            append_to_correct_chain(C, current, is_left)
            C.right.append(right_edge_C3)
    intersection = intersection_of_lines(current, left_edge_C3)
    if intersection is not None:
        if is_to_left(point, left_edge_C3):
            append_to_correct_chain(C, current, is_left)
        else:
            C.left.append(left_edge_C3)


c = intersect_halfplanes(
    [HalfPlane(2, 1, False), HalfPlane(2, -6, True)])

print(c.left)
print(c.right)
