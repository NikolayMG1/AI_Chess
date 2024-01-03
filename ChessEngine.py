# log of the game, valid moves

class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]

        self.move_functions = {'p': self.get_pawn_moves, 'R': self.get_rook_moves, 'N':self.get_knight_moves, 'B':self.get_bishop_moves,
                               'Q':self.get_queen_moves, 'K':self.get_king_moves}
        self.whiteMove = True
        self.moveLog = []
        self.white_king_loc = (7,4)
        self.black_king_loc = (0,4)
        self.checkmate = False
        self.stalemate = False
        self.enpassantPoss = ()
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.CastleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]

    def make_move(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #log of moves
        self.whiteMove = not self.whiteMove #switch turns

        #changes kings loc
        if move.pieceMoved == 'wK':
            self.white_king_loc = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.black_king_loc = (move.endRow, move.endCol)

        #pown prom
        if move.isPawnProm:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
        
        #enpass move  
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--' #capturing the pawn

        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPoss = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPoss = ()

        if move.isCastleMove:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1] = '--'
            else:
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = '--'

        # update castle righs
        self.updateCastleRights(move)
        self.CastleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))
        
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.bks = False

    def undo_move(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteMove = not self.whiteMove  
            if move.pieceMoved == 'wK':
                self.white_king_loc = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.black_king_loc = (move.startRow, move.startCol)
            # undo enpassant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPoss = (move.endRow, move.endCol)
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPoss = ()
            # undo castling
            self.CastleRightsLog.pop()
            self.currentCastlingRights = self.CastleRightsLog[-1]

            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else:
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = '--'
        
        self.checkmate = False
        self.stalemate =  False
        
    def valid_moves(self):
        tempEnpassPoss = self.enpassantPoss
        tempCastleRights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)
        # 1. generate all moves
        moves = self.get_all_possible_moves()
        if self.whiteMove:
            self.get_castle_moves(self.white_king_loc[0], self.white_king_loc[1], moves)
        else:
            self.get_castle_moves(self.black_king_loc[0], self.black_king_loc[1], moves)
        # 2. make each move
        for i in range(len(moves)-1, -1, -1):
            self.make_move(moves[i])
            # 3. make all op moves
            op_move = self.get_all_possible_moves()
        # 4. check if op moves aa the king
            self.whiteMove = not self.whiteMove
            if self.in_check():
                moves.remove(moves[i])
            self.whiteMove = not self.whiteMove
            self.undo_move()
        # 5. if yes not valid  

        if len(moves) == 0:
            if self.in_check():
                self.checkmate = True
            else:
                self.stalemate = True
        self.enpassantPoss = tempEnpassPoss    
        self.currentCastlingRights = tempCastleRights 
        return moves
    
    def in_check(self):
        if self.whiteMove:
            return self.sq_attacked(self.white_king_loc[0],self.white_king_loc[1])
        else:
            return self.sq_attacked(self.black_king_loc[0],self.black_king_loc[1])

    def sq_attacked(self, r, c):
        self.whiteMove = not self.whiteMove
        op_move = self.get_all_possible_moves()
        self.whiteMove = not self.whiteMove

        for move in op_move:
            if move.endRow == r and move.endCol == c:
                return True
        return False


    # def validator(end_row, end_col):
        return 0 <= end_row < 8 and 0 <= end_col < 8
    
    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteMove) or (turn == 'b' and not self.whiteMove):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r,c,moves)

        return moves
    
    def get_knight_moves(self, r, c, moves):
        dirs = ((2, 1),
                (2, -1),
                (-2, +1),
                (-2, -1),
                (+1, +2),
                (+1, -2),
                (-1, -2),
                (-1, +2))
        same = 'w' if self.whiteMove else 'b'

        for dir in dirs:
            end_row = dir[0] + r
            end_col = dir[1] + c
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != same:
                    moves.append(Move((r,c), (end_row, end_col), self.board))

    def get_king_moves(self, r, c, moves):
        dirs = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        allyColor = 'w' if self.whiteMove else 'b'

        for dir in dirs:
            end_row = r + dir[0]
            end_col = c + dir[1]

            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != allyColor:
                    moves.append(Move((r,c), (end_row, end_col), self.board))

    def get_castle_moves(self,r,c,moves):
        # cant castle if in check
        if self.sq_attacked(r,c):
            return
        if (self.whiteMove and self.currentCastlingRights.wks) or (not self.whiteMove and self.currentCastlingRights.bks):
            self.get_king_side_cm(r,c,moves)  

        if (self.whiteMove and self.currentCastlingRights.wqs) or (not self.whiteMove and self.currentCastlingRights.bqs):
            self.get_queen_side_cm(r,c,moves)  

    def get_king_side_cm(self,r,c,moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.sq_attacked(r, c+1) and not self.sq_attacked(r, c+2):
                moves.append(Move((r,c), (r, c+2), self.board, isCastleMove = True))

    def get_queen_side_cm(self,r,c,moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.sq_attacked(r, c-1) and not self.sq_attacked(r, c-2) and not self.sq_attacked(r, c-3):
                moves.append(Move((r,c), (r, c-2), self.board, isCastleMove = True))

    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    def get_bishop_moves(self, r, c, moves):
        dirs = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = 'b' if self.whiteMove else 'w'

        for dir in dirs:
            for i in range(1,8):
                end_row = r + dir[0]*i
                end_col = c + dir[1]*i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == '--':
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemyColor:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else: break

    def get_pawn_moves(self, r, c, moves):
        
        if self.whiteMove:
            if self.board[r-1][c] == '--':
                moves.append(Move((r,c), (r-1,c), self.board))
                if r == 6 and self.board[r-2][c] == '--':
                    moves.append(Move((r,c), (r-2,c), self.board))
            if c-1 >= 0:
                if self.board[r-1][c-1][0] == 'b':
                    moves.append(Move((r, c), (r-1,c-1), self.board))
                elif (r-1, c-1) == self.enpassantPoss:
                    moves.append(Move((r, c), (r-1,c-1), self.board, isEnpassantMove=True))
            if c+1 < 8:
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r,c), (r-1,c+1), self.board))
                elif (r-1, c+1) == self.enpassantPoss:
                    moves.append(Move((r, c), (r-1,c+1), self.board, isEnpassantMove=True))

        else:
            if self.board[r+1][c] == '--':
                moves.append(Move((r,c), (r+1,c), self.board))
                if r == 1 and self.board[r+2][c] == '--':
                    moves.append(Move((r,c), (r+2,c), self.board))
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r, c), (r+1,c-1), self.board))
                elif (r+1, c-1) == self.enpassantPoss:
                    moves.append(Move((r, c), (r+1,c-1), self.board, isEnpassantMove=True))
            if c+1 < 8:
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r,c), (r+1,c+1), self.board))
                elif (r+1, c+1) == self.enpassantPoss:
                    moves.append(Move((r, c), (r+1,c+1), self.board, isEnpassantMove=True))
    
    def get_rook_moves(self, r, c, moves):
        dirs = ((-1,0), (0,-1), (1,0), (0,1))
        enemyColor = 'b' if self.whiteMove else 'w'

        for dir in dirs:
            for i in range(1,8):
                end_row = r + dir[0]*i
                end_col = c + dir[1]*i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == '--':
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemyColor:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else: break

class CastleRights():

    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():

    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2,"7": 1,"8": 0}
    rows_to_ranks = {v : k for k, v in ranks_to_rows.items()}

    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5,"g": 6,"h": 7}
    cols_to_files = {v: k for k,v in files_to_cols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove = False, isCastleMove = False):
        self.startRow = startSq[0]  
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnProm = False
        # promotion
        self.isPawnProm = ((self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7))
        # enpasant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'    
        self.moveID = self.startRow * 1000 + self.startCol* 100 + self.endRow * 10 +self.endCol
        # castle move
        self.isCastleMove = isCastleMove

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
    

    def get_chess_notation(self):
        return self.get_rank_file(self.startRow, self.startCol) + self.get_rank_file(self.endRow, self.endCol)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]


# log of the game, valid moves

# class GameState():
#     def __init__(self):
#         self.board = [
#             ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
#             ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
#             ["--", "--", "--", "--", "--", "--", "--", "--"],
#             ["--", "--", "--", "--", "--", "--", "--", "--"],
#             ["--", "--", "--", "--", "--", "--", "--", "--"],
#             ["--", "--", "--", "--", "--", "--", "--", "--"],
#             ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
#             ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
#         ]

#         self.move_functions = {'p': self.get_pawn_moves, 'R': self.get_rook_moves, 'N':self.get_knight_moves, 'B':self.get_bishop_moves,
#                                'Q':self.get_queen_moves, 'K':self.get_king_moves}
#         self.whiteMove = True
#         self.moveLog = []
#         self.white_king_loc = (7,4)
#         self.black_king_loc = (0,4)
#         self.inCheck = False
#         self.pins = []
#         self.checks = []
#         self.checkmate = False
#         self.stalemate = False

#     def make_move(self, move):
#         self.board[move.endRow][move.endCol] = move.pieceMoved
#         self.board[move.startRow][move.startCol] = "--"
#         self.moveLog.append(move) #log of moves
#         self.whiteMove = not self.whiteMove #switch turns

#         if move.pieceMoved[1] == 'K':
#             if move.pieceMoved[0] == 'b':
#                 self.black_king_loc = (move.endRow, move.endCol)
#             if move.pieceMoved[0] == 'w':
#                 self.white_king_loc = (move.endRow, move.endCol)

#     def undo_move(self):
#         if len(self.moveLog) != 0:
#             move = self.moveLog.pop()
#             self.board[move.startRow][move.startCol] = move.pieceMoved
#             self.board[move.endRow][move.endCol] = move.pieceCaptured
#             self.whiteMove = not self.whiteMove  
#             if move.pieceMoved == 'wK':
#                 self.white_king_loc = (move.startRow, move.startCol)
#             elif move.pieceMoved == 'bK':
#                 self.black_king_loc = (move.startRow, move.startCol)

#     def valid_moves(self):
        
#         # 1. generate all moves
#         moves = []
#         self.in_check, self.pins, self.checks = self.check_pins_and_checks()
#         # print(self.in_check, self.pins, self.checks)
#         if self.whiteMove:
#             king_row = self.white_king_loc[0]
#             king_col = self.white_king_loc[1]
#         else:
#             king_row = self.black_king_loc[0]
#             king_col = self.black_king_loc[1]

#         if self.inCheck:
#             if len(self.checks) == 1:
#                 moves = self.get_all_possible_moves()
                
#                 check = self.checks[0]
#                 check_row = check[0]
#                 check_col = check[1]
#                 piece_checking = self.board[check_row][check_col]
#                 valid_squares = []

#                 if piece_checking[1] == 'N':
#                     valid_squares = [(check_row, check_col)]
#                 else:
#                     for i in range(1, 8):
#                         valid_square = (king_row + check[2] * i, king_col + check[3] * i)
#                         valid_squares.append(valid_square)
#                         if valid_square[0] == check_row and valid_square[1] == check_col:
#                             break

#                 for i in range(len(moves) -1, -1, -1):
#                     if moves[i].pieceMoved[1] != 'K':
#                         if not (moves[i].endRow, moves[i].endCol) in valid_squares:
#                             moves.remove(moves[i])
#             else: self.get_king_moves(king_row, king_col, moves)

#         else: moves = self.get_all_possible_moves()

#         return moves
    
#     def check_pins_and_checks(self):
#         pins = []
#         checks = []
#         in_check = False

#         if self.whiteMove:
#             enemy_color = 'b'
#             ally_color = 'w'
#             start_row = self.white_king_loc[0]
#             start_col = self.white_king_loc[1]
#         else:
#             enemy_color = 'w'
#             ally_color = 'b'
#             start_row = self.black_king_loc[0]
#             start_col = self.black_king_loc[1]

#         dirs = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
       
#         for j in range(len(dirs)):
#             print(j)

#             dir = dirs[j]
#             possible_pin = ()
#             print(dir)
#             for i in range(1, 8):
#                 end_row = start_row + dir[0] * i
#                 end_col = start_col + dir[1] * i
                
#                 if 0<= end_row < 8 and 0 <= end_col <8:
#                     end_piece = self.board[end_row][end_col]

#                     if end_piece[0] == ally_color and end_piece[1] != 'K':
#                         if possible_pin == ():
#                             possible_pin = (end_row, end_col, dir[0], dir[1])
#                         else:
#                             break
#                     elif end_piece[0] == enemy_color:
#                         type = end_piece[1]
#                         if (0 <= j <= 3 and type == 'R') or \
#                             (4 <= j <= 7 and type == 'B') or \
#                             (i == 1 and type == 'p' and ((enemy_color == 'w' and 6 <= j <= 7) or (enemy_color == 'b' and 4 <= j <=5 ))) or \
#                             (type == 'Q') or (i == 1 and type == 'K'):
#                             if possible_pin == ():
#                                 in_check = True
#                                 checks.append((end_row, end_col, dir[0], dir[1]))
#                                 break
#                             else:
#                                 pins.append(possible_pin)
#                                 print("AZ SUM 1")
#                                 break
#                         else:
#                             print("AZ SUM 2")
#                             break
#                 else:
#                     print(in_check)
#                     break
                
#                 knight_moves = ((2, 1),(2, -1),(-2, +1),(-2, -1),(+1, +2),(+1, -2),(-1, -2),(-1, +2))
#                 for m in knight_moves:
#                     end_row = start_row + m[0]
#                     end_col = start_col + m[1]
#                     if 0 <= end_row < 8 and 0 <= end_col < 8:
#                         end_piece = self.board[end_row][end_col]
#                         if end_piece[0] == enemy_color and end_piece[1] == 'N':
#                             in_check = True
#                             checks.append((end_row, end_col, m[0], m[1]))

#                 return in_check,pins,checks

#     def in_check(self):
#         if self.whiteMove:
#             return self.sq_attacked(self.white_king_loc[0],self.white_king_loc[1])
#         else:
#             return self.sq_attacked(self.black_king_loc[0],self.black_king_loc[1])

#     def sq_attacked(self, r, c):
#         self.whiteMove = not self.whiteMove
#         op_move = self.get_all_possible_moves()
#         self.whiteMove = not self.whiteMove

#         for move in op_move:
#             if move.endRow == r and move.endCol == c:
#                 return True
#         return False


#     # def validator(end_row, end_col):
#         return 0 <= end_row < 8 and 0 <= end_col < 8
    
#     def get_all_possible_moves(self):
#         moves = []
#         for r in range(len(self.board)):
#             for c in range(len(self.board[r])):
#                 turn = self.board[r][c][0]
#                 if (turn == 'w' and self.whiteMove) or (turn == 'b' and not self.whiteMove):
#                     piece = self.board[r][c][1]
#                     self.move_functions[piece](r,c,moves)

#         return moves
    
#     def get_knight_moves(self, r, c, moves):

#         piece_pinned = False

#         for i  in range(len(self.pins) -1, -1, -1):
#             if self.pins[i][0] == r and self.pins[i][1] == c:
#                 piece_pinned = True
#                 self.pins.remove(self.pins[i])
#                 break

#         dirs = ((2, 1),
#                 (2, -1),
#                 (-2, +1),
#                 (-2, -1),
#                 (+1, +2),
#                 (+1, -2),
#                 (-1, -2),
#                 (-1, +2))
#         same = 'w' if self.whiteMove else 'b'

#         for dir in dirs:
#             end_row = dir[0] + r
#             end_col = dir[1] + c
#             if 0 <= end_row < 8 and 0 <= end_col < 8:
#                 if not piece_pinned:
#                     end_piece = self.board[end_row][end_col]
#                     if end_piece[0] != same:
#                         moves.append(Move((r,c), (end_row, end_col), self.board))

#     def get_king_moves(self, r, c, moves):
#         # dirs = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
#         rowsM = (-1, -1, -1, 0,0,1,1,1)
#         colsM = (-1, 0, 1, -1 ,1,-1,0,1)
#         allyColor = 'w' if self.whiteMove else 'b'

#         for i in range(8):
#             end_row = r + rowsM[i]
#             end_col = c + colsM[i]

#             if 0 <= end_row < 8 and 0 <= end_col < 8:
#                 end_piece = self.board[end_row][end_col]
                
#                 if end_piece[0] != allyColor:

#                     if allyColor == 'w':
#                         self.white_king_loc = (end_row, end_col)
#                     else:
#                         self.black_king_loc = (end_row, end_col)
                        
#                     inCheck, pins, checks = self.check_pins_and_checks()
#                     if not inCheck:
#                         moves.append(Move((r,c), (end_row, end_col), self.board))
#                     if allyColor == 'w':
#                         self.white_king_loc = (r,c)
#                     else:
#                         self.black_king_loc = (r,c)

#     def get_queen_moves(self, r, c, moves):
#         self.get_rook_moves(r, c, moves)
#         self.get_bishop_moves(r, c, moves)

#     def get_bishop_moves(self, r, c, moves):

#         piece_pinned = False
#         pinDirection = ()

#         for i  in range(len(self.pins) -1, -1, -1):
#             if self.pins[i][0] == r and self.pins[i][1] == c:
#                 piece_pinned = True
#                 pinDirection = (self.pins[i][2], self.pins[i][3])    
#                 self.pins.remove(self.pins[i])
#                 break

#         dirs = ((-1, -1), (-1, 1), (1, -1), (1, 1))
#         enemyColor = 'b' if self.whiteMove else 'w'

#         for dir in dirs:
#             for i in range(1,8):
#                 end_row = r + dir[0]*i
#                 end_col = c + dir[1]*i
#                 if 0 <= end_row < 8 and 0 <= end_col < 8:
#                     if not piece_pinned or pinDirection == dir or pinDirection == (-dir[0], -dir[1]):
#                         end_piece = self.board[end_row][end_col]
#                         if end_piece == '--':
#                             moves.append(Move((r, c), (end_row, end_col), self.board))
#                         elif end_piece[0] == enemyColor:
#                             moves.append(Move((r, c), (end_row, end_col), self.board))
#                             break
#                         else:
#                             break
#                 else: break

#     def get_pawn_moves(self, r, c, moves):
        
#         piece_pinned = False
#         pinDirection = ()

#         for i  in range(len(self.pins) -1, -1, -1):
#             if self.pins[i][0] == r and self.pins[i][1] == c:
#                 piece_pinned = True
#                 pinDirection = (self.pins[i][2], self.pins[i][3])
#                 self.pins.remove(self.pins[i])
#                 break

#         if self.whiteMove:
#             if self.board[r-1][c] == '--':
#                 if not piece_pinned or pinDirection == (-1, 0):
#                     moves.append(Move((r,c), (r-1,c), self.board))
#                     if r == 6 and self.board[r-2][c] == '--':
#                         moves.append(Move((r,c), (r-2,c), self.board))
#             if c-1 >= 0:
#                 if self.board[r-1][c-1][0] == 'b':
#                     if not piece_pinned or pinDirection == (-1, -1):
#                         moves.append(Move((r, c), (r-1,c-1), self.board))
#             if c+1 < 8:
#                 if self.board[r-1][c+1][0] == 'b':
#                     if not piece_pinned or pinDirection == (-1, 1):
#                         moves.append(Move((r,c), (r-1,c+1), self.board))

#         else:
#             if self.board[r+1][c] == '--':
#                 if not piece_pinned or pinDirection == (1, 0):
#                     moves.append(Move((r,c), (r+1,c), self.board))
#                     if r == 1 and self.board[r+2][c] == '--':
#                         moves.append(Move((r,c), (r+2,c), self.board))
#             if c-1 >= 0:
#                 if self.board[r+1][c-1][0] == 'w':
#                     if not piece_pinned or pinDirection == (1, -1):
#                         moves.append(Move((r, c), (r+1,c-1), self.board))
#             if c+1 < 8:
#                 if self.board[r+1][c+1][0] == 'w':
#                     if not piece_pinned or pinDirection == (1, 1):
#                         moves.append(Move((r,c), (r+1,c+1), self.board))
    
#     def get_rook_moves(self, r, c, moves):

#         piece_pinned = False
#         pinDirection = ()

#         for i  in range(len(self.pins) -1, -1, -1):
#             if self.pins[i][0] == r and self.pins[i][1] == c:
#                 piece_pinned = True
#                 pinDirection = (self.pins[i][2], self.pins[i][3])
#                 if self.board[r][c][1] != 'Q':
#                     self.pins.remove(self.pins[i])
#                 break

#         dirs = ((-1,0), (0,-1), (1,0), (0,1))
#         enemyColor = 'b' if self.whiteMove else 'w'

#         for dir in dirs:
#             for i in range(1,8):
#                 end_row = r + dir[0]*i
#                 end_col = c + dir[1]*i
#                 if 0 <= end_row < 8 and 0 <= end_col < 8:
#                     if not piece_pinned or pinDirection == dir or pinDirection == (-dir[0], -dir[1]):
#                         end_piece = self.board[end_row][end_col]
#                         if end_piece == '--':
#                             moves.append(Move((r, c), (end_row, end_col), self.board))
#                         elif end_piece[0] == enemyColor:
#                             moves.append(Move((r, c), (end_row, end_col), self.board))
#                             break
#                         else:
#                             break
#                 else: break

# class Move():#

#     ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2,"7": 1,"8": 0}
#     rows_to_ranks = {v : k for k, v in ranks_to_rows.items()}

#     files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5,"g": 6,"h": 7}
#     cols_to_files = {v: k for k,v in files_to_cols.items()}

#     def __init__(self, startSq, endSq, board):
#         self.startRow = startSq[0]  
#         self.startCol = startSq[1]
#         self.endRow = endSq[0]
#         self.endCol = endSq[1]
#         self.pieceMoved = board[self.startRow][self.startCol]
#         self.pieceCaptured = board[self.endRow][self.endCol]
#         self.moveID = self.startRow * 1000 + self.startCol* 100 + self.endRow * 10 +self.endCol

#     def __eq__(self, other):
#         if isinstance(other, Move):
#             return self.moveID == other.moveID
#         return False
    

#     def get_chess_notation(self):
#         return self.get_rank_file(self.startRow, self.startCol) + self.get_rank_file(self.endRow, self.endCol)

#     def get_rank_file(self, r, c):
#         return self.cols_to_files[c] + self.rows_to_ranks[r]


