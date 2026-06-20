from TikTokLive import TikTokLiveClient
from TikTokLive.events import GiftEvent, ConnectEvent
import pygame
import sys
import math
import threading
import os

# ===== CONFIG =====
USERNAME = "@darkfrenchvibes"  # @
WIDTH, HEIGHT = 800, 600
FPS = 60
# ==================

class KingOfTheHill:
    def __init__(self):
        pygame.init()
        pygame.mixer.init() # Sound play කරන්න mixer එක on කරනවා
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("King of the Hill - WE ARE IN CONTROL")
        self.clock = pygame.time.Clock()
        
        self.font_big = pygame.font.Font(None, 72)
        self.font_mid = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        
        # Game State
        self.king_name = "No King Yet"
        self.king_gift_count = 0
        self.total_gifts = 0
        self.pulse = 0
        self.flash_alpha = 0  # Screen flash effect එකට
        
        # Sounds Load කිරීම
        try:
            # ඔයාගේ folder එකේ මේ නම් වලින් sounds තියාගන්න (wav හෝ ogg format එකෙන්)
            self.sound_new_king = pygame.mixer.Sound("new_king.wav") 
            self.sound_gift = pygame.mixer.Sound("gift.wav")
        except Exception as e:
            print("⚠️ Sound files ('new_king.wav', 'gift.wav') හොයාගන්න බෑ. Sounds නැතුව run වෙනවා.")
            self.sound_new_king = None
            self.sound_gift = None
        
    def play_sound(self, sound_obj):
        if sound_obj:
            sound_obj.play()

    def update_king(self, username, amount):
        if self.king_name != username:
            # අලුත් රජෙක් ආවම - Hype එක වැඩි කරනවා!
            self.king_gift_count = amount
            self.play_sound(self.sound_new_king) # අලුත් රජාගේ සද්දෙ
            self.flash_alpha = 255 # Screen එක සුදු පාටින් flash වෙනවා
        else:
            # දැනට ඉන්න රජාම තව roses එව්වම
            self.king_gift_count += amount
            self.play_sound(self.sound_gift)
            
        self.king_name = username
        self.total_gifts += amount
        print(f"👑 KING: {username} | King's Total: {self.king_gift_count} | All Gifts: {self.total_gifts}")
        
    def draw_crown(self, x, y, size):
        points = [
            (x, y + size),
            (x - size, y),
            (x - size//2, y + size//2),
            (x, y - size//3),
            (x + size//2, y + size//2),
            (x + size, y),
            (x, y + size)
        ]
        pygame.draw.polygon(self.screen, (255, 215, 0), points)
        pygame.draw.polygon(self.screen, (255, 255, 255), points, 3)
        
    def draw(self):
        self.screen.fill((10, 10, 30))
        self.pulse += 0.1
        
        # Titles and Texts
        title = self.font_big.render("KING OF THE HILL", True, (255, 255, 255))
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 40))
        
        crown_size = 60 + math.sin(self.pulse) * 10
        self.draw_crown(WIDTH//2, 200, int(crown_size))
        
        king_text = self.font_mid.render(self.king_name, True, (255, 215, 0))
        self.screen.blit(king_text, (WIDTH//2 - king_text.get_width()//2, 300))
        
        stats = f"King's Gifts: {self.king_gift_count}"
        stats_text = self.font_small.render(stats, True, (200, 200, 200))
        self.screen.blit(stats_text, (WIDTH//2 - stats_text.get_width()//2, 370))
        
        total = f"Total Gifts: {self.total_gifts}"
        total_text = self.font_small.render(total, True, (200, 200, 200))
        self.screen.blit(total_text, (WIDTH//2 - total_text.get_width()//2, 410))
        
        rule1 = self.font_small.render("Send a ROSE to become KING!", True, (0, 255, 100))
        self.screen.blit(rule1, (WIDTH//2 - rule1.get_width()//2, 500))
        
        rule2 = self.font_small.render("1 Coin = 1 Crown", True, (150, 150, 150))
        self.screen.blit(rule2, (WIDTH//2 - rule2.get_width()//2, 540))
        
        # Flash Effect එක (අලුත් රජෙක් ආවම සුදු පාටින් පත්තු වෙන්න)
        if self.flash_alpha > 0:
            flash_surface = pygame.Surface((WIDTH, HEIGHT))
            flash_surface.fill((255, 255, 255))
            flash_surface.set_alpha(self.flash_alpha)
            self.screen.blit(flash_surface, (0, 0))
            # Alpha එක අඩු කරලා flash එක හිමින් නැති කරනවා
            self.flash_alpha = max(0, self.flash_alpha - 15)
            
        pygame.display.flip()
        
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

# ===== TIKTOK BOT =====
game = KingOfTheHill()
client = TikTokLiveClient(unique_id=USERNAME)

@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    print(f"✅ Connected to @{event.unique_id} | Room ID: {client.room_id}")
    print("👑 King of the Hill Started. Waiting for Roses...")

@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    gift_amount = event.gift.count
    
    if event.gift.name.lower() == "rose":
        game.update_king(event.user.nickname, gift_amount)
    else:
        # වෙනත් Gifts වලට (Roses නෙවෙයි නම්)
        game.total_gifts += gift_amount
        game.play_sound(game.sound_gift) # පොඩි gift sound එකක්
        print(f"💰 {event.user.nickname} sent {event.gift.name} x{gift_amount} | Total: {game.total_gifts}")

def run_tiktok_client():
    client.run()

if __name__ == "__main__":
    tiktok_thread = threading.Thread(target=run_tiktok_client, daemon=True)
    tiktok_thread.start()
    game.run()
        # Crown එක Draw කරනවා
        points = [
            (x, y + size),
            (x - size, y),
            (x - size//2, y + size//2),
            (x, y - size//3),
            (x + size//2, y + size//2),
            (x + size, y),
            (x, y + size)
        ]
        pygame.draw.polygon(self.screen, (255, 215, 0), points) # Gold Color
        pygame.draw.polygon(self.screen, (255, 255, 255), points, 3)
        
    def draw(self):
        self.screen.fill((10, 10, 30)) # Dark Blue BG
        self.pulse += 0.1
        
        # Title
        title = self.font_big.render("KING OF THE HILL", True, (255, 255, 255))
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 40))
        
        # Crown Animation
        crown_size = 60 + math.sin(self.pulse) * 10
        self.draw_crown(WIDTH//2, 200, int(crown_size))
        
        # King Name
        king_text = self.font_mid.render(self.king_name, True, (255, 215, 0))
        self.screen.blit(king_text, (WIDTH//2 - king_text.get_width()//2, 300))
        
        # King Stats
        stats = f"King's Gifts: {self.king_gift_count}"
        stats_text = self.font_small.render(stats, True, (200, 200, 200))
        self.screen.blit(stats_text, (WIDTH//2 - stats_text.get_width()//2, 370))
        
        # Total Gifts
        total = f"Total Gifts: {self.total_gifts}"
        total_text = self.font_small.render(total, True, (200, 200, 200))
        self.screen.blit(total_text, (WIDTH//2 - total_text.get_width()//2, 410))
        
        # Rules
        rule1 = self.font_small.render("Send a ROSE to become KING!", True, (0, 255, 100))
        self.screen.blit(rule1, (WIDTH//2 - rule1.get_width()//2, 500))
        
        rule2 = self.font_small.render("1 Coin = 1 Crown", True, (150, 150, 150))
        self.screen.blit(rule2, (WIDTH//2 - rule2.get_width()//2, 540))
        
        pygame.display.flip()
        
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

# ===== TIKTOK BOT =====
game = KingOfTheHill()
client = TikTokLiveClient(unique_id=USERNAME)

@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    print(f"✅ Connected to @{event.unique_id} | Room ID: {client.room_id}")
    print("👑 King of the Hill Started. Waiting for Roses...")

@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    # Rose එකක් ආවොත් විතරක් King මාරු කරනවා
    if event.gift.name.lower() == "rose":
        game.update_king(event.user.nickname)
    else:
        # වෙන Gift එකක් නම් Total එක විතරක් වැඩි කරනවා
        game.total_gifts += 1
        print(f"💰 {event.user.nickname} sent {event.gift.name} | Total: {game.total_gifts}")

# Run both Pygame and TikTok Client
if __name__ == "__main__":
    import threading
    # Pygame වෙන Thread එකක Run කරනවා
    pygame_thread = threading.Thread(target=game.run)
    pygame_thread.start()
    
    # TikTok Client එක Main Thread එකේ
    client.run()
