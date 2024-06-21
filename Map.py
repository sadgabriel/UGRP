import random as rd

class Map:
    def __init__(self, n = 10) -> None:
        self.matrix = []
        self.n = n
        self.tracer = {}

        self.clear()

        return

    # initialize & reset attributes.
    def clear(self):
        self.matrix = []
        n = self.n
        self.tracer = {}

        for i in range(n):
            self.matrix.append([])

        for i in range(n):
            for j in range(n):
                self.matrix[i].append(0)

        return
    
    # move id on x1,y1 to x2,y2.
    def move(self, x1, y1, x2, y2):
        id = self.matrix[x1][y1]
        self.matrix[x2][y2] = id
        self.matrix[x1][y1] = 0

        self.tracer[id] = (x2, y2)

        return
    
    # move id to (x, y)
    def move_id(self, id, x, y):
        point = self.tracer[id]
        self.move(point[0], point[1], x, y)
        return
    
    # create id on x,y.
    # Error if id is not unique (already exist in tracer.keys)
    def create(self, id, x, y):
        if id in self.tracer.keys():
            raise Exception("id is not unique")
        self.matrix[x][y] = id
        self.tracer[id] = (x, y)

        return
    
    # Just put id into self.tracer.
    # This method does not place id "on self.matrix"
    def put(self, id):
        self.tracer[id] = (-1, -1)

        return
    
    # reset id on x,y into 0.
    def remove(self, x, y):
        id = self.matrix[x][y]
        self.matrix[x][y] = 0
        self.tracer.pop(id)

        return
    
    # random placement.
    def random_place(self):
        n = self.n
        occupy = len(self.tracer) / (n*n)
        print("Occupy is ", occupy)

        for id in self.tracer.keys():
            x = rd.randrange(n)
            y = rd.randrange(n)
            while self.matrix[x][y] != 0:
                x = rd.randrange(n)
                y = rd.randrange(n)

            self.matrix[x][y] = id
            self.tracer[id] = (x, y)
            
        
        return
    
    # Return distance btw two points that is id1, id2.
    # This distance is not diagonal. It is the Taxy distance(x_dis + y_pos).
    # 대각선 거리(피타고라스)가 아니고 택시거리(=맨해튼거리)(x거리 y거리의 합)이다.
    def distance(self, id1, id2):
        temp_keys = self.tracer.keys()
        if (id1 not in temp_keys) or (id2 not in temp_keys):
            raise Exception("There are no such id")
        
        id1_pos = self.tracer[id1]
        id2_pos = self.tracer[id2]

        x_dis = id1_pos[0] - id2_pos[0]
        if x_dis < 0:
            x_dis = -x_dis
        
        y_dis = id1_pos[1] - id2_pos[1]
        if y_dis < 0:
            y_dis = -y_dis

        return x_dis + y_dis
    
    # Move id1 around id2.
    # id1을 id2에 인접한 4타일 중 하나로 이동시킨다.
    # id2에 인접한 네 타일이 모두 점유 중이라면 raise.
    def move_around(self, id1, id2):
        
        # Find the surrounding point of id2.
        id2_pos = self.tracer[id2]
        id2_x = id2_pos[0]
        id2_y = id2_pos[1]

        if (id2_x-1 > -1) and (self.matrix[id2_x-1][id2_y] == 0):
            # Here index error not occur because index is checked first.
            # If index is out of range, the back part: (self.matrix[id2_x-1] == 0) is not operated.
            # 여기서는 인덱스를 먼저 확인하기 때문에 인덱스 오류가 발생하지 않습니다.
            # 인덱스가 범위를 벗어날 경우 뒷부분: (self.matrix[id2_x-1] == 0)이 실행되지 않습니다.
            destination = (id2_x-1, id2_y)

        elif (id2_x+1 < self.n) and (self.matrix[id2_x+1][id2_y] == 0):
            destination = (id2_x+1, id2_y)

        elif (id2_y-1 > -1) and (self.matrix[id2_x][id2_y-1] == 0):
            destination = (id2_x, id2_y-1)
        
        elif (id2_y+1 < self.n) and (self.matrix[id2_x][id2_y+1] == 0):
            destination = (id2_x, id2_y+1)
        
        else:
            raise Exception("There is no surrounding point of id2.")
        
        # Move id1 to 'destination'.
        id1_pos = self.tracer[id1]
        self.move(id1_pos[0], id1_pos[1], destination[0], destination[1])

        return
    
    # print map
    def print_map(self):
        print()
        for i in range(self.n):

            for j in range(self.n):
                if self.matrix[i][j] != 0:
                    print('\033[31m' + f'{str(self.matrix[i][j]):<3}' + '\033[0m', end='')
                else:
                    print(self.matrix[i][j], end='')
                    print(end="  ")

            print()
        
        return
    
    # A attackablility check that consider a range not only a movepoint.
    # check whether is id1 able to attack id2.
    def is_movable_with_range(self, id1, id2, movement_point, range):
        """
        A attackablility check that consider a range not only a movepoint.
        check whether is id1 able to attack id2.

        Args:
            id1: subject or caster (attacker/mover)
            id2: object
            movement_point: movement point of id1
            range: range of attack

        Returns:
            bool
        """
        return self.distance(id1, id2) < (movement_point + range)

    # 어택땅
    def move_attack(self, id1, id2, movement_point, shooting_range):

        # 이미 최대 사거리에 있는 경우
        if shooting_range == self.distance(id1, id2):
            return # Do not move.
        
        # 사거리+이동이 닿는 경우
        if self.is_movable_with_range(id1, id2, movement_point, shooting_range):
            # move at least.
            d = shooting_range

        # 사거리+이동이 안 닿는 경우
        else:
            # move at most
            d = self.distance(id1, id2) - movement_point

        far_from_d = []
        x = self.tracer[id2][0]
        y = self.tracer[id2][1]

        # id2에서 거리 d떨어진 모든 점 찾기.
        for i in range(d):
            far_from_d.append((x+i, y-i+d))
            far_from_d.append((x-i+d, y-i))
            far_from_d.append((x-i, y+i-d))
            far_from_d.append((x+i-d, y+i))
        
        # 유효한지 검사
        n = self.n
        disabled_indices = []
        for index in range(len(far_from_d)):
            x = far_from_d[index][0]
            y = far_from_d[index][1]

            # 유효하지 않은 점 제거
            if (x>=n) or (x<0) or (y>=n) or (y<0) or (self.matrix[x][y] != 0):
                disabled_indices.append(index)
        
        for dis_index in reversed(disabled_indices):
            far_from_d.pop(dis_index)

        # d 떨어진 아무 점 중 id1과 가장 가까운 점 선택
        nearest_distane = 19

        for current_point in far_from_d:
            # calculate current_distance
            id1_x = self.tracer[id1][0]
            id1_y = self.tracer[id1][1]
            current_distance = abs(current_point[0] - id1_x) + abs(current_point[1] - id1_y)

            if current_distance < nearest_distane:
                nearest_point = current_point
                nearest_distane = current_distance

        # move id1
        self.move_id(id1, nearest_point[0], nearest_point[1])

        return
    
    # (x, y) 튜플 입력이 유효한지 검사
    def check_available_point(self, point):
        x = point[0]
        y = point[1]

        if (x > -1) and (x < self.n):
            if (y > -1) and (y < self.n):
                return True
            
        return False
    
    # 유효한 인접 점을 출력, 없으면 False.
    # 그래프 부터 새로 만들기.
    def visit_neighbor(self, point, visited):
        x = point[0]
        y = point[1]

        if self.check_available_point((x+1, y)) and ((x+1,y) not in visited):
            return (x+1, y)
        
        elif self.check_available_point((x-1, y)) and ((x-1,y) not in visited):
            return (x-1, y)
        
        elif self.check_available_point((x, y+1)) and ((x,y+1) not in visited):
            return (x, y+1)
        
        elif self.check_available_point((x, y-1)) and ((x,y-1) not in visited):
            return (x, y-1)
        
        else:     
            return False


if __name__ == '__main__':
    map = Map()

    map.put('A')
    map.put('B')
    map.put(3)

    print(map.matrix)
    print(map.n)
    print(map.tracer)

    print(map.tracer['A'])
    map.random_place()
    print(map.tracer['A'])
    print(map.tracer)

    map.print_map()

    map.move_attack('A', 'B', 1, 2)
    map.print_map()
    map.move_attack('A', 'B', 1, 2)
    map.print_map()
    map.move_attack('A', 'B', 1, 2)
    map.print_map()