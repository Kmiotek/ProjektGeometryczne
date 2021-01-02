class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y



class Circle:

    def __init__(self, x, p, a):
        self.x = x
        self.point = p
        self.arc = a
        self.valid = True


class Arc:

    def __init__(self, p, a=None, b=None):
        self.point = p
        self.prev = a
        self.next = b
        self.circle_event = None
        self.upper_edge = None
        self.lower_edge = None


class Edge:

    def __init__(self, p):
        self.start = p
        self.end = None
        self.done = False

    def finish(self, p):
        if self.done:
            return
        self.end = p
        self.done = True
