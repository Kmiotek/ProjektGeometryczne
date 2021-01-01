import heapq


class PriorityQueue:
    def __init__(self):
        self.queue = []
        self.counter = 0

    def push(self, item):
        entry = [item.y, item.x, item]
        heapq.heappush(self.queue, entry)

    def pop(self):
        if not self.queue:
            raise KeyError('pop from an empty priority queue')
        y, x, item = heapq.heappop(self.queue)
        return item

    def top(self):
        if not self.queue:
            raise KeyError('top from an empty priority queue')
        y, x, item = heapq.heappop(self.queue)
        self.push(item)
        return item


    def empty(self):
        return not self.queue

