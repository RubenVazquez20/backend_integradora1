from mesa import Agent, Model
from mesa.space import MultiGrid as Grid
from mesa.time import RandomActivation
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
import random

# Time
from mesa.time import RandomActivation 

#Pathfinder
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid as pGrid
from pathfinding.finder.a_star import AStarFinder

# Charts
from mesa.visualization.modules import ChartModule

# Datacollector
from mesa.datacollection import DataCollector

# Slider
from mesa.visualization.UserParam import UserSettableParameter

Nrow = 22
Ncol = 22
X = [[0 for _ in range(Ncol)] for _ in range(Nrow)]


class BoxStack(Agent):
    def __init__(self, model):
        super().__init__(model.next_id(), model)

class Box(Agent):
    def __init__(self, model):
        super().__init__(model.next_id(), model)

class Deposito(Agent):
    def __init__(self, model, pos, counter):
        super().__init__(model.next_id(), model)
        self.pos = pos
        self.counter = counter
        
class Muros(Agent):
    def __init__(self, model, pos):
        super().__init__(model.next_id(), model)
        self.pos = pos
        
class Chiquito(Agent):
    def __init__(self, model, pos, posCajas, matriz, posDeposit = (1,Ncol-2)):
        super().__init__(model.next_id(), model)
        self.posCajas = posCajas
        self.cargando = False
        self.pos = pos
        self.posDeposit = posDeposit
        self.matriz = matriz
        #caja destino
        self.des = self.posCajas[random.randint(0, len(self.posCajas)-1)] #tupla x y

    def step(self):

        # Llegar a destino 
        if self.pos == self.des:
            
            for agent in self.model.grid.iter_cell_list_contents([self.pos]):
                # Destino == Caja
                if isinstance(agent, Box) and not self.cargando:
                    self.des = self.posDeposit # Cambiar destino a un deposito
                    self.cargando = True
                    pos = agent.pos
                    x, y = pos
                    self.model.grid[x][y].remove(agent)
                    self.model.schedule.remove(agent)
            
                # Destino == Deposit
                if self.cargando and isinstance(agent, Deposito) and not self.validar():
                    self.cambiar_deposit() # Cambiar deposito al que llega
                
                # Destino == None y tambien funciona cuando el depósto fue válido
                if not isinstance(agent,Box) and not isinstance(agent, Deposito) and not self.cargando:
                    self.des = self.posCajas[random.randint(0, len(self.posCajas)-1)] #tupla x y

        #else para llegar a la caja   
        else:
            m = pGrid(matrix=self.matriz)
            start = m.node(self.pos[0], self.pos[1])
            end = m.node(self.des[0], self.des[1])

            finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
            path= finder.find_path(start, end, m)
            mov_next = path[0][1]
            self.model.grid.move_agent(self, mov_next)
        
        
    
    def validar(self):
        for agent in self.model.grid.iter_cell_list_contents([self.pos]):
            if isinstance(agent,Deposito) and agent.counter < 5: 
                stack = BoxStack(self.model)
                self.model.grid.place_agent(stack, self.posDeposit) 
                self.model.schedule.add(stack)
                self.cargando = False
                self.model.units += 1 #contador universal de cajas acomodadas
                agent.counter += 1
                return True
        return False
 
    def cambiar_deposit(self):
        self.des = (self.des[0]+1, self.des[1])
        self.posDeposit = (self.posDeposit[0] + 1, self.posDeposit[1])

class Maze(Model):
    def __init__(self, rows = Nrow, columns = Ncol, time=0):  
        super().__init__() 
        self.posCajas = [] 
        self.steps = 0 
        self.schedule = RandomActivation(self) 
        self.time = time 
        self.rows = rows 
        self.units = 0
        self.columns = columns 
        self.grid = Grid(width = rows, height = columns, torus=False) 
        matrix =  [[0 for _ in range(self.columns)] for _ in range(self.rows)] 
        
        # BOX
        for _,x,y in self.grid.coord_iter(): 
            if self.random.random() < .1 and y < columns-2 and x > 0 and x < columns - 1 and y > 0: 
                box = Box(self) 
                self.grid.place_agent(box, (x,y)) 
                self.schedule.add(box) 
                self.posCajas.append((x, y)) 
        
        #DEPOSIT
        for i in range(self.columns - 2):
            y = self.rows - 2
            x = i + 1
            pos = (x,y)
            deposito = Deposito(self, pos, 0)
            self.grid.place_agent(deposito, pos)
            self.schedule.add(deposito)
            
        #MUROS
        for i in range(self.columns):
            y = self.rows - 1
            x = i 
            pos = (x,y)
            muros = Muros(self, pos)
            self.grid.place_agent(muros, pos)
            self.schedule.add(muros)
            
        for i in range(self.columns):
            y = 0
            x = i 
            pos = (x,y)
            muros = Muros(self, pos)
            self.grid.place_agent(muros, pos)
            self.schedule.add(muros)
            
        for i in range(self.columns - 2):
            y = i + 1
            x = 0
            pos = (x,y)
            muros = Muros(self, pos)
            self.grid.place_agent(muros, pos)
            self.schedule.add(muros)
        
        for i in range(self.columns - 2):
            y = i + 1
            x = self.rows - 1
            pos = (x,y)
            muros = Muros(self, pos)
            self.grid.place_agent(muros, pos)
            self.schedule.add(muros) 
            
        #ROBOTS
        for i in range(5):
            x = random.randint(1, self.rows - 2)
            y = random.randint(1, self.columns - 3)
            agent = self.grid[x][y]
            pos = (x, y)
            while agent and pos in self.posCajas and (not isinstance( agent, Chiquito)):
                x = random.randint(1, self.rows - 2)
                y = random.randint(1, self.columns - 3)
                agent = self.grid[x][y]
                pos = (x, y)

            chiquito = Chiquito(self, (x, y), self.posCajas, X)
            self.grid.place_agent(chiquito, (x, y))
            self.schedule.add(chiquito)
        
        #Filling matrix
        for _,x,y in self.grid.coord_iter():
            agent = self.grid[x][y]
            if(agent and not isinstance(agent, Chiquito)):
                matrix[x][y] = 100
            else:
                matrix[x][y] = 1

        #Trasponer matrix
        for i in range( self.rows):
            for j in range(len(X[0])):
                X[j][i] = matrix[i][j]
        #Matriz traspuesta
        X.reverse()    

        # Datacollectors
        self.time_datacollector=DataCollector({"Tiempo":lambda x:self.steps}) 
        self.step_datacollector=DataCollector({"Pasos":lambda x:self.steps * 5}) 
  
    def step(self):
        self.schedule.step()
        self.steps += 1
        self.time_datacollector.collect(self) 
        self.step_datacollector.collect(self) 
        if self.steps == self.time or (self.units == len(self.posCajas)): 
            self.running = False
        # return self.posCajas

    def getCajas(self):
        cajas = []
        for n in self.schedule.agents:
            if isinstance(n, Box):
                cajas.append({"id": n.unique_id, "pos": [n.pos[0], n.pos[1]]})
        return cajas
    def getChiquitos(self):
        chiquitos = []
        for n in self.schedule.agents:
            if isinstance(n, Chiquito):
                chiquitos.append({"id": n.unique_id, "pos": [n.pos[0], n.pos[1]]}) 
        return chiquitos 
    def getMuros(self):
        muros = [] #ojo es minuscula
        for n in self.schedule.agents:
            if isinstance(n, Muros):
                muros.append({"id": n.unique_id, "pos": [n.pos[0], n.pos[1]]}) 
        return muros
    def getDepositos(self):
        depositos = []
        for n in self.schedule.agents:
            if isinstance(n, Deposito):
                depositos.append({"id": n.unique_id, "pos": [n.pos[0], n.pos[1]], "counter":n.counter}) 
        return depositos
    def getStack(self):
        stack = []
        for n in self.schedule.agents:
            if isinstance(n, BoxStack):
                stack.append({"id": n.unique_id, "pos": [n.pos[0], n.pos[1]]}) 
        return stack



#Rendering function
def agent_portrayal(agent):
    if isinstance(agent, BoxStack):
        return {"Shape": "rect", "Filled": "true", "Color": "Brown", "w": 0.3, "h": 0.3, "Layer": 0}
    if isinstance(agent, Box):
        return {"Shape": "rect", "Filled": "true", "Color": "Brown", "w": 0.5, "h": 0.5, "Layer": 0}
    if isinstance(agent, Chiquito) and not agent.cargando:
        return {"Shape": "circle", "Filled": "true", "Color": "Blue", "r": 0.75, "Layer": 0}
    if isinstance(agent, Chiquito) and agent.cargando:
        return {"Shape": "circle", "Filled": "true", "Color": "Green", "r": 0.75, "Layer": 0}
    if isinstance(agent, Deposito):
        return {"Shape": "circle", "Filled": "true", "Color": "Black", "r": 0.75, "Layer": 0}
    if isinstance(agent, Muros):
        return {"Shape": "rect", "Filled": "true", "Color": "Gray", "w": 1, "h": 1, "Layer": 0}

# Charts
chart = ChartModule([{"Label": "Tiempo", "Color": "Black"}], data_collector_name='time_datacollector')
numsteps = ChartModule([{"Label": "Pasos", "Color": "Black"}], data_collector_name='step_datacollector')

grid = CanvasGrid(agent_portrayal, Nrow, Ncol, 450, 450)

server = ModularServer(Maze, 
[grid], "Robotron", {}) 
server = ModularServer(Maze, 
                       [grid, chart, numsteps],
                       "Room", 
                       {"time": UserSettableParameter("slider","Time",200,1,400,1)}) 

# server.port = 3420
# server.launch()