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


def evaluate_window(window, piece):
  score = 0
  if random.randint(1, 20) == 1:
    print(window)
  opp_piece = PLAYER_PIECE
  if piece == PLAYER_PIECE:
    opp_piece = AI_PIECE

  if window.count(piece) == 4:
    score += 100
  elif window.count(piece) == 3 and window.count(EMPTY) == 1:
    score += 5
  elif window.count(piece) == 2 and window.count(EMPTY) == 2:
    score += 2

  if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
    score -= 4

  return score


def is_valid_location(board, col, empty):
  return board[5][col] == empty


def get_valid_locations(board, empty):
  valid_locations = []
  for col in range(7):
    if is_valid_location(board, col, empty):
      valid_locations.append(col)
  return valid_locations


def get_next_open_row(board, col, empty):
  for r in range(6):
    if board[r][col] == empty:
      return r


def drop_piece(board, row, col, piece):
  board[row][col] = piece


def score_array(array):
  scores = []
  for i in array:
    if i == ':blue_square:':
      scores.append(0)
    elif i == ':red_circle:':
      scores.append(1)
    elif i == ':yellow_circle:':
      scores.append(2)
    else:
      scores.append(int(i))
  return scores


def score_position(board, piece):
  score = 0

  ## Score center column
  center_array = score_array(list(board[:, 7 // 2]))
  center_count = center_array.count(piece)
  score += center_count * 3

  ## Score Horizontal
  for r in range(6):
    row_array = score_array(list(board[r, :]))
    for c in range(4):
      window = row_array[c:c + 4]
      score += evaluate_window(window, piece)

  ## Score Vertical
  for c in range(7):
    col_array = score_array(list(board[:, c]))
    for r in range(3):
      window = col_array[r:r + 4]
      score += evaluate_window(window, piece)

  ## Score posiive sloped diagonal
  for r in range(3):
    for c in range(4):
      window = [board[r + i][c + i] for i in range(4)]
      window = score_array(window)
      score += evaluate_window(window, piece)

  for r in range(3):
    for c in range(4):
      window = [board[r + 3 - i][c + i] for i in range(4)]
      window = score_array(window)
      score += evaluate_window(window, piece)

  return score


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


def is_terminal_node(board, empty):
  return winning_move(board, PLAYER_PIECE) or winning_move(
    board, AI_PIECE) or len(get_valid_locations(board, empty)) == 0


def minimax(board, depth, alpha, beta, maximizingPlayer, empty):
  valid_locations = get_valid_locations(board, empty)
  is_terminal = is_terminal_node(board, empty)
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
      row = get_next_open_row(board, col, empty)
      b_copy = board.copy()
      drop_piece(b_copy, row, col, AI_PIECE)
      new_score = minimax(b_copy, depth - 1, alpha, beta, False, empty)[1]
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
      row = get_next_open_row(board, col, empty)
      b_copy = board.copy()
      drop_piece(b_copy, row, col, PLAYER_PIECE)
      new_score = minimax(b_copy, depth - 1, alpha, beta, True, empty)[1]
      if new_score < value:
        value = new_score
        column = col
      beta = min(beta, value)
      if alpha >= beta:
        break
    return column, value


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
    text = ''
    for ind, row in enumerate(self.gameboard):
      for ind2, col in enumerate(row):
        text += col
      text += '\n'
    return text

  def place(self, num, color):
    column = [i[num - 1] for i in self.gameboard]
    for m in column:
      if m != self.empty:
        self.gameboard[column.index(m) - 1][num - 1] = color
        break
    else:
      self.gameboard[5][num - 1] = color

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

  def __init__(self, empty):
    self.empty = empty
    self.gameboard = np.asarray([[empty for _ in range(7)] for _ in range(6)])

  def print_board(self):
    text = ''
    for ind, row in enumerate(self.gameboard):
      for ind2, col in enumerate(row):
        if 'yellow_circl' in col:
          text += ':yellow_circle:'
        else:
          text += col
      text += '\n'
    return text

  def place(self, num, color):
    column = [i[num - 1] for i in self.gameboard]
    for m in column:
      if m != self.empty:
        self.gameboard[column.index(m) - 1, num - 1] = color
        break
    else:
      self.gameboard[5, num - 1] = color

  def is_full(self, num):
    return self.gameboard[0, num - 1] != self.empty

  def all_full(self):
    return all(self.gameboard[0, i] != self.empty for i in range(7))

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
    col, minimax_score = minimax(self.gameboard, 5, -math.inf, math.inf, True,
                                 self.empty)
    return col, minimax_score


class Gamemode(Enum):
  NORMAL = 1
  EXTREME = 2
  INVISIBLE = 3
  SWIFTPLAY = 4
