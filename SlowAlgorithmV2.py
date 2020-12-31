class Convex:
    def __init__(self, left = None, right = None):
        if right is None:
            right = []
        if left is None:
            left = []
        self.left = right
        self.right = left

    def append(self, current, is_right):
        if is_right:
            self.right.append(current)
        else:
            self.left.append(current)

    def get(self, index, is_right):
        if is_right:
            return self.right[index]
        else:
            return self.left[index]

    def highest(self):
        if len(self.right) < 1:
            if len(self.left) < 1:
                print("cos poszlo bardzo zle")
                return None
            return self.left[-1].x_from_y(10 ** 10), 10 ** 10
        if len(self.left) < 1:
            return self.right[-1].x_from_y(10 ** 10), 10 ** 10

        intersection = intersection_of_lines(self.left[0], self.right[0])
        if intersection is not None:
            return intersection
        return 0, 10 ** 10

    def lowest(self):
        if len(self.right) < 1:
            if len(self.left) < 1:
                print("cos poszlo bardzo zle")
                return None
            return self.left[-1].x_from_y(-1 * 10 ** 10), -1 * 10 ** 10
        if len(self.left) < 1:
            return self.right[-1].x_from_y(-1 * 10 ** 10), -1 * 10 ** 10

        intersection = intersection_of_lines(self.left[0], self.right[0])
        if intersection is not None:
            return intersection
        return 0, -1 * 10 ** 10

    def intersecting_line_segments(self, y):
        if self.highest()[1] < y:
            return None, None
        if self.lowest()[1] > y:
            return None, None
        r1, r2 = self.intersecting_line_segment_in_chain(False, y), self.intersecting_line_segment_in_chain(True, y)
        if len(self.left) < 1:
            return None, r2
        if len(self.right) < 1:
            return r1, None
        return r1, r2

    def intersecting_line_segment_in_chain(self, chain_is_right, y):
        if chain_is_right:
            chain = self.right
        else:
            chain = self.left
        for i in range(0, len(chain) - 1):
            if intersection_of_lines(chain[i], chain[i + 1])[1] < y:
                return i
        return len(chain) - 1

    def lower_endpoint(self, chain_is_right, line_segment_index):
        if line_segment_index is None:
            return None
        if chain_is_right:
            chain = self.right
        else:
            chain = self.left
        if line_segment_index > len(chain) - 1:
            print("ojoj")
            return None
        elif line_segment_index == len(chain) - 1:
            return self.lowest()
        return intersection_of_lines(chain[line_segment_index], chain[line_segment_index + 1])


class Line:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def x_from_y(self, y):
        return (y - self.b) / self.a

    def is_to_left(self, point):
        if point[0] < self.x_from_y(point[1]):
            return True
        return False

    def is_to_right(self, point):
        if point[0] > self.x_from_y(point[1]):
            return True
        return False


class HalfPlane:
    def __init__(self, a, b, is_right_boundary):
        self.line = Line(a, b)
        self.is_right_boundary = is_right_boundary


def intersection_of_lines(l1, l2):
    if l1 is None or l2 is None:
        return None
    if l1.a == l2.a:
        return None
    return (l2.b - l1.b) / (l1.a - l2.a), l1.a * (l2.b - l1.b) / (l1.a - l2.a) + l1.b


def is_between(point, l1, l2):
    if l1 is None:
        if l2 is None:
            return True
        if l2.x_from_y(point[1]) > point[0]:
            return True
        return False
    if l2 is None:
        if l1.x_from_y(point[1]) < point[0]:
            return True
        return False
    if l1.x_from_y(point[1]) < point[0] < l2.x_from_y(point[1]):
        return True
    return False


def make_a_convex(halfplane):
    if halfplane.is_right_boundary:
        return Convex([], [halfplane.line])
    else:
        return Convex([halfplane.line], [])


# here algorithm

def intersect_halfplanes(H):
    if len(H) == 1:
        return make_a_convex(H[0])

    C1 = intersect_halfplanes(H[:(len(H) + 1) // 2])
    C2 = intersect_halfplanes(H[len(H) // 2:])

    return intersect_convex_regions(C1, C2)


def intersect_convex_regions(C1, C2):
    C = Convex()

    y1 = C1.highest()[1]
    y2 = C2.highest()[1]

    y_start = min(y1, y2)

    left_edge_C1_index, right_edge_C1_index = C1.intersecting_line_segments(y_start)
    left_edge_C2_index, right_edge_C2_index = C2.intersecting_line_segments(y_start)

    while True:
        lower_endpoint_left_C1 = C1.lower_endpoint(False, left_edge_C1_index)
        lower_endpoint_right_C1 = C1.lower_endpoint(True, right_edge_C1_index)
        lower_endpoint_left_C2 = C2.lower_endpoint(False, left_edge_C2_index)
        lower_endpoint_right_C2 = C2.lower_endpoint(True, right_edge_C2_index)

        print(lower_endpoint_left_C1)
        print(lower_endpoint_right_C1)
        print(lower_endpoint_left_C2)
        print(lower_endpoint_right_C2)

        if lower_endpoint_right_C2 is None and lower_endpoint_right_C1 is None and lower_endpoint_left_C2 is None and \
                lower_endpoint_left_C1 is None:
            break

        current = max(lower_endpoint_left_C1, lower_endpoint_left_C2, lower_endpoint_right_C1, lower_endpoint_right_C2,
                      key=lambda t: (-1) * 10 ** 21 if t is None else t[1])

        print(current)

        if current == lower_endpoint_left_C1:
            handle_event(C, C1, C2, left_edge_C2_index, right_edge_C2_index, left_edge_C1_index,
                         current, False)
            left_edge_C1_index += 1
            if left_edge_C1_index >= len(C1.left):
                left_edge_C1_index = None

        elif current == lower_endpoint_right_C1:
            handle_event(C, C1, C2, left_edge_C2_index, right_edge_C2_index, right_edge_C1_index,
                         current, True)
            right_edge_C1_index += 1
            if right_edge_C1_index >= len(C1.right):
                right_edge_C1_index = None

        elif current == lower_endpoint_left_C2:
            handle_event(C, C2, C1, left_edge_C1_index, right_edge_C1_index, left_edge_C2_index,
                         current, False)
            left_edge_C2_index += 1
            if left_edge_C2_index >= len(C2.left):
                left_edge_C2_index = None

        elif current == lower_endpoint_right_C2:
            handle_event(C, C2, C1, left_edge_C1_index, right_edge_C1_index, right_edge_C2_index,
                         current, True)
            right_edge_C2_index += 1
            if right_edge_C2_index >= len(C2.right):
                right_edge_C2_index = None

    return C


def handle_event(C, C0, C3, left_edge_C3_index, right_edge_C3_index, current_line_index, point, is_right):
    current_line = C0.get(current_line_index, is_right)
    if left_edge_C3_index is None:
        left_edge_C3 = None
    else:
        left_edge_C3 = C3.left[left_edge_C3_index]
    if right_edge_C3_index is None:
        right_edge_C3 = None
    else:
        right_edge_C3 = C3.right[right_edge_C3_index]

    if is_between(point, left_edge_C3, right_edge_C3):
        C.append(current_line, is_right)

    if right_edge_C3 is not None:
        intersection = intersection_of_lines(current_line, right_edge_C3)
        if intersection is not None:
            if not right_edge_C3.is_to_left(point):
                C.append(current_line, is_right)
                C.right.append(right_edge_C3)

    if left_edge_C3 is not None:
        intersection = intersection_of_lines(current_line, left_edge_C3)
        if intersection is not None:
            if left_edge_C3.is_to_left(point):
                C.append(current_line, is_right)
            else:
                C.left.append(left_edge_C3)


c = intersect_halfplanes(
    [HalfPlane(2, 1, False), HalfPlane(3, -6, True)])

print(c.left)
print(c.right)
