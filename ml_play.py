import queue

class MLPlay:
    def __init__(self, player):
        self.player = player
        if self.player == "player1":
            self.player_no = 0
        elif self.player == "player2":
            self.player_no = 1
        elif self.player == "player3":
            self.player_no = 2
        elif self.player == "player4":
            self.player_no = 3
        self.car_pos = (0,0)                                       # pos initial
        self.lanes = [35, 105, 175, 245, 315, 385, 455, 525, 595]  # lanes center
        self.last_command = []
        pass

    def update(self, scene_info):
        if scene_info["status"] != "ALIVE":
            return "RESET"

        grid = [[0 for i in range(5)] for j in range(5)]

        self.car_pos = scene_info[self.player]
        if len(self.car_pos) != 2:
            return 'SPEED'

        if (self.car_pos[0] - 35) % 70 != 0:
            return self.last_command

        for car in scene_info['cars_info']:
            if car['id'] == self.player_no:
                continue

            x = car['pos'][0] - self.car_pos[0]
            y = car['pos'][1] - self.car_pos[1]
            cmp = lambda a: 1 if a >= 0 else -1

            offset = [abs(x) // 70, abs(y) // 120]
            remain = [abs(x) %  70, abs(y) %  120]
            for i in range(2):
                if remain[i] < 10:
                    remain[i] = 0

            if max(offset[0], offset[1]) > 2:
                continue

            x_idx = 2 + cmp(x) * offset[0]
            y_idx = 2 + cmp(y) * offset[1]
            grid[y_idx][x_idx] = None

            if remain[0] and 0 <= x_idx + cmp(x) < 5:
                grid[y_idx][x_idx + cmp(x)] = None
            if remain[1] and 0 <= y_idx + cmp(y) < 5:
                grid[y_idx + cmp(y)][x_idx] = None

        for i in range(1, 3):
            if self.car_pos[0] - i * 70 < self.lanes[0]:
                for j in range(len(grid)):
                    grid[j][2 - i] = None

            if self.car_pos[0] + i * 70 > self.lanes[-1]:
                for j in range(len(grid)):
                    grid[j][2 + i] = None

        goal = None
        q = queue.Queue()
        q.put([2, 2])
        need_brake = True if grid[2][2] == None else False
        grid[2][2] = [0, 0]
        while not q.empty():
            t = q.get()
            direction = [[-1, 0], [1, 0], [0, -1], [0, 1]]

            goal = t
            if t[0] == 0:
                break

            for d in direction:
                p = [t[0] + d[0], t[1] + d[1]]
                if 0 <= p[0] < len(grid[0]) and 0 <= p[1] < len(grid) and grid[p[0]][p[1]] == 0:
                    grid[p[0]][p[1]] = [-d[0], -d[1]]
                    q.put(p)

        if need_brake:
            self.last_command = ['BRAKE']
            return self.last_command

        command = ['SPEED']
        if grid[1][2] == None:
            command.remove('SPEED')


        last_move = [0, 0]
        while goal != [2, 2]:
            last_move = grid[goal[0]][goal[1]]
            goal[0] += last_move[0]
            goal[1] += last_move[1]

        if last_move == [-1, 0]:
            command.append('BRAKE')
        elif last_move == [0, 1]:
            command.append('MOVE_LEFT')
        elif last_move == [0, -1]:
            command.append('MOVE_RIGHT')

        self.last_command = command
        return command

    def reset(self):
        """
        Reset the status
        """
        pass

