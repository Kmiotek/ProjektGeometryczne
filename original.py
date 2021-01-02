import math

from Visualization import Scene, PointsCollection, LinesCollection, Plot
from originalData import Point, Circle, Arc, Edge
from PriorityQueue import PriorityQueue


def find_circle_center(a, b, c):  # function from internet
    # check if bc is a "right turn" from ab
    if ((b.x - a.x) * (c.y - a.y) - (c.x - a.x) * (b.y - a.y)) > 0:
        return None, None

    # Joseph O'Rourke, Computational Geometry in C (2nd ed.) p.189
    A = b.x - a.x
    B = b.y - a.y
    C = c.x - a.x
    D = c.y - a.y
    E = A * (a.x + b.x) + B * (a.y + b.y)
    F = C * (a.x + c.x) + D * (a.y + c.y)
    G = 2 * (A * (c.y - b.y) - B * (c.x - b.x))

    if G == 0:
        return None, None  # Points are co-linear

    # point o is the center of the circle
    ox = 1.0 * (D * E - B * F) / G
    oy = 1.0 * (A * F - C * E) / G

    # o.x plus radius equals max x coord
    x = ox + math.sqrt((a.x - ox) ** 2 + (a.y - oy) ** 2)
    o = Point(ox, oy)

    return x, o


def calculate_parabolas_intersection(parabola1, parabola2, sweep_line):
    z0 = 2.0 * (parabola1.x - sweep_line)
    z1 = 2.0 * (parabola2.x - sweep_line)

    a = 1.0 / z0 - 1.0 / z1
    b = -2.0 * (parabola1.y / z0 - parabola2.y / z1)
    c = 1.0 * (parabola1.y ** 2 + parabola1.x ** 2 - sweep_line ** 2) / z0 - 1.0 * (
            parabola2.y ** 2 + parabola2.x ** 2 - sweep_line ** 2) / z1

    py = 1.0 * (-b - math.sqrt(b * b - 4 * a * c)) / (2 * a)
    px = 1.0 * (parabola1.x ** 2 + (parabola1.y - py) ** 2 - sweep_line ** 2) / (2 * parabola1.x - 2 * sweep_line)
    return Point(px, py)


def find_intersection_of_parabolas(parabola1, parabola2, sweep_line):
    if parabola1.x == parabola2.x:
        py = (parabola1.y + parabola2.y) / 2.0
        px = 1.0 * (parabola1.x ** 2 + (parabola1.y - py) ** 2 - sweep_line ** 2) / (2 * parabola1.x - 2 * sweep_line)
        return Point(px, py)
    elif parabola2.x == sweep_line:
        py = parabola2.y
        px = 1.0 * (parabola1.x ** 2 + (parabola1.y - py) ** 2 - sweep_line ** 2) / (2 * parabola1.x - 2 * sweep_line)
        return Point(px, py)
    elif parabola1.x == sweep_line:
        py = parabola1.y
        px = 1.0 * (parabola2.x ** 2 + (parabola2.y - py) ** 2 - sweep_line ** 2) / (2 * parabola2.x - 2 * sweep_line)
        return Point(px, py)
    else:
        return calculate_parabolas_intersection(parabola1, parabola2, sweep_line)


def intersect(point, arc):
    if arc is None:
        return None
    if arc.point.x == point.x:
        return None

    y1 = 0.0
    y2 = 0.0

    if arc.prev is not None:
        y1 = find_intersection_of_parabolas(arc.prev.point, arc.point, point.x).y
    if arc.next is not None:
        y2 = find_intersection_of_parabolas(arc.point, arc.next.point, point.x).y

    if (arc.prev is None or y1 <= point.y) and (arc.next is None or point.y <= y2):
        py = point.y
        px = (arc.point.x ** 2 + (arc.point.y - py) ** 2 - point.x ** 2) / (2 * arc.point.x - 2 * point.x)
        res = Point(px, py)
        return res
    return None


def intersection_of_lines(line1, line2):
    p1 = ((line1[0].x * line1[1].y - line1[0].y * line1[1].x) * (line2[0].x - line2[1].x) - (line1[0].x - line1[1].x)
          * (line2[0].x * line2[1].y - line2[0].y * line2[1].x)) / \
         ((line1[0].x - line1[1].x) * (line2[0].y - line2[1].y) - (line1[0].y - line1[1].y) * (line2[0].x - line2[1].x))
    p2 = ((line1[0].x * line1[1].y - line1[0].y * line1[1].x) * (line2[0].y - line2[1].y) - (line1[0].y - line1[1].y)
          * (line2[0].x * line2[1].y - line2[0].y * line2[1].x)) / \
         ((line1[0].x - line1[1].x) * (line2[0].y - line2[1].y) - (line1[0].y - line1[1].y) * (line2[0].x - line2[1].x))
    return Point(p1, p2)


def get_bounds(center, size):
    upper_left = Point(center.x - size, center.y + size)
    upper_right = Point(center.x + size, center.y + size)
    lower_left = Point(center.x - size, center.y - size)
    lower_right = Point(center.x + size, center.y - size)
    bounds = [(upper_left, upper_right), (lower_left, lower_right), (upper_right, lower_right),
              (upper_left, lower_left)]
    return bounds


def lines_from_bounds(bounds):
    result = []
    for boundary in bounds:
        result.append([(boundary[0].x, boundary[0].y), (boundary[1].x, boundary[1].y)])
    return result


class Voronoi:
    def __init__(self, points):
        self.voronoi = []
        self.beach_line = None
        self.points = points
        self.scenes = []

        self.events = PriorityQueue()

        self.LEFT = -50
        self.RIGHT = 50
        self.BOTTOM = -50
        self.TOP = 50

        self.create_bounding_box(points)

    def create_bounding_box(self, points):
        for pts in points:
            point = Point(pts[0], pts[1])
            self.events.push(point)
            if point.x < self.LEFT:
                self.LEFT = point.x
            if point.y < self.BOTTOM:
                self.BOTTOM = point.y
            if point.x > self.RIGHT:
                self.RIGHT = point.x
            if point.y > self.TOP:
                self.TOP = point.y

        dx = (self.RIGHT - self.LEFT + 1) / 5.0
        dy = (self.TOP - self.BOTTOM + 1) / 5.0
        self.LEFT = self.LEFT - dx
        self.RIGHT = self.RIGHT + dx
        self.BOTTOM = self.BOTTOM - dy
        self.TOP = self.TOP + dy

    def calculate_voronoi_diagram(self):
        while not self.events.empty():
            event = self.events.pop()
            if isinstance(event, Circle):
                self.handle_circle_event(event)
            else:
                self.handle_point_event(event)

        self.scenes.append(Scene([PointsCollection(self.points, color='red'),
                                  PointsCollection(self.get_voronoi_points(), color='blue')],
                                 [LinesCollection(self.get_voronoi_lines())]))

        self.finish_edges()
        self.scenes.append(Scene([PointsCollection(self.points, color='red'),
                                  PointsCollection(self.get_voronoi_points(), color='blue')],
                                 [LinesCollection(self.get_voronoi_lines())]))
        self.bound(Point(0, 0), 20)
        self.scenes.append(Scene([PointsCollection(self.points, color='red'),
                                  PointsCollection(self.get_voronoi_points(), color='blue')],
                                 [LinesCollection(self.get_voronoi_lines()),
                                  LinesCollection(lines_from_bounds(get_bounds(Point(0, 0), 20)), color='black')]))

    def handle_point_event(self, event):
        self.insert_arc(event)

    def handle_circle_event(self, event):
        if event.valid:
            edge = Edge(event.point)
            self.voronoi.append(edge)

            arc = event.arc
            if arc.prev is not None:
                arc.prev.next = arc.next
                arc.prev.lower_edge = edge
            if arc.next is not None:
                arc.next.prev = arc.prev
                arc.next.upper_edge = edge

            if arc.upper_edge is not None:
                arc.upper_edge.finish(event.point)
            if arc.lower_edge is not None:
                arc.lower_edge.finish(event.point)

            if arc.prev is not None:
                self.check_circle_event(arc.prev)
            if arc.next is not None:
                self.check_circle_event(arc.next)

    def insert_arc(self, point):
        if self.beach_line is None:
            self.beach_line = Arc(point)
            return

        if self.insert_arc_among_existing(point):
            return

        arc = self.beach_line
        while arc.next is not None:
            arc = arc.next
        arc.next = Arc(point, arc)

        x = self.LEFT
        y = (arc.next.point.y + arc.point.y) / 2.0
        start = Point(x, y)

        seg = Edge(start)
        arc.lower_edge = arc.next.upper_edge = seg
        self.voronoi.append(seg)

    def insert_arc_among_existing(self, point):
        arc = self.beach_line
        while arc is not None:
            intersection_point = intersect(point, arc)
            if intersection_point is not None:
                second_intersection_point = intersect(point, arc.next)
                if (arc.next is not None) and second_intersection_point is None:
                    arc.next.prev = Arc(arc.point, arc, arc.next)
                    arc.next = arc.next.prev
                else:
                    arc.next = Arc(arc.point, arc)
                arc.next.lower_edge = arc.lower_edge

                arc.next.prev = Arc(point, arc, arc.next)
                arc.next = arc.next.prev

                arc = arc.next

                seg = Edge(intersection_point)
                self.voronoi.append(seg)
                arc.prev.lower_edge = arc.upper_edge = seg

                seg = Edge(intersection_point)
                self.voronoi.append(seg)
                arc.next.upper_edge = arc.lower_edge = seg

                self.check_circle_event(arc)
                self.check_circle_event(arc.prev)
                self.check_circle_event(arc.next)

                return True

            arc = arc.next
        return False

    def check_circle_event(self, arc):
        if arc.circle_event is not None and arc.circle_event.x != self.LEFT:
            arc.circle_event.valid = False
        arc.circle_event = None

        if arc.prev is None or arc.next is None:
            return

        max_x, o = find_circle_center(arc.prev.point, arc.point, arc.next.point)
        if o is not None and max_x > self.LEFT:
            arc.circle_event = Circle(max_x, o, arc)
            self.events.push(arc.circle_event)

    def finish_edges(self):
        limit = self.RIGHT + (self.RIGHT - self.LEFT) + (self.TOP - self.BOTTOM)
        arc = self.beach_line
        while arc.next is not None:
            if arc.lower_edge is not None:
                p = find_intersection_of_parabolas(arc.point, arc.next.point, limit * 2.0)
                arc.lower_edge.finish(p)
            arc = arc.next

    def print_output(self):
        for edge in self.voronoi:
            print(edge.start.x, edge.start.y, edge.end.x, edge.end.y)

    def get_voronoi_points(self):
        result = []
        for edge in self.voronoi:
            if edge.done:
                result.append((edge.start.x, edge.start.y))
                result.append((edge.end.x, edge.end.y))
            else:
                result.append((edge.start.x, edge.start.y))
        return result

    def get_voronoi_lines(self):
        result = []
        for edge in self.voronoi:
            if edge.done:
                result.append([(edge.start.x, edge.start.y), (edge.end.x, edge.end.y)])
        return result

    def bound(self, center, size):
        bounds = get_bounds(center, size)
        for edge in self.voronoi:
            if edge.end.y > center.y + size:
                intersection = intersection_of_lines(bounds[0], (edge.start, edge.end))
                edge.end = intersection
            if edge.end.x > center.x + size:
                intersection = intersection_of_lines(bounds[2], (edge.start, edge.end))
                edge.end = intersection
            if edge.end.y < center.y - size:
                intersection = intersection_of_lines(bounds[1], (edge.start, edge.end))
                edge.end = intersection
            if edge.end.x < center.x - size:
                intersection = intersection_of_lines(bounds[3], (edge.start, edge.end))
                edge.end = intersection


a = Voronoi([(4, 1), (0, 9), (1, 5), (7, 10), (-3, 11), (8, 4)])

a.calculate_voronoi_diagram()

print(a.scenes)

plot = Plot(a.scenes)
plot.draw()
