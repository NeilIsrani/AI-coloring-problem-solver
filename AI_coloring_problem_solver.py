
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

game = ShapePlacementGrid(GUI=False, render_delay_sec=0.1, gs=6, num_colored_boxes=5)
shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')
np.savetxt('initial_grid.txt', grid, fmt="%d")

##############################################################################################################################

shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')
#input() 
print(shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done)

####################################################
# Timing your code's execution for the leaderboard.
####################################################

start = time.time()  # <- do not modify this.

##########################################
# Write all your code in the area below. 
##########################################

def evaluate_board(grid):
    score = 0
    size = len(grid)
    
    # Penalize empty cells (-1)
    score -= np.sum(grid == -1) * 10  # Increased penalty for empty cells
    
    # Reward fully filled grid
    if -1 not in grid:
        score += 1000  # Reward for completing the grid
    
    # Penalize same color neighbors
    for i in range(size):
        for j in range(size):
            if grid[i][j] != -1:
                # Horizontal placement
                if j < size - 1 and grid[i][j] == grid[i][j + 1]:
                    score -= 50  # Increased penalty for color conflicts
                # Vertical placement 
                if i < size - 1 and grid[i][j] == grid[i + 1][j]:
                    score -= 50  # Increased penalty for color conflicts
    return score

def randomizer(game, grid):
    size = len(grid)
    
    shape_rand = random.randint(0, len(game.shapes) - 1)
    color_rand = random.randint(0, len(game.colors) - 1)
    
    shape = game.shapes[shape_rand]
    height, width = shape.shape
    
    # Ensure positions are valid for shape dimensions
    x = random.randint(0, size - width)
    y = random.randint(0, size - height)
    
    return {
        'shape_rand': shape_rand,
        'color_rand': color_rand,
        'pos': [x, y]
    }

def is_valid_placement(grid, shape, pos, color_index):
    """
    Check if placing the shape at the given position with the given color would violate adjacency constraints.
    """
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                x = pos[0] + j
                y = pos[1] + i
                # Check adjacent cells
                if x > 0 and grid[y][x - 1] == color_index:
                    return False
                if x < len(grid) - 1 and grid[y][x + 1] == color_index:
                    return False
                if y > 0 and grid[y - 1][x] == color_index:
                    return False
                if y < len(grid) - 1 and grid[y + 1][x] == color_index:
                    return False
    return True

def mover(game, move):
    # Switch to correct shape
    while game.currentShapeIndex != move['shape_rand']:
        shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('h')
    
    # Switch to correct color
    while game.currentColorIndex != move['color_rand']:
        shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('k')
    
    target_x, target_y = move['pos']
    
    # Move horizontally
    while game.shapePos[0] != target_x:
        if game.shapePos[0] < target_x:
            shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('d')
        else:
            shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('a')
    
    # Move vertically
    while game.shapePos[1] != target_y:
        if game.shapePos[1] < target_y:
            shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('s')
        else:
            shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('w')
    
    # Check if the placement is valid before placing the shape
    shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')
    if is_valid_placement(grid, game.shapes[move['shape_rand']], move['pos'], move['color_rand']):
        shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('p')
    else:
        # If placement is invalid, return the current state without placing the shape
        return game.execute('e')
    
    return game.execute('e')

def fill_remaining_cells(game, grid):
    size = len(grid)
    while -1 in grid:
        # Find all empty cells
        empty_cells = np.argwhere(grid == -1)
        if len(empty_cells) == 0:
            break  # No more empty cells
        
        # Try to fill each empty cell with the smallest shape (1x1)
        for cell in empty_cells:
            y, x = cell  # Get the coordinates of the empty cell
            
            # Check if a valid color exists for this cell
            valid_color = game.getAvailableColor(grid, x, y)
            if valid_color is None:
                # No valid color exists for this cell, so we cannot fill it
                print("No valid color for cell:", (x, y), "- Terminating early.")
                return grid, game.placedShapes
            
            # Try to place the smallest shape (1x1) with the valid color
            shape_index = 0  # 1x1 square
            move = {
                'shape_rand': shape_index,
                'color_rand': valid_color,
                'pos': [x, y]
            }
            
            # Attempt to place the shape
            new_pos, new_shape_idx, new_color_idx, new_grid, new_shapes, new_done = mover(game, move)
            
            # Update the grid state
            if new_shapes != game.placedShapes:  # If the shape was successfully placed
                grid = new_grid.copy()
                game.placedShapes = new_shapes.copy()
            else:
                # If the shape could not be placed, skip this cell
                print("Could not place shape at cell:", (x, y))
        
    return grid, game.placedShapes

def solve_grid(game, initial_temp=100.0, cooling_rate=0.99, min_temp=0.1):
    current_temp = initial_temp
    
    # Get initial state
    shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')
    current_score = evaluate_board(grid)
    
    # Keep track of best solution
    best_grid = grid.copy()
    best_score = current_score
    best_shapes = placedShapes.copy()
    
    while current_temp > min_temp:
        # Check if the grid is fully filled
        if -1 not in grid:
            break  # Terminate if the grid is fully filled
        
        # Generate random move
        move = randomizer(game, grid)
        
        # Try the move
        new_pos, new_shape_idx, new_color_idx, new_grid, new_shapes, new_done = mover(game, move)
        
        if new_shapes != placedShapes:  # Only evaluate if shape was successfully placed
            new_score = evaluate_board(new_grid)
            score_diff = new_score - current_score
            
            # Decide whether to accept move
            if score_diff > 0 or random.random() < math.exp(score_diff / current_temp):
                current_score = new_score
                grid = new_grid.copy()
                placedShapes = new_shapes.copy()
                done = new_done
                
                # Update best solution if this is better
                if current_score > best_score:
                    best_score = current_score
                    best_grid = grid.copy()
                    best_shapes = new_shapes.copy()
            else:
                # Undo move if rejected
                shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('u')
        
        # Cool down temperature
        current_temp *= cooling_rate
    
    # Force completion of the grid if there are still empty cells
    if -1 in grid:
        print("Attempting to fill remaining cells...")
        grid, placedShapes = fill_remaining_cells(game, grid)
    
    return placedShapes, grid

# Solve the grid
solve_grid(game)
shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')

########################################
# Do not modify any of the code below. 
########################################

end = time.time()

np.savetxt('grid.txt', grid, fmt="%d")
with open("shapes.txt", "w") as outfile:
    outfile.write(str(placedShapes))
with open("time.txt", "w") as outfile:
    outfile.write(str(end-start))