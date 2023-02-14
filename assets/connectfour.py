from enum import Enum
import numpy as np
import random
import time
import math
# Code taken from https://github.com/KeithGalli/Connect4-Python/blob/master/connect4_with_ai.py

COLUMN_COUNT = 7
ROW_COUNT = 6
EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2
WINDOW_LENGTH = 4
transpo = {}


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0


def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r


def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c + 1] == piece and board[r][
                    c + 2] == piece and board[r][c + 3] == piece:
                return True

    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c] == piece and board[
                    r + 2][c] == piece and board[r + 3][c] == piece:
                return True

    # Check positively sloped diaganols
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c + 1] == piece and board[
                    r + 2][c + 2] == piece and board[r + 3][c + 3] == piece:
                return True

    # Check negatively sloped diaganols
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r - 1][c + 1] == piece and board[
                    r - 2][c + 2] == piece and board[r - 3][c + 3] == piece:
                return True


def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 4:
        score += 1000
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 2 and window.count(EMPTY) == 2:
        score -= 2
    elif window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 100

    return score


def score_position(board, piece):
    score = 0

    ## Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    ## Score Horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    ## Score Vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    ## Score posiive sloped diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score


def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(
        board, AI_PIECE) or len(get_valid_locations(board)) == 0


def minimax(board, depth, alpha, beta, maximizingPlayer):
    x = 7
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000000000000)
            else:  # Game is over, no more valid moves
                return (None, 0)
        else:  # Depth is zero
            return (None, score_position(board, AI_PIECE))
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            if hash(tuple([tuple(row) for row in b_copy])) not in transpo:
                new_score = minimax(b_copy, depth - 1, alpha, beta,
                                    False)[1] + random.randint(-x, x)
            else:
                new_score = transpo[hash(tuple([tuple(row) for row in b_copy
                                                ]))] + random.randint(-x, x)
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else:  # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            if hash(tuple([tuple(row) for row in b_copy])) not in transpo:
                new_score = minimax(b_copy, depth - 1, alpha, beta,
                                    True)[1] + random.randint(-x, x)
            else:
                new_score = transpo[hash(tuple([tuple(row) for row in b_copy
                                                ]))] + random.randint(-x, x)
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value


def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations


class ConnectFour:

    def __init__(self, empty, players):
        self.empty = empty
        self.gameboard = [[empty for _ in range(7)] for _ in range(6)]
        self.players = players
        self.red = players[0]
        self.yellow = players[1]
        self.last = time.time()
        self.guaranteed = True
        self.gamemode = None
        self.move_count = 0

    def print_board(self):
        if self.gamemode == Gamemode.EXTREME:
            game_theme = self.bot.database['members'][str(
                self.turn.id)]['settings']['c4extremetheme']
            theme_map = {
                'Default': ':c4_fire:',
                'Sakura': '<:THEME_sakura:1065929561419825162>',
                'Pink-Blue': '<a:THEME_colorful:1065931156685606973>',
                'Anika In Space': '<:THEME_anika:1073873897360982076>',
                'Galaxy': '<:THEME_galaxy:1073875133925699624>',
                'Charles': '<:THEME_charles:1073876973824266351>'
            }
        else:
            game_theme = self.bot.database['members'][str(
                self.turn.id)]['settings']['c4gametheme']
            theme_map = {
                'Default': ':blue_square:',
                'Sakura': '<:THEME_sakura:1065929561419825162>',
                'Pink-Blue': '<a:THEME_colorful:1065931156685606973>',
                'Anika In Space': '<:THEME_anika:1073873897360982076>',
                'Galaxy': '<:THEME_galaxy:1073875133925699624>',
                'Charles': '<:THEME_charles:1073876973824266351>'
            }
        text = ''
        for ind, row in enumerate(self.gameboard):
            for ind2, col in enumerate(row):
                if col == self.empty:  # fix for custom board theme
                    text += theme_map[game_theme]
                else:
                    text += col
            text += '\n'
        number_row = self.bot.database['members'][str(
            self.turn.id)]['settings']['number_row']
        if number_row == 'Enabled':
            text += ':one::two::three::four::five::six::seven:'
        return text

    def place(self, num, color):
        column = [i[num - 1] for i in self.gameboard]
        for m in column:
            if m != self.empty:
                self.gameboard[column.index(m) - 1][num - 1] = color
                break
        else:
            self.gameboard[5][num - 1] = color
        self.move_count += 1

    def extreme_explosion(self):
        coords = (random.randint(0, 5), random.randint(0, 6))
        while self.gameboard[coords[0]][coords[1]] != self.empty:
            coords = (random.randint(0, 5), random.randint(0, 6))
        self.gameboard[coords[0]][
            coords[1]] = '<a:c4_explosion:1056120412133675028>'
        return coords

    def extreme_petrify(self, coords):
        self.gameboard[coords[0]][coords[1]] = ':black_large_square:'

    def is_full(self, num):
        return self.gameboard[0][num - 1] != self.empty

    def all_full(self):
        return all(self.gameboard[0][i] != self.empty for i in range(7))

    def win_check(self, color):
        # vertical wins
        for ia in range(3):  # rows
            for ib in range(7):  # columns
                if self.gameboard[::-1][ia][ib] == color and self.gameboard[::-1][ia + 1][ib] == color and \
                        self.gameboard[::-1][ia + 2][ib] == color and self.gameboard[::-1][ia + 3][ib] == color:
                    return True
        # horizontal wins
        for ja in range(6):  # rows
            for jb in range(4):  # columns
                if self.gameboard[::-1][ja][jb] == color and self.gameboard[::-1][ja][jb + 1] == color and \
                        self.gameboard[::-1][ja][jb + 2] == color and self.gameboard[::-1][ja][jb + 3] == color:
                    return True
        # diagonal wins (bottom left - top right)
        for ka in range(3):  # rows
            for kb in range(4):  # columns
                if self.gameboard[::-1][ka][kb] == color and self.gameboard[::-1][ka + 1][kb + 1] == color and \
                        self.gameboard[::-1][ka + 2][kb + 2] == color and self.gameboard[::-1][ka + 3][kb + 3] == color:
                    return True
        # diagonal wins (top left - bottom right)
        for ha in range(3):  # rows
            for hb in range(4):  # columns
                if self.gameboard[::-1][ha + 3][hb] == color and self.gameboard[::-1][ha + 2][hb + 1] == color and \
                        self.gameboard[::-1][ha + 1][hb + 2] == color and self.gameboard[::-1][ha][hb + 3] == color:
                    return True
        return False


class ConnectFourAI:

    def __init__(self, empty, depth):
        self.empty = empty
        self.difficulty = depth
        self.gameboard = np.zeros((ROW_COUNT, COLUMN_COUNT))
        self.move_count = 0

    def print_board(self):
        text = ''
        for ind, row in enumerate(self.gameboard[::-1]):
            for ind2, col in enumerate(row):
                d = {0: self.empty, 1: ':red_circle:', 2: ':yellow_circle:'}
                text += d[col]
            text += '\n'
        number_row = self.bot.database['members'][str(
            self.user.id)]['settings']['number_row']
        if number_row == 'Enabled':
            text += ':one::two::three::four::five::six::seven:'
        return text

    def place(self, num, color):
        column = [i[num - 1] for i in self.gameboard]
        for m in column:
            if m == 0:
                self.gameboard[column.index(m), num - 1] = color
                break
        else:
            self.gameboard[0, num - 1] = color
        self.move_count += 1

    def is_full(self, num):
        return self.gameboard[5, num - 1] != 0

    def all_full(self):
        return all(self.gameboard[5, i] != 0 for i in range(7))

    def win_check(self, color):
        # vertical wins
        for ia in range(3):  # rows
            for ib in range(7):  # columns
                if self.gameboard[::-1][ia, ib] == color and self.gameboard[::-1][ia + 1, ib] == color and \
                        self.gameboard[::-1][ia + 2, ib] == color and self.gameboard[::-1][ia + 3, ib] == color:
                    return True
        # horizontal wins
        for ja in range(6):  # rows
            for jb in range(4):  # columns
                if self.gameboard[::-1][ja, jb] == color and self.gameboard[::-1][ja, jb + 1] == color and \
                        self.gameboard[::-1][ja, jb + 2] == color and self.gameboard[::-1][ja, jb + 3] == color:
                    return True
        # diagonal wins (bottom left - top right)
        for ka in range(3):  # rows
            for kb in range(4):  # columns
                if self.gameboard[::-1][ka, kb] == color and self.gameboard[::-1][ka + 1, kb + 1] == color and \
                        self.gameboard[::-1][ka + 2, kb + 2] == color and self.gameboard[::-1][ka + 3, kb + 3] == color:
                    return True
        # diagonal wins (top left - bottom right)
        for ha in range(3):  # rows
            for hb in range(4):  # columns
                if self.gameboard[::-1][ha + 3, hb] == color and self.gameboard[::-1][ha + 2, hb + 1] == color and \
                        self.gameboard[::-1][ha + 1, hb + 2] == color and self.gameboard[::-1][ha, hb + 3] == color:
                    return True
        return False

    def ai_place(self):
        col, minimax_score = minimax(self.gameboard, self.difficulty,
                                     -math.inf, math.inf, True)
        return col


class Gamemode(Enum):
    NORMAL = 1
    EXTREME = 2
    INVISIBLE = 3
    SWIFTPLAY = 4
