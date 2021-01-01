import heapq


class PriorityQueue:
    def __init__(self):
        self.queue = []
        self.entry_finder = {}
        self.counter = 0

    def push(self, item):
        if item in self.entry_finder: return
        entry = [item.y, item.x, item]
        self.entry_finder[item] = entry
        heapq.heappush(self.queue, entry)

    def pop(self):
        if not self.queue:
            raise KeyError('pop from an empty priority queue')
        y, x, item = heapq.heappop(self.queue)
        del self.entry_finder[item]
        return item

    def top(self):
        if not self.queue:
            raise KeyError('top from an empty priority queue')
        y, x, item = heapq.heappop(self.queue)
        del self.entry_finder[item]
        self.push(item)
        return item


    def empty(self):
        return not self.queue

