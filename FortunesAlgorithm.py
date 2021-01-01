from PriorityQueue import PriorityQueue


class CircleEvent:
    def __init__(self,y,point,arc):
        self.y = y
        self.x = point.x
        self.point = point
        self.arc = arc
        self.valid = True

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Arc:
    def __init__(self, p, prev=None, next=None):
        self.point = p
        self.prev = prev
        self.next = next
        self.event = None
        self.halfEdge = None


class HalfEdge:
    def __init__(self, start):
        self.start = start
        self.end = None

    def finish(self, end):
        if self.end is not None:
            return
        else:
            self.end = end




def findArc(T, point):
    try:
        res = T.ceiling_item(point[0])[1]
        if res[1][1] == 'leaf':
            return res
        else:
            return res[1][2]
    except:
        pass

    try:
        res = T.floor_item(point[0])[1]
        if res[1][1] == 'leaf':
            return res
        else:
            return res[1][3]
    except:
        return None


def findParabolasIntersections(sweep, point1, point2):
    ys = sweep
    x1, y1 = point1.x, point1.y
    x2, y2 = point2.x, point2.y

    a = 2 * (y2 - y1)
    b = 4 * (-x1 * y2 + x1 * ys + x2 * y1 - x2 * ys)
    c = 2 * ((y2 - ys) * (x1 ** 2 - ys ** 2 + y1 ** 2) - (y1 - ys)(x2 ** 2 - ys ** 2 + y2 ** 2))

    d = b ** 2 - 4 * a * c

    xRes1 = (-b - d ** 0.5) / 2 * a
    xRes2 = (-b + d ** 0.5) / 2 * a
    yRes1 = (xRes1 ** 2 - 2 * xRes1 * x1 + x1 ** 2 - ys ** 2 + y1 ** 2) / (2 * (y1 - ys))
    yRes2 = (xRes2 ** 2 - 2 * xRes2 * x1 + x1 ** 2 - ys ** 2 + y1 ** 2) / (2 * (y1 - ys))

    return (xRes1, yRes1), (xRes2, yRes2)


def handlePointEvent(point, Q, T, beachLinePoints, diagramPoints, diagramEdges):
    arc = findArc(T, point)
    if arc is None:
        beachLinePoints.insert(point[0], point)
        T.insert(point[0], (point, "leaf"))

    else:
        curr = T.get_value(arc[0][0])

        intersection1, intersection2 = findParabolasIntersections(point[1], point, curr[0])

        if point[0] < intersection1[0] < curr[0][0]:
            T.insert(intersection1[0], (intersection1, "intersection", point, curr[0]))  # (point, "label", left, right)
        elif curr[0][0] < intersection1[0] < point[0]:
            T.insert(intersection1[0], (intersection1, "intersection", curr[0], point))  # (point, "label", left, right)
        else:
            if intersection1[0] > point[0]:
                T.insert(intersection1[0],
                         (intersection1, "intersection", point, curr[0]))  # (point, "label", left, right)
            else:
                T.insert(intersection1[0],
                         (intersection1, "intersection", curr[0], point))  # (point, "label", left, right)

        if point[0] < intersection2[0] < curr[0][0]:
            T.insert(intersection2[0], (intersection2, "intersection", point, curr[0]))  # (point, "label", left, right)
        elif curr[0][0] < intersection2[0] < point[0]:
            T.insert(intersection2[0], (intersection2, "intersection", curr[0], point))  # (point, "label", left, right)
        else:
            if intersection2[0] > point[0]:
                T.insert(intersection2[0],
                         (intersection2, "intersection", point, curr[0]))  # (point, "label", left, right)
            else:
                T.insert(intersection2[0],
                         (intersection2, "intersection", curr[0], point))  # (point, "label", left, right)

    # add edge to D

    # find circle events
    points = beachLinePoints.items()
    for i in range(len(points) - 2):
        center = findCircleCenter(points[i], points[i + 1], points[i + 2])
        if center[1] < point[1]:
            Q.push( center)


def handleCircleEvent(point, Q, T, beachLinePoints, diagramPoints, diagramEdges):
    diagramPoints.append(point)

    # remove parabola

    # add edge

    # find circle events
    points = beachLinePoints.items()
    for i in range(len(points) - 2):
        center = findCircleCenter(points[i], points[i + 1], points[i + 2])
        if center[1] < point[1]:
            Q.push( center)


def findCircleCenter(a, b, c):
    x1, y1 = a.x, a.y
    x2, y2 = b.x, b.y
    x3, y3 = c.x, c.y

    xs = 0.5 * ((x2 ** 2) * y3 + (y2 ** 2) * y3 - (x1 ** 2) * y3 - (y1 ** 2) * y3 + (x1 ** 2) * y2 + (y1 ** 2) * y2 - (
            x3 ** 2) * y2 - (y3 ** 2) * y2 + (x3 ** 2) * y1 + (y3 ** 2) * y1 - (x2 ** 2) * y1 - (y2 ** 2) * y1) / (
                 y1 * x3 - y1 * x2 + y2 * x1 - y2 * x3 + y3 * x2 - y3 * x1)

    ys = 0.5 * (-x1 * (x3 ** 2) - x1 * (y3 ** 2) + x1 * (x2 ** 2) + x1 * (y2 ** 2) + x2 * (x3 ** 2) + x2 * (y3 ** 2) - (
            x2 ** 2) * x3 - (y2 ** 2) * x3 + (x1 ** 2) * x3 - (x1 ** 2) * x2 + (y1 ** 2) * x3 - (y1 ** 2) * x2) / (
                 y1 * x3 - y1 * x2 - y2 * x3 - y3 * x1 + y3 * x2 + y2 * x1)

    return Point(xs, ys)


def findCircleEvents():
    pass


def Fortune(points):
    diagramPoints = []
    diagramEdges = {}
    T = None
    Q = PriorityQueue()
    for point in points:
        Q.push(Point(point[0],point[1]))

    while Q:
        event = Q.pop()
        if event[2]:
            handlePointEvent(event[1], Q, T, beachLinePoints, diagramPoints, diagramEdges)
        else:
            handleCircleEvent()
