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

    def findIntersection(self, sweep, i, j):

        p: Point = i

        # First we replace some stuff to make it easier
        a = i.x
        b = i.y
        c = j.x
        d = j.y
        u = 2 * (b - sweep)
        v = 2 * (d - sweep)
        xRes = 0
        yRes = 0

        # Handle the case where the two points have the same y-coordinate (breakpoint is in the middle)
        if i.y == j.y:
            xRes = (i.x + j.x) / 2

            if j.x < i.x:
                yRes = TOP
                return Point(xRes,yRes)

        # Handle cases where one point's y-coordinate is the same as the sweep line
        elif i.y == sweep:
            xRes = i.x
            p = j
        elif j.y == sweep:
            xRes = j.x
        else:
            # We now need to solve for x
            # 1/u * (x**2 - 2*a*x + a**2 + b**2 - l**2) = 1/v * (x**2 - 2*c*x + c**2 + d**2 - l**2)
            # Then we let Wolfram alpha do the heavy work for us, and we put it here in the code :D
            xRes = -((
                v * (a ** 2 * u - 2 * a * c * u + b ** 2 * (u - v) + c ** 2 * u) + d ** 2 * u * (v - u) + sweep ** 2 * (
                        u - v) ** 2)**0.5 + a * v - c * u) / (u - v)


        # We have to re-evaluate this, since the point might have been changed
        a = p.x
        b = p.y
        x = xRes
        u = 2 * (b - sweep)

        # Handle degenerate case where parabolas don't intersect
        if u == 0:
            yRes = float("inf")
            return Point(xRes,yRes)

        # And we put everything back in y
        yRes = 1 / u * (x ** 2 - 2 * a * x + a ** 2 + b ** 2 - sweep ** 2)
        return Point(xRes,yRes)

    # def findParabolasIntersection(self, sweep, point1, point2):
    #     ys = sweep
    #     x1, y1 = point1.x, point1.y
    #     x2, y2 = point2.x, point2.y
    #     if y1 == y2:
    #         xRes = (x1 + x2) / 2
    #         yRes = y1
    #         return Point(xRes, yRes)
    #     elif y1 == sweep:
    #         xRes = x1
    #         yRes = (xRes ** 2 - 2 * xRes * x2 + x2 ** 2 - ys ** 2 + y2 ** 2) / (2 * (y2 - ys))
    #         return Point(xRes, yRes)
    #
    #     elif y2 == sweep:
    #         xRes = x2
    #         yRes = (xRes ** 2 - 2 * xRes * x1 + x1 ** 2 - ys ** 2 + y1 ** 2) / (2 * (y1 - ys))
    #         return Point(xRes, yRes)
    #     else:
    #         a = 2 * (y2 - y1)
    #         b = 4 * (-x1 * y2 + x1 * ys + x2 * y1 - x2 * ys)
    #         c = 2 * ((y2 - ys) * (x1 ** 2 - ys ** 2 + y1 ** 2) - (y1 - ys) * (x2 ** 2 - ys ** 2 + y2 ** 2))
    #
    #         d = b ** 2 - 4 * a * c
    #
    #         xRes = (-b - d ** 0.5) / 2 * a
    #         yRes = (xRes ** 2 - 2 * xRes * x1 + x1 ** 2 - ys ** 2 + y1 ** 2) / (2 * (y1 - ys))
    #
    #         return Point(xRes, yRes)

    def checkArc(self, point, arc):
        if arc is None:
            return None
        if point.y == arc.point.y:
            return None

        leftIntersection = Point(0, 0)
        rightIntersection = Point(0, 0)

        if arc.prev is not None:
            leftIntersection = self.findIntersection(point.y, arc.prev.point, point)
        if arc.next is not None:
            rightIntersection = self.findIntersection(point.y, point, arc.next.point)

        if (arc.prev is None or leftIntersection.x <= point.x) and (arc.next is None or point.x <= rightIntersection.x):
            y = (arc.point.y ** 2 + (arc.point.x - point.x) ** 2 - point.y ** 2) / (2 * arc.point.y - 2 * point.y)

            return Point(point.x, y)

        return None

    def checkCircleEvent(self, arc, y):
        if arc.event is not None and arc.event.point.y != TOP:
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
                        arc.next = Arc(arc.point, arc)
                    arc.next.secondHalfEdge = arc.secondHalfEdge

                    arc.next.prev = Arc(point, arc, arc.next)
                    arc.next = arc.next.prev

                    arc = arc.next

                    halfEdge = HalfEdge(intersection)
                    self.diagram.append(halfEdge)
                    arc.prev.secondHalfEdge = arc.firstHalfEdge = halfEdge

                    halfEdge = HalfEdge(intersection)
                    self.diagram.append(halfEdge)
                    arc.next.firstHalfEdge = arc.secondHalfEdge = halfEdge

                    self.checkCircleEvent(arc.prev, point.y)
                    self.checkCircleEvent(arc, point.y)
                    self.checkCircleEvent(arc.next, point.y)

                    return

                arc = arc.next

            arc = self.beachLine

            while arc.next is not None:
                arc = arc.next
            arc.next = Arc(point, arc)

            x = (arc.next.point.x + arc.point.x) / 2

            start = Point(x, BOTTOM)

            halfEdge = HalfEdge(start)
            self.diagram.append(halfEdge)
            arc.secondHalfEdge = arc.next.firstHalfEdge = halfEdge

    def handleCircleEvent(self, event):
        if event.valid:
            halfEdge = HalfEdge(event.point)
            self.diagram.append(halfEdge)
            arc = event.arc

            if arc.prev is not None:
                arc.prev.next = arc.next
                arc.secondHalfEdge = halfEdge
            if arc.next is not None:
                arc.next.prev = arc.prev
                arc.firstHalfEdge = halfEdge

            if arc.firstHalfEdge is not None:
                arc.firstHalfEdge.finish(event.point)

            if arc.secondHalfEdge is not None:
                arc.secondHalfEdge.finish(event.point)

            if arc.prev is not None:
                self.checkCircleEvent(arc.prev, event.y)

            if arc.next is not None:
                self.checkCircleEvent(arc.next, event.y)

    def findCircleCenter(self, a, b, c):
        x1, y1 = a.x, a.y
        x2, y2 = b.x, b.y
        x3, y3 = c.x, c.y

        if ((b.x - a.x) * (c.y - a.y) - (c.x - a.x) * (b.y - a.y)) > 0: return None, None

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
        yMax = ys - ((x1 - xs) ** 2 + (y1 - ys) ** 2) ** 0.5

        return yMax, Point(xs, ys)

    def finishHalfEdges(self):
        arc = self.beachLine
        while arc.next is not None:
            if arc.secondHalfEdge is not None:
                end = self.findIntersection(BOTTOM, arc.point, arc.next.point)
                arc.secondHalfEdge.finish(end)

            arc = arc.next

    def printOutput(self):
        for d in self.diagram:
            p0 = d.start
            p1 = d.end
            if p1 is None:
                print(p0.x, p0.y)
            else:
                print(p0.x, p0.y, p1.x, p1.y)

    def Fortune(self, points):
        for point in points:
            self.events.push(Point(point[0], point[1]))

        while not self.events.empty():
            event = self.events.pop()
            if isinstance(event, Point):
                self.handlePointEvent(event)
            else:
                self.handleCircleEvent(event)

        self.finishHalfEdges()
        self.printOutput()


a = Fortune()

a.Fortune([(4, 0), (0, 0), (0, 5)])
print(a.findIntersection(0, Point(1, 1), Point(2, 2)).x)
