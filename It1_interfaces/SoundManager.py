import pygame
from It1_interfaces.EventTypes import MOVE_DONE, PIECE_CAPTURED, GAME_ENDED, GAME_STARTED

class SoundManager:
    def __init__(self):
        try:
            pygame.mixer.init()
            self.sounds_enabled = True
            self.sounds = {
                MOVE_DONE: "sounds/5movement0.wav",
                PIECE_CAPTURED: "sounds/gan.wav",
                GAME_ENDED: "sounds/applause.mp3",
                GAME_STARTED: "sounds/1TADA.WAV"
            }
        except Exception as e:
            print(f"[DEBUG] Sound system disabled due to error: {e}")
            self.sounds_enabled = False
            self.sounds = {}

    def update(self, event_type, data):
        if not self.sounds_enabled:
            return
            
        sound_file = self.sounds.get(event_type)
        if sound_file:
            try:
                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.play()
            except Exception:
                pass
        else:
            pass
