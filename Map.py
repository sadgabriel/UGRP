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
    
    # create id on x,y.
    # Error if id is not unique (already exist in tracer.keys)
    def create(self, id, x, y):
        if id in self.tracer.keys():
            raise "id is not unique"
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
    
    # Return distance btw two points.
    # This distance is not diagonal. It is x_dis + y_pos.
    # 대각선 거리(피타고라스)가 아니고 직각거리(x거리 y거리의 합)이다.
    def distance(self, a, b):
        temp_keys = self.tracer.keys()
        if (a not in temp_keys) or (b not in temp_keys):
            raise "There are no such id"
        
        a_pos = self.tracer[a]
        b_pos = self.tracer[b]

        x_dis = a_pos[0] - b_pos[0]
        if x_dis < 0:
            x_dis = -x_dis
        
        y_dis = a_pos[1] - b_pos[1]
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
            raise "There is no surrounding point of id2."
        
        # Move id1 to 'destination'.
        id1_pos = self.tracer[id1]
        self.move(id1_pos[0], id1_pos[1], destination[0], destination[1])

        return
    
    # print map
    def print_map(self):
        for i in range(self.n):

            for j in range(self.n):
                if self.matrix[i][j] != 0:
                    print('\033[31m' + str(self.matrix[i][j]) + '\033[0m', end='')
                else:
                    print(self.matrix[i][j], end='')
                print(end="  ")

            print()
        
        return


if __name__ == '__main__':
    a = Map()

    a.put('A')
    a.put('B')
    a.put(3)

    print(a.matrix)
    print(a.n)
    print(a.tracer)

    print(a.tracer['A'])
    a.random_place()
    print(a.tracer['A'])
    print(a.tracer)

    a.print_map()