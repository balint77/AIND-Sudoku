from collections import Counter

assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'


def cross(a, b):
    return [s + t for s in a for t in b]


boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
# diagonal_units contains the two diagonal units
diagonal_units = [[rows[i] + cols[i] for i in range(len(cols))],
                  [rows[i] + cols[len(cols) - 1 - i] for i in range(len(cols))]]
# unitlist is all of the units including the diagonal ones
unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def removeTwinValuesFromUnit(twins, unit, values):
    """removes the two values of the twins from all the other boxes in the unit"""
    for box in unit:
        value = values[box]
        if value != twins:
            #dont touch the twins themselves
            values[box] = value.replace(twins[0], "").replace(twins[1], "")
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    potentialTwins = Counter()
    for unit in unitlist:
        #lets count how many boxes we have with two values in the actual unit
        #potentialTwins keeps track from which value pairs how many we have in the unit
        potentialTwins.clear()
        for box in unit:
            value = values[box]
            if len(value) == 2:
                potentialTwins[value] += 1
        # now lets see if we have 2+ boxes with the same value pair in it
        for content, count in potentialTwins.items():
            if count > 1:
                # we have found a twin, lets clear its value from all the other boxes in the unit
                # note: if count is 3+ the sudoku is not solveable but that is a responsiblity of another method
                # to take care of
                values = removeTwinValuesFromUnit(content, unit, values)
    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    return dict((v, cols if grid[k] == '.' else grid[k]) for k, v in enumerate(boxes))


def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def removeIt(valueToRemove, boxes, values):
    """ removes a given value from a set of boxes's """
    for box in boxes:
        boxValue = values[box]
        if valueToRemove in boxValue:
            values[box] = boxValue.replace(valueToRemove, "")


def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    for k, v in values.items():
        if len(v) == 1:
            removeIt(v, peers[k], values)
    return values


def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values


def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Use the Eliminate Strategy
        values = eliminate(values)
        # Use the Only Choice Strategy
        values = only_choice(values)
        # Use the Naked Twins Strategy
        values = naked_twins(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        if (solved_values_after == 81):
            break
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    # display(values)
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values == False:
        # dead end
        return values
    # Choose one of the unfilled squares with the fewest possibilities
    minLen = 10
    minBox = None
    for k, v in values.items():
        myLen = len(v)
        if myLen > 1 and myLen < minLen:
            minLen = myLen
            minBox = k
    if minBox == None:
        # sudoku solved, no box with more than one value
        return values
    variations = values[minBox]
    for c in variations:
        #choose next option for actual box
        valuesNew = dict(values)
        valuesNew[minBox] = c
        #go deeper in search tree
        valuesNew = search(valuesNew)
        if valuesNew != False:
            #sudoku solved no need to iterate further
            return valuesNew
    return False


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    # to solve a diagonal sudoku see the diagonal_units variable added to the units that are taken into consideration
    values = search(grid_values(grid))
    return values


if __name__ == '__main__':
    #diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    diag_sudoku_grid = '......8.68.........7..863.....8............8..8.5.9...1.8..............8.....8.4.'
    display(grid_values(diag_sudoku_grid))
    display(solve(diag_sudoku_grid))
    try:
        from visualize import visualize_assignments

        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
