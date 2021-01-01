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
        self.firstHalfEdge = None
        self.secondHalfEdge = None


class HalfEdge:
    def __init__(self, start):
        self.start = start
        self.end = None

    def finish(self, end):
        if self.end is not None:
            return
        else:
            self.end = end






def findParabolasIntersections(sweep, point1, point2):
    ys = sweep
    x1, y1 = point1.x, point1.y
    x2, y2 = point2.x, point2.y

    a = 2 * (y2 - y1)
    b = 4 * (-x1 * y2 + x1 * ys + x2 * y1 - x2 * ys)
    c = 2 * ((y2 - ys) * (x1 ** 2 - ys ** 2 + y1 ** 2) - (y1 - ys)(x2 ** 2 - ys ** 2 + y2 ** 2))

    d = b ** 2 - 4 * a * c

    xRes1 = (-b - d ** 0.5) / 2 * a
    yRes1 = (xRes1 ** 2 - 2 * xRes1 * x1 + x1 ** 2 - ys ** 2 + y1 ** 2) / (2 * (y1 - ys))

    return Point(xRes1, yRes1)


def checkArc(point, arc):
    if arc is None:
        return None
    if point.y == arc.point.y:
        return  None

    leftIntersection = rightIntersection = 0


    if arc.prev is not None:
        leftIntersection = findParabolasIntersections(point[0], arc.prev.point, point)
    if arc.next is not None:
        rightIntersection = findParabolasIntersections(point[0], point, arc.next.point)

    if (arc.prev is None or leftIntersection.x <= point.x) and (arc.next is None or point.x <= rightIntersection.x):
        y = (arc.point.x ** 2 + (arc.point.y - py) ** 2 - point.x ** 2) / (2 * arc.point.x - 2 * point.x)
        return  Point(point.x, y)

    return  None


def handlePointEvent(point, Q, T, D):

    if T is None:
        T.append(Arc(point))
    else:
        arc = T
        while arc is not None:
            intersection = checkArc(point, arc)
            if intersection is not None:
                check = checkArc(point, arc.next)
                if arc.next is not None and check is None:
                    arc.next.prev = Arc(arc.point, arc, arc.next)
                    arc.next = arc.next.prev
                else:
                    arc.next = Arc(arc.point)
                arc.next.secondHalfEdge = arc.secondHalfEdge

                arc.next.prev = Arc(point, arc, arc.next)
                arc.next = arc.next.prev

                arc = arc.next

                halfEdge = HalfEdge(intersection)
                D.append(halfEdge)
                arc.prev.secondHalfEdge = arc.firstHalfEdge = halfEdge

                halfEdge = HalfEdge(intersection)
                D.append(halfEdge)
                arc.prev.firstHalfEdge = arc.secondHalfEdge = halfEdge

                #check for circle events

                break

            arc = arc.next

        arc = T

        while arc.next is not None:
            arc = arc.next
        arc.next = Arc(point, arc)

        x = (arc.next.point.x + arc.point.x)/2

        start = Point(x, borderTop)

        halfEdge = HalfEdge(start)
        D.append(halfEdge)
        arc.secondHalfEdge = arc.next.firstHalfEdge = halfEdge





# def handleCircleEvent(point, Q, T, beachLinePoints, diagramPoints, diagramEdges):
#     diagramPoints.append(point)
#
#     # remove parabola
#
#     # add edge
#
#     # find circle events
#     points = beachLinePoints.items()
#     for i in range(len(points) - 2):
#         center = findCircleCenter(points[i], points[i + 1], points[i + 2])
#         if center[1] < point[1]:
#             Q.push( center)


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
    D = []
    T = []
    Q = PriorityQueue()
    for point in points:
        Q.push(Point(point[0],point[1]))

    while Q:
        event = Q.pop()
        if event[2]:
            handlePointEvent(event[1], Q, T, beachLinePoints, D)
        else:
            handleCircleEvent()
