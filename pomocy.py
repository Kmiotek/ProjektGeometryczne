import math

from DataType import Point, Circle, Arc, Edge, PriorityQueue
from Visualization import Scene, PointsCollection, Plot, LinesCollection


def find_circle_center(a, b, c):
    # check if bc is a "right turn" from ab - det
    if ((b.x - a.x) * (c.y - a.y) - (c.x - a.x) * (b.y - a.y)) < 0:
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
    ox = (D * E - B * F) / G
    oy = (A * F - C * E) / G

    max_x = ox + math.sqrt((a.x - ox) ** 2 + (a.y - oy) ** 2)
    o = Point(ox, oy)

    return max_x, o


def find_intersection_of_parabolas(parabola1, parabola2, sweep_line):
    p = parabola1
    if parabola1.x == parabola2.x:
        py = (parabola1.y + parabola2.y) / 2.0
    elif parabola2.x == sweep_line:
        py = parabola2.y
    elif parabola1.x == sweep_line:
        py = parabola1.y
        p = parabola2
    else:
        return calculate_parabolas_intersection(parabola1, parabola2, sweep_line)

    px = (p.x ** 2 + (p.y - py) ** 2 - sweep_line ** 2) / (2 * p.x - 2 * sweep_line)
    res = Point(px, py)
    return res


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


def check_if_arc_intersects(point, arc):
    if arc is None:
        return None
    if arc.point.x == point.x:
        return None

    upper_intersection_y = 0
    lower_intersection_y = 0

    if arc.prev is not None:
        upper_intersection_y = (find_intersection_of_parabolas(arc.prev.point, arc.point, point.x)).y
    if arc.next is not None:
        lower_intersection_y = (find_intersection_of_parabolas(arc.point, arc.next.point, point.x)).y

    if (arc.prev is None or upper_intersection_y <= point.y) and (arc.next is None or point.y <= lower_intersection_y):
        py = point.y
        px = (arc.point.x ** 2 + (arc.point.y - py) ** 2 - point.x ** 2) / (2 * arc.point.x - 2 * point.x)
        return Point(px, py)
    return None


class Fortune:
    def __init__(self, points):
        self.voronoi = []
        self.beach_line = None
        self.scenes = []
        self.points = points

        self.events = PriorityQueue()

        # bounding box
        self.LEFT = -50
        self.RIGHT = -50
        self.TOP = 500
        self.BOTTOM = 500

        self.create_bounding_box(points)

    def create_bounding_box(self, points):
        for pts in points:
            point = Point(pts[0], pts[1])
            self.events.push(point)

            if point.x < self.LEFT:
                self.LEFT = point.x
            if point.y < self.TOP:
                self.TOP = point.y
            if point.x > self.RIGHT:
                self.RIGHT = point.x
            if point.y > self.BOTTOM:
                self.BOTTOM = point.y

        dx = (self.RIGHT - self.LEFT + 1) / 5.0
        dy = (self.BOTTOM - self.TOP + 1) / 5.0
        self.LEFT = self.LEFT - dx
        self.RIGHT = self.RIGHT + dx
        self.TOP = self.TOP - dy
        self.BOTTOM = self.BOTTOM + dy

    def calculate_voronoi_diagram(self):
        while not self.events.empty():
            event = self.events.pop()
            if isinstance(event, Circle):
                self.handle_circle_event(event)
            else:
                self.handle_point_event(event)

        self.finish_edges()

    def calculate_voronoi_diagram_with_visualization(self):
        while not self.events.empty():
            event = self.events.pop()
            if isinstance(event, Circle):
                self.handle_circle_event(event)
            else:
                self.handle_point_event(event)
            self.scenes.append(Scene([PointsCollection(self.points, color='red'),
                                      PointsCollection(self.get_voronoi_points(), color='blue')],
                                     [LinesCollection(self.get_voronoi_lines())]))
        self.finish_edges_with_visualization()

    def handle_point_event(self, point):
        self.insert_arc(point)

    def handle_circle_event(self, circle_event):
        if circle_event.valid:
            edge = Edge(circle_event.point)
            self.voronoi.append(edge)

            arc = circle_event.beach_line
            if arc.prev is not None:
                arc.prev.next = arc.next
                arc.prev.lower_edge = edge
            if arc.next is not None:
                arc.next.prev = arc.prev
                arc.next.upper_edge = edge

            if arc.upper_edge is not None:
                arc.upper_edge.finish(circle_event.point)
            if arc.lower_edge is not None:
                arc.lower_edge.finish(circle_event.point)

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

        edge = Edge(start)
        arc.lower_edge = arc.next.upper_edge = edge
        self.voronoi.append(edge)

    def insert_arc_among_existing(self, point):
        arc = self.beach_line
        while arc is not None:
            intersection_point = check_if_arc_intersects(point, arc)
            if intersection_point is not None:
                second_intersection_point = check_if_arc_intersects(point, arc.next)
                if arc.next is not None and second_intersection_point is None:
                    arc.next.prev = Arc(arc.point, arc, arc.next)
                    arc.next = arc.next.prev
                else:
                    arc.next = Arc(arc.point, arc)
                arc.next.lower_edge = arc.lower_edge

                arc.next.prev = Arc(point, arc, arc.next)
                arc.next = arc.next.prev
                arc = arc.next

                edge = Edge(intersection_point)
                self.voronoi.append(edge)
                arc.prev.lower_edge = arc.upper_edge = edge

                edge = Edge(intersection_point)
                self.voronoi.append(edge)
                arc.next.upper_edge = arc.lower_edge = edge

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

        max_x, center = find_circle_center(arc.prev.point, arc.point, arc.next.point)
        if center is not None and max_x > self.LEFT:
            arc.circle_event = Circle(max_x, center, arc)
            self.events.push(arc.circle_event)

    def finish_edges(self):
        limit = self.RIGHT + (self.RIGHT - self.LEFT) + (self.BOTTOM - self.TOP)
        arc = self.beach_line
        while arc.next is not None:
            if arc.lower_edge is not None:
                point = find_intersection_of_parabolas(arc.point, arc.next.point, limit * 2.0)
                arc.lower_edge.finish(Point(-1 * point.x, -1 * point.y))
            arc = arc.next

    def finish_edges_with_visualization(self):
        limit = self.RIGHT + (self.RIGHT - self.LEFT) + (self.BOTTOM - self.TOP)
        arc = self.beach_line
        while arc.next is not None:
            if arc.lower_edge is not None:
                point = find_intersection_of_parabolas(arc.point, arc.next.point, limit * 2.0)
                arc.lower_edge.finish(Point(-1 * point.x, -1 * point.y))
                self.scenes.append(Scene([PointsCollection(self.points, color='red'),
                                          PointsCollection(self.get_voronoi_points(), color='blue')],
                                         [LinesCollection(self.get_voronoi_lines())]))
            arc = arc.next

    def print_output(self):
        for edge in self.voronoi:
            if edge.done:
                print(edge.start.x, edge.start.y, edge.end.x, edge.end.y)
            else:
                print(edge.start.x, edge.start.y)

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




a = Fortune([(4, 1), (0, 9), (1, 5), (7, 10), (-3, 11), (8, 4)])

a.calculate_voronoi_diagram_with_visualization()

print(a.scenes)

plot = Plot(a.scenes)
plot.draw()

a.print_output()
