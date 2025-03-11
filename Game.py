import pygame

#Begin of initialization
pygame.init()
pygame.font.init()
#End of initialization

#Begin of constant variables declaration
GREY = (150, 150, 150)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

font = pygame.font.SysFont("comic sans ms", 40)

clock = pygame.time.Clock()
#End of constant variables declaration

screen = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("meo meo")

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
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
            pygame.draw.circle(screen, WHITE, (i, j), 45)
            
    text1 = font.render("NEW", True, BLACK)  
    text1_rect = text1.get_rect(center=rect1.center)  
    screen.blit(text1, text1_rect) 
    
    text2 = font.render("BACK", True, BLACK)
    text2_rect = text2.get_rect(center=rect2.center)
    screen.blit(text2, text2_rect)
    
    pygame.display.flip()
    clock.tick(120)
    
pygame.quit()