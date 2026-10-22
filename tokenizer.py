class Node:
    def __init__(self, pair):
        # Store as list so elements can be updated in-place (e.g. pair[0] or pair[1])
        self.pair: list = list(pair) if pair is not None else None
        self.prev: 'Node' = None
        self.next: 'Node' = None
        self.let: bool = False


class Data:
    def __init__(self, data: list):
        self.data = self.parse(data)
        self.histogram: dict = self.data[0]
        self.node_links: dict = self.data[1]

    def parse(self, data: list):
        histogram = {}
        node_links = {}
        prev = None

        # Building a doubly linked list of parsed pairs.
        for i in range(len(data) - 1):
            pair = (data[i], data[i + 1])
            histogram[pair] = histogram.get(pair, 0) + 1
            node = Node(pair)
            node.prev = prev
            if prev is not None:
                prev.next = node
            node_links.setdefault(pair, []).append(node)
            prev = node

        return [histogram, node_links]

    def merge(self, pair: tuple, token: str):
        # Copy the list as self.node_links will be modified during merging
        locants: list[Node] = list(self.node_links.get(pair, []))
        if not locants:
            return token, pair

        # Helper Function, updates the node immediately before the merge region
        def mergeLeft(token: str, right: Node, node: Node):
            old_p = tuple(node.pair)
            self.histogram[old_p] -= 1
            if self.histogram[old_p] == 0:
                del self.histogram[old_p]
            if old_p in self.node_links and node in self.node_links[old_p]:
                self.node_links[old_p].remove(node)

            node.pair[1] = token
            node.next = right
            if right is not None:
                right.prev = node

            new_p = tuple(node.pair)
            self.histogram[new_p] = self.histogram.get(new_p, 0) + 1
            self.node_links.setdefault(new_p, []).append(node)
            return new_p

        # Helper Function, updates the node immediately after the merge region
        def mergeRight(token: str, left: Node, node: Node):
            old_p = tuple(node.pair)
            self.histogram[old_p] -= 1
            if self.histogram[old_p] == 0:
                del self.histogram[old_p]
            if old_p in self.node_links and node in self.node_links[old_p]:
                self.node_links[old_p].remove(node)

            node.pair[0] = token
            node.prev = left
            if left is not None:
                left.next = node

            new_p = tuple(node.pair)
            self.histogram[new_p] = self.histogram.get(new_p, 0) + 1
            self.node_links.setdefault(new_p, []).append(node)
            return new_p

        # 1. Handling Overlapping occurrences, merging them into contiguous runs of adjacent nodes
        runs = []
        current_run = []
        for locant in locants:
            if not current_run:
                current_run.append(locant)
            elif locant.prev is current_run[-1]:
                current_run.append(locant)
            else:
                runs.append(current_run)
                current_run = [locant]
        if current_run:
            runs.append(current_run)

        # 2. Merge each run
        output_candidate = pair
        for run in runs:
            left = run[0]
            right = run[-1]
            node_before = left.prev
            node_after = right.next

            # If overlapping identical pairs: k pairs of (c, c) represent k + 1 identical tokens
            # e.g., 3 pairs of ('G', 'G') in 'A G G G G M' collapse 4 'G's -> ('G', 'G', 'G', 'G')
            if pair[0] == pair[1]:
                output_candidate = tuple([pair[0]] * (len(run) + 1))
            else:
                output_candidate = tuple(pair)

            # Update neighboring pairs and rewire pointers around the entire run
            if node_before is not None:
                mergeLeft(token, node_after, node_before)
            if node_after is not None:
                mergeRight(token, node_before, node_after)

        # 3. Purge the merged candidate pair from histogram and node_links
        if pair in self.histogram:
            del self.histogram[pair]
        if pair in self.node_links:
            del self.node_links[pair]

        return token, output_candidate


class Tokenizer:
    def __init__(self, data, iters):
        self.data = Data(data)
        self.P2T = {}
        self.T2P = {}
        for i in range(iters):
            if not self.data.histogram:
                break
            candidate = max(self.data.histogram, key=self.data.histogram.get)
            token = f"<{i + 1}>"
            token, candidate = self.data.merge(candidate, token)
            self.T2P[token] = candidate
            self.P2T[candidate] = token