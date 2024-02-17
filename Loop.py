import pygame as p
import ChessEngine, ChessAI
from Const import *

import tkinter as tk
root = tk.Tk()
root.title("Chess")
root.geometry("1400x600")
photo = tk.PhotoImage(file="assets\images\ezgif-2-23f9e634b0.png")
label = tk.Label(root, image=photo)
label.pack()
IMAGES = {}
f = open("demofile3.txt", "w")

def load_images() -> None: 
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bp", "wp", "wR", "wN", "wB", "wQ", "wK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("assets/images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

def main_loop():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    valid_moves = gs.valid_moves()
    
    moveMade = False
    load_images()
    running = True

    square_selected = () #lack click of the player
    player_clicks = [] #keep track of player clicks
    gameOver = False
    player1 = True #true if human else ai
    player2 = False
    # integer for ai diff, later

    while running:
        humanTurn = (gs.whiteMove and player1) or (not gs.whiteMove and player2)


        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
                f.close() 
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos() #x,y mouse location    
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE

                    if square_selected == (row, col): #repeated clicks
                        square_selected = ()
                        player_clicks = []
                    else:
                        square_selected = (row, col)
                        player_clicks.append(square_selected)
                    if len(player_clicks) == 2:
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:    
                                gs.make_move(valid_moves[i])
                                f.write(f"{move.pieceMoved} {move.endRow} {move.endCol}\n")
                                moveMade = True
                                square_selected = () # reset user clicks
                                player_clicks = []
                                
                        if not moveMade:
                            player_clicks = [square_selected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #call undo when z is pressed
                    gs.undo_move()
                    moveMade = True
                    gameOver = False
                if e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    valid_moves = gs.valid_moves()
                    square_selected = ()
                    player_clicks = []
                    moveMade = False
                    gameOver = False

        # AI Move finder
        if not gameOver and not humanTurn:
            AIMove = ChessAI.find_bestMove_abp(gs, valid_moves)
            # if AIMove is None:
            #     AIMove = ChessAI.find_randomMove(valid_moves)
            gs.make_move(AIMove)
            f.write(f"{AIMove.pieceMoved} {AIMove.endRow} {AIMove.endCol}\n")
            moveMade = True

        if moveMade:
            valid_moves = gs.valid_moves()
            moveMade = False

        draw_game_state(screen,gs, valid_moves, square_selected)
        if gs.checkmate:
            gameOver = True
            if gs.whiteMove:
                finisher(screen, "You lost")
                # label.mainloop()
            else:
                finisher(screen, "You won")
                # label.mainloop()
                
        elif gs.stalemate:
            gameOver = True
            finisher(screen, "Stalemate")

        clock.tick(MAX_FPS)
        p.display.flip()
       
def draw_game_state(screen, gs, valid_moves, sq_attacked) -> None:
    draw_board(screen)
    cur_sq(screen, gs, valid_moves, sq_attacked)
    draw_pieces(screen, gs.board)

def cur_sq(screen, gs, valid_moves, square_selected) -> None:

    if square_selected != ():  
        r, c = square_selected
        if gs.board[r][c][0] == ('w' if gs.whiteMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('red'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            s.fill(p.Color('blue'))

            for move in valid_moves:
                if move.startRow == r and move.startCol == c:
                        screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))

def finisher(screen, text) -> None:
    font = p.font.SysFont("Times New Roman", 32, True, False)
    textObject = font.render(text, 0, p.Color('Black'))
    textLocation = p.Rect(0,0,WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT /2- textObject.get_height()/2)
    screen.blit(textObject, textLocation)

def draw_board(screen) -> None:

    for r in range(DIMENSION):
        for c in range(DIMENSION):
            if (r + c) % 2 == 0:
                    color = (234, 235, 200)
            else:
                color = (119, 154, 88)
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))  
    
def draw_pieces(screen, board) -> None:
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            # print(piece)
            if piece != '--':
                # print(piece)
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
