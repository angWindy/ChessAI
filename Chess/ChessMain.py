'''
this is our main drive file. it will be responsible for handling user input and displaying the current gamestate object
'''

import pygame as  p
import ChessEngine

WIDTH = HEIGHT = 512
DIMENSION = 8 #chiều của bàn cờ là 8x8
SQ_SIZE = HEIGHT//DIMENSION # kich cỡ của một ô vuông trong bàn cờ
MAX_FPS = 15 # cho animation
IMAGES = {}

'''
khởi tạo một từ điển hình ảnh toàn cục. sẽ được gọi một lần duy nhât trong main
'''

def loadImages():
    pieces = ["wp","wR","wN","wB","wQ","wK","bp","bR","bN","bB","bQ","bK"]
    for pi in pieces:
        # hàm p.transform.scale để scale lại tỉ lệ của hình ảnh sao cho khớp với ô vuông trong bàn cờ 
        IMAGES[pi] = p.transform.scale(p.image.load("images/" + pi + ".png"), (SQ_SIZE, SQ_SIZE))
    # giờ chúng ta có thể dẫn tới hình ảnh bằng cách gọi : "IMAGES['wp']"

'''
phần chính của code. đoạn này sẽ kiểm soát đầu vào của người dùng và cập nhập đồ hoạ
'''

def main():
    p.init()
    screen = p.display.set_mode((WIDTH,HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    # khởi tạo một game state ban đầu
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False # một biến cờ khi mà một nước đi được tạo ra
    animate = False # một biến để ktra xem khi nào nên tạo hoạt ảnh cho nước đi
    loadImages()
    running = True
    sqSelected = () # ko có hình vuông nào được chọn, theo dõi lần click chuột cuối cùng của user ( tuple : (row, col))
    playerClicks = [] # keep track of player clicks (two tuple [(6,4), (4,4)])
    gameOver = False
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos() # trả về một cặp toạ độ x y 
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row, col): # hành động chọn 2 lần vào một ô vuông
                        # hoàn tác lại các giá trị
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2: # sau 2 lan click chuot
                        move = ChessEngine.Move(playerClicks[0],playerClicks[1],gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
                    
            
            #key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: # undo
                    gs.undoMove()
                    moveMade = True
                    animate = False
                if e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1],screen,gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
                
        drawGameState(screen, gs, validMoves, sqSelected)    

        if gs.checkMate:
            gameOver = True    
            if gs.whiteToMove:
                drawText(screen, ' Black wins by checkmate')
            else:
                drawText(screen, ' White wins by checkmate')
        elif gs.staleMate:
            gameOver = True
            drawText(screen, 'Stalemate')

        clock.tick(MAX_FPS)
        p.display.flip()

"""
chịu trách nhiệm vẽ các quân cờ của trạng thái hiện tại
"""

def highlightSquares(screen, gs,validMoves,sqSelected):
    if sqSelected !=():
        r,c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):  #sqSelected là một quân cờ có thể di chuyển đc
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) # mức độ trong suốt : = 0: trong suốt hoàn toàn, = 255 : đục ngầu
            s.fill(p.Color('blue'))
            screen.blit(s,(c*SQ_SIZE, r*SQ_SIZE))
            s.fill(p.Color('yellow'))
            # làm nổi bật các ô mà quân cờ có thể di chuyển đến
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s,(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))


def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPiece(screen,gs.board)

# làm nổ bật ô vuông được chọn và các ô có thể di chuyển được


"""
vẽ các hình vuông trên bàn cờ
"""
def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r+c)%2]
            p.draw.rect(screen,color,p.Rect(c*SQ_SIZE,r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

# vẽ các quân cờ trên bàn cờ sử dụnng GameState.board khởi đầu
def drawPiece(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

# tạo ra hiệu ứng cho nước đi
def animateMove(move,screen, board, clock):
    global colors
    coords = [] # danh sách các toạ độ mà hoạt ảnh sẽ di chuyển qua
    dR = move.endRow - move.startRow
    dC = move.endCol  - move.startCol

    framesPerSquare = 10 # số khung hình mà ô vuong di chuyển ( kiểu như tốc độ nhanh hay chậm)
    frameCount = (abs(dR)+ abs(dC)) * framesPerSquare
    for frame in range (frameCount + 1):
        r,c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPiece(screen,board)

        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)

        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE,SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text,0, p.Color('Black'))
    textLocation = p.Rect(0,0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject,textLocation)
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2,2))

if __name__ == "__main__":
    main()        