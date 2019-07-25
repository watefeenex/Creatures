import turtle
import hashlib

"""This class represents a creature"""
class Creature:

    # A creature stores its position and direction and its "DNA" - the list of instructions it follows
    def __init__(self, row, col, dna, direction):
        self.direction = direction
        self.row = row
        self.col = col
        self.dna = dna
        self.next_instruction = 1

    ## A creature draws itself using the colour specified as part of its dna
    ## the size of the grid squares, and the position of the top-left pixel are provided as input
    def draw(self, grid_size, top_left_x, top_left_y):

        # Compute the position of the top left hand corner of the cell this creature is in
        x = top_left_x + (self.col-1)*grid_size
        y = top_left_y - (self.row-1)*grid_size
        turtle.color(self.dna[0].split(":")[1])

        # Initialise variables for drawing coords
        startingPos = (None, None) # First point, drawing starts here. 1st point
        tipPos = (None, None) # Position of the tip of the triangle. 2nd point
        endPos = (None, None) # 3rd point. Mirrored of starting position. 3rd point

        # Set coords to draw triangle in correct orentation
        if self.direction == 'North':
            startingPos = (x, y - grid_size)
            tipPos = (x + grid_size / 2, y)
            endPos = (x + grid_size, y - grid_size)
        elif self.direction == 'South':
            startingPos = (x, y)
            tipPos = (x + grid_size / 2, y - grid_size)
            endPos = (x + grid_size, y)
        elif self.direction == 'East':
            startingPos = (x, y)
            tipPos = (x + grid_size, y - grid_size / 2)
            endPos = (x, y - grid_size)
        elif self.direction == 'West':
            startingPos = (x + grid_size, y)
            tipPos = (x, y - grid_size / 2)
            endPos = (x + grid_size, y - grid_size)

        # Draw the creature as a triangle
        turtle.goto(startingPos)
        turtle.pendown()
        turtle.begin_fill()
        turtle.goto(tipPos)
        turtle.goto(endPos)
        turtle.goto(startingPos)
        turtle.end_fill()
        turtle.penup()
        turtle.color("black")

    # Returns the name of the species for this creature
    def get_species(self):
        return self.dna[0].split(":")[0]

    # Gets the current position of the creature
    def get_position(self):
        return (self.row, self.col)

    # Returns a string representation of the creature
    def __str__(self):
        return str(self.get_species() + ' ' + str(self.row) + ' ' + str(self.col) + ' ' + str(self.direction))

    # Execute a single move (either hop, reverse or twist) for this creature by following the instructions in its dna
    def make_move(self, world):
        finished = False
        # Find out what lies ahead
        ahead_row = self.row
        ahead_col = self.col
        if self.direction == 'North':
            ahead_row = ahead_row - 1 
        elif self.direction == 'South':
            ahead_row = ahead_row + 1 
        elif self.direction == 'East':
            ahead_col = ahead_col + 1 
        elif self.direction == 'West':
            ahead_col = ahead_col - 1 
        ahead_value = world.get_cell(ahead_row, ahead_col)
        world.update_info_grid() # Update the creatures in the information grid

        # Continue to execute the creature's instructions until a 
        # "hop", "reverse", "twist" or "infect" instruction is reached
        while not finished:
            next_op = self.dna[self.next_instruction]
            op = next_op.split()
            
            """
            IFSAME 
            Instruction set for "ifsame x"
            Detects if there is a creature of the same type in front of the creature,
            if so, jumps to instruction x
            """
            if op[0] == 'ifsame':
                if ahead_value == 'EMPTY':
                    if world.info_grid[ahead_row-1][ahead_col-1] != None:
                        if world.info_grid[ahead_row-1][ahead_col-1][0] == self.get_species(): # [0] item is species
                            self.next_instruction = int(op[1])
                            next_op = self.dna[self.next_instruction]
                            op = next_op.split()
                        else:
                            self.next_instruction = self.next_instruction + 1
                    else:
                        self.next_instruction = self.next_instruction + 1
                else:
                    self.next_instruction = self.next_instruction + 1
            """
            IFENEMY
            Instruction set for "ifenemy x"
            Detects if there is a creature of a different type in front of the creature,
            if so, jumps to instruction x
            """
            if op[0] == 'ifenemy':
                if ahead_value == 'EMPTY':
                    if world.info_grid[ahead_row-1][ahead_col-1] != None:
                        if world.info_grid[ahead_row-1][ahead_col-1][0] != self.get_species(): # [0] item is species
                            self.next_instruction = int(op[1])
                            next_op = self.dna[self.next_instruction]
                            op = next_op.split()
                        else:
                            self.next_instruction = self.next_instruction + 1
                    else:
                        self.next_instruction = self.next_instruction + 1
                else:
                    self.next_instruction = self.next_instruction + 1
            """
            IFRANDOM
            Instruction set for "ifrandom x"
            Calls the world pseudo_random function which returns either a 0 or a 1,
            if 1, jumps to instruction x
            """
            if op[0] == 'ifrandom':
                if world.pseudo_random() == 1:
                    self.next_instruction = int(op[1])
                    next_op = self.dna[self.next_instruction]
                    op = next_op.split()
                else:
                    self.next_instruction = self.next_instruction + 1
            """
            INFECT
            Instruction set for "infect"
            Detects if there is a creature of a different type in front of the creature,
            if so, copies it's dna to the creature in front of it. Sets its next_instruction back to 1
            """
            if op[0] == 'infect':
                if world.info_grid[ahead_row-1][ahead_col-1] != None:
                    if world.info_grid[ahead_row-1][ahead_col-1][0] != self.get_species(): # [0] item is species
                        world.info_grid[ahead_row-1][ahead_col-1][4].dna = self.dna
                        world.info_grid[ahead_row-1][ahead_col-1][4].next_instruction = 1
                        self.next_instruction = 1
                        finished = True
                    else:
                        self.next_instruction = self.next_instruction + 1
                        finished = True
                else:
                    self.next_instruction = self.next_instruction + 1
                    finished = True
            """
            GO
            Instruction set for "go"
            Starts
            """
            if op[0] == 'go':
                self.next_instruction = int(op[1])

            """
            HOP
            Instruction set for "hop"
            Move forward by 1
            """
            if op[0] == 'hop':
                if ahead_value == 'EMPTY':
                    if world.info_grid[ahead_row - 1][ahead_col - 1] == None:
                        self.row = ahead_row
                        self.col = ahead_col
                self.next_instruction = self.next_instruction + 1
                finished = True
            """
            REVERSE
            Instruction set for "reverse"
            Turns 180 degrees and ends the creatures turn
            """
            if op[0] == 'reverse':
                if self.direction == 'North':
                    self.direction = 'South'
                elif self.direction == 'East':
                    self.direction = 'West'
                elif self.direction == 'South':
                    self.direction = 'North'
                elif self.direction == 'West':
                    self.direction = 'East'

                self.next_instruction = self.next_instruction + 1
                finished = True
            """
            IFNOTWALL
            Instruction set for "ifnotwall"
            If there is not a wall in front of the creature, then jump to
            instruction X in the DNA, otherwise just continue from the next
            instruction and doesnt end the creatures turn
            """            
            if op[0] == 'ifnotwall':
                if ahead_value == 'WALL':
                    self.next_instruction = self.next_instruction + 1
                else:
                    self.next_instruction = int(op[1])
            """
            TWIST
            Instruction set for "twist"
            Turns 90 degrees clockwise and end creatures turn
            """
            if op[0] == 'twist':
                if self.direction == 'North':
                    self.direction = 'East'
                elif self.direction == 'East':
                    self.direction = 'South'
                elif self.direction == 'South':
                    self.direction = 'West'
                elif self.direction == 'West':
                    self.direction = 'North'

                self.next_instruction = self.next_instruction + 1
                finished = True


        world.update_info_grid() # Update the creatures in the information grid


""" This class represents the grid-based world"""
class World:

    ## The world stores its grid-size, and the number of generations to be executed.  It also stores the creatures
    ## as well as a 2D array, info_grid, which is represent the state of each square in the grid.
    def __init__(self, size, max_generations):
        self.size = size
        self.generation = 0
        self.max_generations = max_generations
        self.creatures = [] # Initialise blank list for creatures to be added to
        self.info_grid = self.initialise_info_grid() # Initialise a blank/None filled info grid
    """Initialises a size x size 2D array containing None for each value"""
    def initialise_info_grid(self):
        
        temp = [[None]*self.size for _ in range(self.size)]
        
        return temp
    
    """
    Updates the info grid by adding in all the creatures in the grid,
    replacing the value of None with a list descriping the creature.
    The list of features is in the format [species, row, column, direction, creature(itself)].
    The place the information is stored in the info_grid is at the creatures [row - 1], [col - 1]
    """
    def update_info_grid(self):
        
        self.info_grid = self.initialise_info_grid() # Reset the grid

        # Update all the creatures into the right place in the grid
        for c in self.creatures:
            if self.info_grid[c.row - 1][c.col - 1] == None:
                creatureFeatures = [c.get_species(), c.row, c.col, c.direction, c]
                self.info_grid[c.row - 1][c.col - 1] = creatureFeatures
        return
    
    """Nicely prints the info grid. Useful for debugging"""
    def print_info_grid(self):
        
        for i in range(0, self.size):
            for j in range(0, self.size):
                if j == self.size - 1:
                    print(self.info_grid[i][j], end='')
                else:
                    print(self.info_grid[i][j], end=' ')
            print("\n")

    """
    Calculates a pseudo random number. This is done by 
    For every creature in the world, compute the sum of that creature’s row and column positions
    Add all of these creature’s sums together to get a total sum
    Multiply this total sum by the current generation (see self.generation)
    string_total is simply this product converted to a string.
    This string_total is then passed into a hash funtion and converted to a base 10 number.
    The funtion then returns this number modulo 2. Returning either a 1 or 0.
    """
    def pseudo_random(self):
        string_total = 0
        for c in self.creatures:
            row, col = c.get_position()
            string_total += row + col
        string_total *= self.generation
        string_total = str(string_total)
        return int(hashlib.sha256(string_total.encode()).hexdigest(), 16) % 2

    """Adds a creature to the world"""
    def add_creature(self, c):
        self.creatures.append(c) # New creature is added onto list of creatures

    """
    Gets the contents of the specified cell.  This could be 'WALL' if the cell is off the grid
    or 'EMPTY' if the cell is unoccupied
    """
    def get_cell(self, row, col):
        if row <= 0 or col <= 0 or row >= self.size + 1 or col >= self.size + 1:
            return 'WALL'            
        return 'EMPTY'

    """
    Executes one generation for the world - the creature moves once.  If there are no more
    generations to simulate, the world is printed
    """
    def simulate(self):
        if self.generation < self.max_generations:
            for c in self.creatures:
                c.make_move(self)
            self.generation += 1
            return False
        else:
            print(self)
            return True

    """Returns a string representation of the world"""
    def __str__(self):
        returnString = ''
        # Each item in creatureList list will be a string in the format 
        # "{creatureType} {row} {col} {direction}"
        creatureList = []

        creatureCount = {} # dictionary containing frequency of creatures
        for c in self.creatures:
            creatureType = c.get_species()
            if creatureType not in creatureCount:
                creatureCount[creatureType] = 1
            else:
                creatureCount[creatureType] += 1
            creatureList.append("{} {} {} {}".format(creatureType, c.row, c.col, c.direction))
        creatureCount = list(creatureCount.items()) # Change dict in list of tuples
        creatureCount.sort()
        creatureCount.sort(key=lambda kv:kv[1], reverse=True) # Sort highest freq -> lowest
        # Piece together the return string
        returnString += str(self.size) + "\n" # First line is size
        returnString += str(creatureCount) + "\n" # Second line is the frequency of different creatures
        for creatureInfo in creatureList: # Then the inividual creatures and their info
            returnString += creatureInfo + "\n"

        return returnString

    """Display the world by drawing the creature, and placing a grid around it"""
    def draw(self):

        # Basic coordinates of grid within 800x800 window - total width and position of top left corner
        grid_width = 700
        top_left_x = -350
        top_left_y = 350
        grid_size = grid_width / self.size

        # Draw the creatures
        for c in self.creatures:
            c.draw(grid_size, top_left_x, top_left_y)

        # Draw the bounding box
        turtle.goto(top_left_x, top_left_y)
        turtle.setheading(0)
        turtle.pendown()
        for i in range(0, 4):
            turtle.rt(90)
            turtle.forward(grid_width)
        turtle.penup()

        # Draw rows
        for i in range(self.size):
            turtle.setheading(90)
            turtle.goto(top_left_x, top_left_y - grid_size*i)
            turtle.pendown()
            turtle.forward(grid_width)
            turtle.penup()

        # Draw columns
        for i in range(self.size):
            turtle.setheading(180)
            turtle.goto(top_left_x + grid_size*i, top_left_y)
            turtle.pendown()
            turtle.forward(grid_width)
            turtle.penup()


"""This class reads the data files from disk and sets up the window"""
class CreatureWorld:

    ## Initialises the window, and registers the begin_simulation function to be called when the space-bar is pressed
    def __init__(self):
        self.framework = SimulationFramework(800, 800, 'Creatures')
        self.framework.add_key_action(self.begin_simulation, ' ')
        self.framework.add_tick_action(self.next_turn, 100) # Delay between animation "ticks" - smaller is faster.

    ## Starts the animation
    def begin_simulation(self):
        self.framework.start_simulation()

    ## Ends the animation
    def end_simulation(self):
        self.framework.stop_simulation()

    ## Reads the data files from disk
    def setup_simulation(self):
        
        ## If new creatures are defined, they should be added to this list:
        all_creatures = ['Hopper', 'Roomber', 'Randy', 'Flytrap', 'Parry', 'Rook', 'Patrol', 'Twisty']    

        # Read the creature location data
        with open('world_input.txt') as f:
            world_data = f.read().splitlines()

        # Read the dna data for each creature type
        dna_dict = {}
        for creature in all_creatures:
            with open('Creatures//' + creature + '.txt') as f:
                dna_dict[creature] = f.read().splitlines()        

        # Create a world of the specified size, and set the number of generations to be performed when the simulation runs
        world_size = world_data[0]
        world_generations = world_data[1]
        self.world = World(int(world_size), int(world_generations))
        # Add creatures
        currentCreatures = [] # Keeps tuples of the squares that are occupied
        for i in range(2, len(world_data)): # Loops from first to n'th creature
            creature = world_data[i]
            data = creature.split()
            # Only adds the creature at (row, col) from wolrd_input if not already occupied
            if (data[1], data[2]) not in currentCreatures:
                self.world.add_creature(Creature(int(data[1]), int(data[2]), dna_dict[data[0]], data[3]))
                currentCreatures.append((data[1], data[2]))

        # Draw the initial layout of the world
        self.world.draw()

    ## This function is called each time the animation loop "ticks".  The screen should be redrawn each time.         
    def next_turn(self):
        turtle.clear()
        self.world.draw() 
        if self.world.simulate():
            self.end_simulation()

    ## This function sets up the simulation and starts the animation loop
    def start(self):
        self.setup_simulation() 
        turtle.mainloop() # Must appear last.


## This is the simulation framework - it does not need to be edited
class SimulationFramework:

    def __init__(self, width, height, title):
        self.width = width
        self.height = height
        self.title = title
        self.simulation_running = False
        self.tick = None #function to call for each animation cycle
        self.delay = 100 #default is .1 second.       
        turtle.title(title) #title for the window
        turtle.setup(width, height) #set window display
        turtle.hideturtle() #prevent turtle appearance
        turtle.tracer(False) #prevent turtle animation
        turtle.listen() #set window focus to the turtle window
        turtle.mode('logo') #set 0 direction as straight up
        turtle.penup() #don't draw anything
        self.__animation_loop()
        
    def start_simulation(self):
        self.simulation_running = True
        
    def stop_simulation(self):
        self.simulation_running = False

    def add_key_action(self, func, key):
        turtle.onkeypress(func, key)

    def add_tick_action(self, func, delay):
        self.tick = func
        self.delay = delay

    def __animation_loop(self):
        if self.simulation_running:
            self.tick()
        turtle.ontimer(self.__animation_loop, self.delay)
   
cw = CreatureWorld()

cw.start()
