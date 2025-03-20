import pygame
import math
import Board

#Begin of initialization
pygame.init()
pygame.font.init()
#End of initialization

#Begin of constant variables declaration
GREY = (150, 150, 150)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
VIOLET = (238,130,238)
NAVY = (0,0,128)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

font = pygame.font.SysFont("comic sans ms", 40)
clock = pygame.time.Clock()

screen = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("meo meo")
#End of constant variables declaration

gameState = True

coordinates = []

board = Board.Board()

win_flag = False

def draw_background():
    screen.fill(GREY)
    
    rect1 = pygame.Rect(50, 100, 200, 50)
    
    pygame.draw.rect(screen, WHITE, rect1)
    
    rect2 = pygame.Rect(50, 180, 200, 50)
    pygame.draw.rect(screen, WHITE, rect2)
    
    for i in range (0, 601, 100):
        pygame.draw.line(screen, WHITE, (300, i), (1000, i), 3)
    for i in range (300, 1001, 100):
        pygame.draw.line(screen, WHITE, (i, 0), (i, 600), 3)

    for i in range (350, 951, 100):
        for j in range (50, 551, 100):
            if i - 50 <= mouseX <= i + 50 and j - 50 <= mouseY <= j + 50:
                pygame.draw.circle(screen, BLACK, (i, j), 45)
            else:
                pygame.draw.circle(screen, WHITE, (i, j), 45)

    for i in range(len(coordinates)):
        (y, x) = coordinates[i]
        color = VIOLET if i % 2 == 0 else NAVY
        pygame.draw.circle(screen, color, (350 + x * 100, 50 + y * 100), 45)

    text1 = font.render("NEW", True, BLACK)  
    text1_rect = text1.get_rect(center=rect1.center)  
    screen.blit(text1, text1_rect) 
    
    text2 = font.render("BACK", True, BLACK)
    text2_rect = text2.get_rect(center=rect2.center)
    screen.blit(text2, text2_rect)

while gameState:
    mouseX = pygame.mouse.get_pos()[0]
    mouseY = pygame.mouse.get_pos()[1]
    isMoved = False 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameState = False
            exit()

        if event.type == pygame.MOUSEBUTTONUP:
            if pygame.Rect(50, 100, 200, 50).collidepoint(event.pos):  # reset game
                board = Board.Board()  
                coordinates = [] 
                win_flag = False 
                draw_background()
                pygame.display.flip() 

            x = math.floor((mouseX - 300) / 100)
            y = board.play(x)

            if y == -1:
                continue

            x, y = y, x
            coordinates.append((x, y))
            isMoved = True
                
            # check win
            if board.isWinningMove():
                print(f"{board.current_player ^ 1} WIN!")
                win_flag = True
                board.printBoard()
    
    draw_background()

    if(win_flag):
        win_block = pygame.Rect(20, 300, 250, 100)
        pygame.draw.rect(screen, YELLOW, win_block)
        win_text = font.render("Player "+str((board.current_player ^ 1) + 1)+" win!", True, RED)
        win_rect = win_text.get_rect(center=win_block.center)
        screen.blit(win_text, win_rect)
        pygame.display.update()
                    
    pygame.display.flip()
    clock.tick(120)
    
pygame.quit()