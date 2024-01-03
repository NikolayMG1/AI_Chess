import random

pieceScore = {'K': 0, 'Q': 9, 'R': 5, 'B': 3, 'N':3, 'p':1 }
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2
def find_randomMove(valid_moves):
    return valid_moves[random.randint(0 ,len(valid_moves)-1)]

def find_greedy_bestMove(gs, valid_moves):

    turnMultiplayer = 1 if gs.whiteMove else -1

    maxScore = -CHECKMATE 
    bestMove = None

    for playerMove in valid_moves:
        gs.make_move(playerMove)
        if gs.checkmate:
            score = CHECKMATE 
        elif gs.stalemate:
            score = 0
        else:
            score = score_material(gs.board) * turnMultiplayer
        if score > maxScore:
            maxScore =score 
            bestMove = playerMove
        gs.undo_move()
    return bestMove

def find_bestMove(gs, valid_moves):

    turnMultiplayer = 1 if gs.whiteMove else -1
    opponentMinMaxScore = CHECKMATE 
    bestPlayerMove = None
    random.shuffle(valid_moves)
    for playerMove in valid_moves:
        gs.make_move(playerMove)
        oppMpves = gs.valid_moves()
        if gs.stalemate:
            oppMaxScore = STALEMATE
        elif gs.checkmate:
            oppMaxScore = -CHECKMATE
        else:
            oppMaxScore = -CHECKMATE
            for oppMove in oppMpves:
                gs.make_move(oppMove)
                # gs.valid_moves()
                if gs.checkmate:
                    score = CHECKMATE 
                elif gs.stalemate:
                    score = 0
                else:
                    score = score_material(gs.board) * -turnMultiplayer
                if score > oppMaxScore:
                    oppMaxScore =score 

                gs.undo_move()
        if opponentMinMaxScore > oppMaxScore:
            opponentMinMaxScore = oppMaxScore
            bestPlayerMove = playerMove       
        gs.undo_move()
    return bestPlayerMove

def score_material(board):
    score = 0

    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    
    return score

def find_best_move_minMax(gs, valid_moves):
    global nextMove
    find_moveMinMax(gs, valid_moves, DEPTH, gs.whiteMove)
    return nextMove

def find_moveMinMax(gs, valid_moves, depth, whiteMove):

    global nextMove
    if depth == 0 or gs.checkmate or gs.stalemate:
        return score_material(gs.board)
    
    if whiteMove:
        maxScore = -CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.valid_moves()
            score = find_moveMinMax(gs, next_moves, depth-1,False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undo_move()

        return maxScore
    else:
        minScore = CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.valid_moves()
            score = find_moveMinMax(gs, next_moves, depth-1,True)
            if score < minScore:
                    minScore = score
                    if depth == DEPTH:
                        nextMove = move
            gs.undo_move()
        return minScore

def find_negaMax(gs, valid_moves, depth, turnMultiplayer):
    global nextMove
    if depth == 0:
        return turnMultiplayer * score_board(gs)
    
    maxScore = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move)
        nextMoves = gs.valid_moves()
        score = -find_negaMax(gs, nextMoves,depth-1, -turnMultiplayer)
        if score > maxScore:
            maxScore =  score
            if depth == DEPTH:
                nextMove = move
        gs.undo_move()
    return maxScore

def find_best_move_negaMax(gs, valid_moves):

    global nextMove
    nextMove = None
    random.shuffle(valid_moves)
    find_moveMinMax(gs, valid_moves, DEPTH, 1 if gs.whiteMove else -1)
    return nextMove

def find_negaMaxAlphaBetaP(gs, valid_moves, depth,alpha, beta, turnMultiplayer):
    global nextMove
    if depth == 0:
        return turnMultiplayer * score_board(gs)
    
    maxScore = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move)
        nextMoves = gs.valid_moves()
        score = -find_negaMaxAlphaBetaP(gs, nextMoves,depth-1,-beta, -alpha, -turnMultiplayer)
        if score > maxScore:
            maxScore =  score
            if depth == DEPTH:
                nextMove = move
        gs.undo_move()
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break

    return maxScore

def find_bestMove_abp(gs, valid_moves):
    global nextMove
    nextMove = None
    random.shuffle(valid_moves)
    find_negaMaxAlphaBetaP(gs, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteMove else -1)
    return nextMove

def score_board(gs):



    if gs.checkmate:
        if gs.whiteMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE
    
    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    
    return score