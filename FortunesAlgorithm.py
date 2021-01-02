from PriorityQueue import PriorityQueue

BOTTOM = -500
TOP = 500
LEFT = -500
RIGHT = 500


class CircleEvent:
    def __init__(self, y, point, arc):
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


class Fortune:
    diagram = []
    beachLine = None
    events = PriorityQueue()

    def findParabolasIntersection(self, sweep, point1, point2):
        ys = sweep
        x1, y1 = point1.x, point1.y
        x2, y2 = point2.x, point2.y
        if y1 == y2:
            xRes = (x1+x2)/2
            yRes = y1
            return Point(xRes, yRes)
        elif y1 == sweep:
            xRes = x1
            yRes = (xRes ** 2 - 2 * xRes * x2 + x2 ** 2 - ys ** 2 + y2 ** 2) / (2 * (y2 - ys))
            return Point(xRes, yRes)

        elif y2 == sweep:
            xRes = x2
            yRes = (xRes ** 2 - 2 * xRes * x1 + x1 ** 2 - ys ** 2 + y1 ** 2) / (2 * (y1 - ys))
            return Point(xRes, yRes)
        else:
            a = 2 * (y2 - y1)
            b = 4 * (-x1 * y2 + x1 * ys + x2 * y1 - x2 * ys)
            c = 2 * ((y2 - ys) * (x1 ** 2 - ys ** 2 + y1 ** 2) - (y1 - ys)*(x2 ** 2 - ys ** 2 + y2 ** 2))

            d = b ** 2 - 4 * a * c

            xRes = (-b - d ** 0.5) / 2 * a
            yRes = (xRes ** 2 - 2 * xRes * x1 + x1 ** 2 - ys ** 2 + y1 ** 2) / (2 * (y1 - ys))

            return Point(xRes, yRes)

    def checkArc(self, point, arc):
        if arc is None:
            return None
        if point.y == arc.point.y:
            return None

        leftIntersection = Point(0, 0)
        rightIntersection = Point(0, 0)

        if arc.prev is not None:
            leftIntersection = self.findParabolasIntersection(point.x, arc.prev.point, point)
        if arc.next is not None:
            rightIntersection = self.findParabolasIntersection(point.x, point, arc.next.point)

        if (arc.prev is None or leftIntersection.x <= point.x) and (arc.next is None or point.x <= rightIntersection.x):
            y = (arc.point.y ** 2 + (arc.point.x - point.x) ** 2 - point.y ** 2) / (2 * arc.point.y - 2 * point.y)
            return Point(point.x, y)

        return None

    def checkCircleEvent(self, arc, y):
        if arc.event is not None and arc.event.point.y != BOTTOM:
            arc.event.valid = False

        arc.event = None

        if arc.prev is None or arc.next is None:
            return
        yMax, center = self.findCircleCenter(arc.prev.point, arc.point, arc.next.point)

        if center is not None and yMax > BOTTOM:
            arc.event = CircleEvent(yMax, center, arc)
            self.events.push(arc.event)

    def handlePointEvent(self, point):
        if self.beachLine is None:
            self.beachLine = Arc(point)
        else:
            arc = self.beachLine
            while arc is not None:
                intersection = self.checkArc(point, arc)
                if intersection is not None:
                    check = self.checkArc(point, arc.next)
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
                    self.diagram.append(halfEdge)
                    arc.prev.secondHalfEdge = arc.firstHalfEdge = halfEdge

                    halfEdge = HalfEdge(intersection)
                    self.diagram.append(halfEdge)
                    arc.prev.firstHalfEdge = arc.secondHalfEdge = halfEdge

                    self.checkCircleEvent(arc.prev, point.y)
                    self.checkCircleEvent(arc, point.y)
                    self.checkCircleEvent(arc.next, point.y)

                    break

                arc = arc.next

            arc = self.beachLine

            while arc.next is not None:
                arc = arc.next
            arc.next = Arc(point, arc)

            x = (arc.next.point.x + arc.point.x) / 2

            start = Point(x, TOP)

            halfEdge = HalfEdge(start)
            self.diagram.append(halfEdge)
            arc.secondHalfEdge = arc.next.firstHalfEdge = halfEdge

    def handleCircleEvent(self, event):
        if event.valid:
            halfEdge = HalfEdge(event.point)
            self.diagram.append(halfEdge)

            if event.arc.prev is not None:
                event.arc.prev.next = event.arc.next
                event.arc.secondHalfEdge = halfEdge
            if event.arc.next is not None:
                event.arc.next.prev = event.arc.prev
                event.arc.firstHalfEdge = halfEdge

            if event.arc.firstHalfEdge is not None:
                event.arc.firstHalfEdge.finish(event.point)

            if event.arc.secondHalfEdge is not None:
                event.arc.secondHalfEdge.finish(event.point)

            if event.arc.prev is not None:
                self.checkCircleEvent(event.arc.prev, event.y)

            if event.arc.next is not None:
                self.checkCircleEvent(event.arc.next, event.y)

    def findCircleCenter(self, a, b, c):
        x1, y1 = a.x, a.y
        x2, y2 = b.x, b.y
        x3, y3 = c.x, c.y

        if x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2) == 0:
            return None, None

        xs = 0.5 * ((x2 ** 2) * y3 + (y2 ** 2) * y3 - (x1 ** 2) * y3 - (y1 ** 2) * y3 + (x1 ** 2) * y2 + (
                y1 ** 2) * y2 - (
                            x3 ** 2) * y2 - (y3 ** 2) * y2 + (x3 ** 2) * y1 + (y3 ** 2) * y1 - (x2 ** 2) * y1 - (
                            y2 ** 2) * y1) / (
                     y1 * x3 - y1 * x2 + y2 * x1 - y2 * x3 + y3 * x2 - y3 * x1)

        ys = 0.5 * (-x1 * (x3 ** 2) - x1 * (y3 ** 2) + x1 * (x2 ** 2) + x1 * (y2 ** 2) + x2 * (x3 ** 2) + x2 * (
                y3 ** 2) - (
                            x2 ** 2) * x3 - (y2 ** 2) * x3 + (x1 ** 2) * x3 - (x1 ** 2) * x2 + (y1 ** 2) * x3 - (
                            y1 ** 2) * x2) / (
                     y1 * x3 - y1 * x2 - y2 * x3 - y3 * x1 + y3 * x2 + y2 * x1)
        yMax = ys + ((x1 - xs) ** 2 + (y1 - ys) ** 2) ** 0.5
        return yMax, Point(xs, ys)

    def finishHalfEdges(self):
        arc = self.beachLine
        while arc is not None:
            if arc.secondHalfEdge is not None:
                end = self.findParabolasIntersection(BOTTOM, arc.point, arc.next.point)
                arc.secondHalfEdge.finish(end)

            arc = arc.next

    def printOutput(self):
        for d in self.diagram:
            p0 = d.start
            p1 = d.end

            print(p0.x, p0.y)

    def Fortune(self, points):
        for point in points:
            self.events.push( Point(point[0], point[1]) )

        while not self.events.empty():
            event = self.events.pop()
            if isinstance(event, Point):
                self.handlePointEvent(event)
            else:
                self.handleCircleEvent(event)

        self.finishHalfEdges()
        self.printOutput()


a = Fortune()

a.Fortune([(1, 0), (2, 2), (3, 0), (4,6)])
