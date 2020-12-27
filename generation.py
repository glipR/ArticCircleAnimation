import math, random

class AztecGenerator:

    seed = None
    STRING_SIZE = 6
    current_id = 0

    def generate(self, seed=None, n=10):
        self.obj = {
            "general_info": {},
            "generation_data": [],
            "final_result": {},
        }
        if seed is None:
            seed = self._generate_seed_string()
        self.seed = seed
        random.seed(seed)
        self.obj["general_info"]["seed"] = seed
        self.obj["size"] = n
        # Generate.
        self.area = []
        for x in range(n):
            self.obj["generation_data"].append({
                "iteration": x,
                "created_blocks": [],
                "destroyed_blocks": [],
                "moved_blocks": [],
            })
            (
                self.obj["generation_data"][-1]["destroyed_blocks"], 
                self.obj["generation_data"][-1]["moved_blocks"], 
                self.obj["generation_data"][-1]["created_blocks"]
            ) = self.step_generate()

    def step_generate(self):
        removed = []
        moved = []
        created = []
        # Increase the area by one.
        self.area = [[]] + self.area + [[]]
        for x in range(1, len(self.area)-1):
            self.area[x] = [None] + self.area[x] + [None]
        self.area[0] = [None] * len(self.area)
        self.area[-1] = [None] * len(self.area)
        # Expand the visible region
        for a in range(len(self.area)):
            for b in range(len(self.area[0])):
                manhattan = math.ceil(abs(a + 0.5 - len(self.area) // 2)) + math.ceil(abs(b + 0.5 - len(self.area[0]) // 2)) - 1
                if manhattan <= len(self.area) // 2 and self.area[a][b] is None:
                    self.area[a][b] = "EMPTY"
        # Remove any existing opposite arrows
        for a in range(len(self.area)):
            for b in range(len(self.area[0])):
                if self.area[a][b] not in [None, "EMPTY"]:
                    dx, dy = self.area[a][b]["direction"]
                    if self.area[a+dx][b+dy] not in [None, "EMPTY"]:
                        cx, cy = self.area[a+dx][b+dy]["direction"]
                        if cx == -dx and cy == -dy:
                            # They point inwards. Remove.
                            removed.append([
                                self.area[a][b]["id"],
                                self.area[a+dx][b+dy]["id"],
                            ])
                            ca, cb = self.area[a][b]["neighbour"]
                            da, db = self.area[a+dx][b+dy]["neighbour"]
                            self.area[a][b] = "EMPTY"
                            self.area[a+dx][b+dy] = "EMPTY"
                            self.area[a+ca][b+cb] = "EMPTY"
                            self.area[a+dx+da][b+dy+db] = "EMPTY"
        # Move the remaining arrows
        for a in range(len(self.area)):
            for b in range(len(self.area[0])):
                if self.area[a][b] not in [None, "EMPTY"]:
                    # Just reset the moved variable for the next loop.
                    self.area[a][b]["moved"] = False
        new_area = [[None if v is None else "EMPTY" for v in row] for row in self.area]
        for a in range(len(self.area)):
            for b in range(len(self.area[0])):
                if self.area[a][b] not in [None, "EMPTY"] and not self.area[a][b]["moved"]:
                    dx, dy = self.area[a][b]["direction"]
                    na, nb = self.area[a][b]["neighbour"]
                    new_area[a+dx][b+dy] = self.area[a][b]
                    new_area[a+na+dx][b+nb+dy] = self.area[a+na][b+nb]
                    self.area[a][b]["moved"] = True
                    self.area[a+na][b+nb]["moved"] = True
                    moved.append([self.area[a][b]["id"], self.area[a][b]["direction"]])
        self.area = new_area
        # Generate new arrows
        for a in range(len(self.area) - 1):
            for b in range(len(self.area[0]) - 1):
                if (
                    self.area[a][b] == "EMPTY" and 
                    self.area[a+1][b] == "EMPTY" and
                    self.area[a][b+1] == "EMPTY" and
                    self.area[a+1][b+1] == "EMPTY"
                ):
                    # Generate a square
                    if random.random() > 0.5:
                        # Up/Down. Remember x is down, y is right.
                        self.area[a][b] = {
                            "direction": [-1, 0],
                            "neighbour": [0, 1],
                            "id": self.current_id,
                        }
                        self.area[a][b+1] = {
                            "direction": [-1, 0],
                            "neighbour": [0, -1],
                            "id": self.current_id,
                        }
                        self.current_id += 1
                        self.area[a+1][b] = {
                            "direction": [1, 0],
                            "neighbour": [0, 1],
                            "id": self.current_id,
                        }
                        self.area[a+1][b+1] = {
                            "direction": [1, 0],
                            "neighbour": [0, -1],
                            "id": self.current_id,
                        }
                        self.current_id += 1
                        created.append([
                            [self.current_id - 2, [[a - len(self.area)//2, b - len(self.area)//2], [a - len(self.area)//2, b - len(self.area)//2+1]], (-1, 0)],
                            [self.current_id - 1, [[a - len(self.area)//2+1, b - len(self.area)//2], [a - len(self.area)//2+1, b - len(self.area)//2+1]], (1, 0)],
                        ])
                    else:
                        # Left/Right. Remember x is down, y is right.
                        self.area[a][b] = {
                            "direction": [0, -1],
                            "neighbour": [1, 0],
                            "id": self.current_id,
                        }
                        self.area[a+1][b] = {
                            "direction": [0, -1],
                            "neighbour": [0, -1],
                            "id": self.current_id,
                        }
                        self.current_id += 1
                        self.area[a][b+1] = {
                            "direction": [0, 1],
                            "neighbour": [1, 0],
                            "id": self.current_id,
                        }
                        self.area[a+1][b+1] = {
                            "direction": [0, 1],
                            "neighbour": [0, -1],
                            "id": self.current_id,
                        }
                        self.current_id += 1
                        created.append([
                            [self.current_id - 2, [[a - len(self.area)//2, b - len(self.area)//2], [a - len(self.area)//2+1, b - len(self.area)//2]], (0, -1)],
                            [self.current_id - 1, [[a - len(self.area)//2, b - len(self.area)//2+1], [a - len(self.area)//2+1, b - len(self.area)//2+1]], (0, 1)],
                        ])
        return removed, moved, created

    def _generate_seed_string(self):
        import time
        random.seed(time.time())
        # Generate an string so that you can share the seed rather easily.
        digits = list(map(str, range(10))) + list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        v = random.randint(0, pow(len(digits), self.STRING_SIZE))
        if v == 0:
            return digits[0]
        result = []
        while v:
            result.append(digits[v % len(digits)])
            v = v // len(digits)
        while len(result) < self.STRING_SIZE:
            result = result + [digits[0]]
        return ''.join(result[::-1])

        