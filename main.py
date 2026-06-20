from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, CommentEvent, GiftEvent
import pygame
import threading
import asyncio
import sys

# ---------------------------------------------------------
# 1. Game Variables & State
# ---------------------------------------------------------
brain_power = 0
brain_state = "sleeping" # sleeping, charging, fear, unlocked
lock = threading.Lock()

# ---------------------------------------------------------
# 2. TikTok Connect
# ---------------------------------------------------------
client = TikTokLiveClient(unique_id="@darkfrenchvibes")

@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    print(f"Connected to Room ID: {client.room_id}")

@client.on(CommentEvent)
async def on_comment(event: CommentEvent):
    global brain_power, brain_state
    
    cmd = event.comment.lower().strip()
    
    with lock:
        if cmd == "power":
            brain_power += 10
            brain_state = "charging"
            print(f"⚡ {event.user.nickname} දුන්නා Power! Total: {brain_power}%")
            
        elif cmd == "fear":
            brain_power -= 15
            brain_state = "fear"
            if brain_power < 0: 
                brain_power = 0
            print(f"💀 {event.user.nickname} triggered Fear! Total: {brain_power}%")
            
        if brain_power >= 100:
            brain_state = "unlocked"
            brain_power = 100
            print("🧠 BRAIN UNLOCKED! WE ARE IN CONTROL!")

@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    global brain_power
    
    with lock:
        # Check if the gift is a Rose
        if event.gift.name == "Rose":
            brain_power += 50
            if brain_power > 100: 
                brain_power = 100
            print(f"🌹 {event.user.nickname} දුන්නා Divine Energy! (Rose)")

# Thread runner for TikTok to ensure asyncio loop works properly
def run_tiktok():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    client.run()

# ---------------------------------------------------------
# 3. Pygame Window - Brain Visual
# ---------------------------------------------------------
def run_game():
    global brain_power, brain_state
    
    pygame.init()
    # TikTok Vertical Resolution
    screen = pygame.display.set_mode((1080, 1920)) 
    pygame.display.set_caption("TikTok Live - Brain Control")
    clock = pygame.time.Clock()
    
    # Fallback font in case 'Noto Sans Sinhala' isn't installed
    try:
        font = pygame.font.SysFont('Noto Sans Sinhala', 60)
    except:
        font = pygame.font.Font(None, 60) 
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Safely grab current variables
        with lock:
            current_power = brain_power
            current_state = brain_state
        
        # Background Color based on state
        if current_state == "fear":
            screen.fill((50, 0, 0))       # Dark Red
        elif current_state == "charging":
            screen.fill((0, 0, 50))       # Dark Blue
        elif current_state == "unlocked":
            screen.fill((50, 50, 0))      # Gold
        else:
            screen.fill((10, 10, 10))     # Black (Sleeping)
        
        # Draw Background for Power Bar
        pygame.draw.rect(screen, (50, 50, 50), (140, 1600, 800, 50), border_radius=10)
        
        # Draw Current Power Bar (with smooth boundaries)
        bar_width = int(800 * (current_power / 100))
        if bar_width > 0:
            pygame.draw.rect(screen, (0, 255, 255), (140, 1600, bar_width, 50), border_radius=10)
        
        # Render Text
        text1 = font.render(f"Power: {current_power}%", True, (255, 255, 255))
        text2 = font.render(f"State: {current_state.upper()}", True, (255, 255, 255))
        text3 = font.render("Type 'POWER' or 'FEAR'", True, (200, 200, 200))
        
        screen.blit(text1, (140, 1400))
        screen.blit(text2, (140, 1480))
        screen.blit(text3, (140, 1700))
        
        pygame.display.flip()
        clock.tick(60) # 60 FPS
    
    # Graceful exit
    print("Shutting down...")
    pygame.quit()
    sys.exit()

# ---------------------------------------------------------
# 4. Run Both Together
# ---------------------------------------------------------
if __name__ == "__main__":
    # Start TikTok client in background thread
    tiktok_thread = threading.Thread(target=run_tiktok, daemon=True)
    tiktok_thread.start()
    
    # Start Pygame loop on main thread
    run_game()
