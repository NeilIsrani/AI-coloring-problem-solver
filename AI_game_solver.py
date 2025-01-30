import time
import math
import random
import numpy as np
from gridgame import *

##############################################################################################################################

# You can visualize what your code is doing by setting the GUI argument in the following line to true.
# The render_delay_sec argument allows you to slow down the animation, to be able to see each step more clearly.

# For your final submission, please set the GUI option to False.

# The gs argument controls the grid size. You should experiment with various sizes to ensure your code generalizes.
# Please do not modify or remove lines 18 and 19.

##############################################################################################################################

game = ShapePlacementGrid(GUI=True, render_delay_sec=0.1, gs=6, num_colored_boxes=5)
shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')
np.savetxt('initial_grid.txt', grid, fmt="%d")

##############################################################################################################################

# Initialization

# shapePos is the current position of the brush.

# currentShapeIndex is the index of the current brush type being placed (order specified in gridgame.py, and assignment instructions).

# currentColorIndex is the index of the current color being placed (order specified in gridgame.py, and assignment instructions).

# grid represents the current state of the board. 
    
    # -1 indicates an empty cell
    # 0 indicates a cell colored in the first color (indigo by default)
    # 1 indicates a cell colored in the second color (taupe by default)
    # 2 indicates a cell colored in the third color (veridian by default)
    # 3 indicates a cell colored in the fourth color (peach by default)

# placedShapes is a list of shapes that have currently been placed on the board.
    
    # Each shape is represented as a list containing three elements: a) the brush type (number between 0-8), 
    # b) the location of the shape (coordinates of top-left cell of the shape) and c) color of the shape (number between 0-3)

    # For instance [0, (0,0), 2] represents a shape spanning a single cell in the color 2=veridian, placed at the top left cell in the grid.

# done is a Boolean that represents whether coloring constraints are satisfied. Updated by the gridgames.py file.

##############################################################################################################################

shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')

#input()   # <-- workaround to prevent PyGame window from closing after execute() is called, for when GUI set to True. Uncomment to enable.
print(shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done)


####################################################
# Timing your code's execution for the leaderboard.
####################################################

start = time.time()  # <- do not modify this.



##########################################
# Write all your code in the area below. 
##########################################



# def find_empty_cell(grid):
#     """Find the first empty cell in the grid."""
#     for i in range(len(grid)):
#         for j in range(len(grid[0])):
#             if grid[i][j] == -1:
#                 return (i, j)
#     return None

# def can_place_shape(game, grid, shape_index, pos, color_index):
#     """Check if a shape can be placed at the given position with the given color."""
#     shape = game.shapes[shape_index]
#     height, width = shape.shape
    
#     # Check bounds
#     if pos[0] + height > len(grid) or pos[1] + width > len(grid[0]):
#         return False
    
#     # Check overlap and color constraints
#     for i in range(height):
#         for j in range(width):
#             if shape[i][j] == 1:
#                 # Check if cell is empty
#                 if grid[pos[0] + i][pos[1] + j] != -1:
#                     return False
                
#                 # Check adjacent colors
#                 for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
#                     ni, nj = pos[0] + i + di, pos[1] + j + dj
#                     if (0 <= ni < len(grid) and 0 <= nj < len(grid) and 
#                         grid[ni][nj] == color_index):
#                         return False
    
#     return True

# def solve_grid_b(game):
#     """Main solving function using backtracking."""
#     shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')
    
#     def backtrack():
#         if done:
#             return True
            
#         empty = find_empty_cell(grid)
#         if not empty:
#             return True
            
#         row, col = empty
        
#         # Try each shape
#         for shape_idx in range(len(game.shapes)):
#             # Move to shape
#             while currentShapeIndex != shape_idx:
#                 game.execute('h')
                
#             # Try each color
#             for color_idx in range(len(game.colors)):
#                 # Move to color
#                 while currentColorIndex != color_idx:
#                     game.execute('k')
                
#                 # Move to position
#                 game.execute('export')  # Reset position
#                 while shapePos[1] != row:
#                     game.execute('s' if shapePos[1] < row else 'w')
#                 while shapePos[0] != col:
#                     game.execute('d' if shapePos[0] < col else 'a')
                
#                 if can_place_shape(game, grid, shape_idx, (row, col), color_idx):
#                     # Place shape
#                     game.execute('p')
                    
#                     # Recurse
#                     if backtrack():
#                         return True
                    
#                     # Undo if needed
#                     game.execute('u')
        
#         return False
    
#     backtrack()
#     return placedShapes

def evaluate_board(grid):
    score = 0
    size = len(grid)

    score += np.sum(grid == -1)
    #neg scoring for same color neighbors
    for i in range(size):
        for j in range(size):
            if grid[i][j] != -1:
                #horizontal placement
                if j < size - 1 and grid[i][j] == grid[i][j + 1]:
                    score += 20
                # vertical placement 
                if i < size - 1 and grid[i][j] == grid[i+1][j]:
                    score += 20
    return score

def randomizer(game, grid):
    size = len(grid)

    shape_rand = random.randint(0, len(game.shapes) - 1)
    color_rand = random.randint(0, len(game.colors) - 1)

    shape = game.shapes[shape_rand]
    height, width = shape.shape
    x = random.randint(0, size - width)
    y = random.randint(0, size - height)

    return {
        'shape_rand': shape_rand,
        'color_rand': color_rand,
        'pos': [x, y]
    }
# This function uses execute function of gridgame 
def mover(game, move):
    while game.currentShapeIndex != move['shape_rand']:
        game.execute('h')
    
    while game.currentColorIndex != move['color_rand']:
        game.execute('k')
    
    target_x, target_y = move['pos']
    while game.shapePos[0] != target_x:
        if game.shapePos[0] < target_x:
            #try one position right
            game.execute('d')
        elif game.shapePos[0] > target_x:
            #try one position left
            game.execute('a')


    while game.shapePos[1] != target_y:
        if game.shapePos[1] < target_y:
            #try one position down
            game.execute('s')
        elif game.shapePos[1] > target_y:
            #try one position up
            game.execute('w')
    
    game.execute('p')
    return game.execute('e')
    
def sim_anneal_solve_grid(game, initial_temp = 100.0, cooling_rate = 0.95, min_temp = 0.1):
    current_temp = initial_temp

    #fetch starting state
    shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('e')
    current_score = evaluate_board(grid)

    #dynamic values for grid, score, and shapes
    curr_grid = grid.copy()
    curr_score = current_score
    curr_shapes = placedShapes.copy()

    while current_temp > min_temp and not done:
        move = randomizer(game, grid)
        _, _, _, new_grid, new_shapes, new_done = mover(game, move)
        new_score = evaluate_board(new_grid)

        score_diff = new_score - current_score
        if score_diff < 0 or random.random() < math.exp(-score_diff / current_temp):
            curr_score = new_score
            grid = new_grid.copy()
            placedShapes = new_shapes.copy()
            done = new_done
            
            # Update best solution if this is better
            if current_score < curr_score:
                curr_score = current_score
                curr_grid = grid.copy()
                curr_shapes = placedShapes.copy()
        else:
            # Reject move - undo
            game.execute('u')
        
        # Cool down
        current_temp *= cooling_rate
    
    return curr_grid

def main():
    game = ShapePlacementGrid(GUI=True, render_delay_sec=0.1, gs=6, num_colored_boxes=5)
    solution = sim_anneal_solve_grid(game)
    return solution

if __name__ == "__main__":
    main()








'''

YOUR CODE HERE


'''










########################################

# Do not modify any of the code below. 

########################################

end=time.time()

np.savetxt('grid.txt', grid, fmt="%d")
with open("shapes.txt", "w") as outfile:
    outfile.write(str(placedShapes))
with open("time.txt", "w") as outfile:
    outfile.write(str(end-start))

def main():
    game = ShapePlacementGrid(GUI=True, render_delay_sec=0.1, gs=6, num_colored_boxes=5)
    solution = solve_grid(game)
    return solution

if __name__ == "__main__":
    main()