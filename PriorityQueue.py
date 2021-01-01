import heapq


class PriorityQueue:
    def __init__(self):
        self.queue = []
        self.counter = 0

    def push(self, item):
        entry = [item.y, item.x, item]
        heapq.heappush(self.queue, entry)

    def pop(self):
        while self.queue:
            y, x, item = heapq.heappop(self.queue)
            return item
        raise KeyError('pop from an empty priority queue')

    def top(self):
        while self.queue:
            y, x, item = heapq.heappop(self.queue)
            self.push(item)
            return item
        raise KeyError('top from an empty priority queue')

    def empty(self):
        return not self.queue

