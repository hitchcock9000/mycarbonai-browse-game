# audio.py
"""
Procedural Atmospheric Audio Synthesizer for climate-tech soundscapes.
Generates sound waves dynamically in memory without external audio file dependencies.
"""

import math
import array
import pygame

class AudioSystem:
    def __init__(self):
        self.enabled = False
        self.sounds = {}
        self.ambient_channel = None

    def init_mixer(self):
        """Initialize the mixer and pre-synthesize sounds."""
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.enabled = True
            
            # Synthesize core climate soundscape
            self.sounds['jump'] = self.synthesize_slide(300, 800, 0.12, 0.12, "triangle")
            self.sounds['scan_start'] = self.synthesize_tone(150, 0.4, 0.22, "sine")
            self.sounds['scan_active'] = self.synthesize_tone(80, 0.2, 0.15, "sine")
            self.sounds['sync_connect'] = self.synthesize_arpeggio([261.63, 329.63, 392.00, 523.25], 0.45, 0.18, "sine") # C Maj arpeggio
            self.sounds['damage'] = self.synthesize_slide(180, 60, 0.22, 0.35, "square")
            self.sounds['collect'] = self.synthesize_arpeggio([523.25, 659.25, 783.99], 0.2, 0.14, "triangle")
            self.sounds['ambient'] = self.synthesize_ambient_pad([65.41, 98.00, 130.81, 164.81], 6.0, 0.08) # Low Cmaj7 drone
            
            # Setup ambient looping
            self.ambient_channel = pygame.mixer.Channel(0)
        except Exception as e:
            print(f"Failed to initialize audio system: {e}. Running in silent mode.")
            self.enabled = False

    def synthesize_tone(self, freq, duration, volume=0.5, wave_type="sine"):
        """Generate a single clean tone."""
        if not self.enabled:
            return None
        
        sample_rate = 22050
        num_samples = int(sample_rate * duration)
        buf = array.array('h', [0] * num_samples)
        
        for i in range(num_samples):
            t = i / sample_rate
            # Fade out envelope
            env = 1.0 - (i / num_samples)
            
            if wave_type == "sine":
                val = math.sin(2 * math.pi * freq * t)
            elif wave_type == "square":
                val = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
            elif wave_type == "triangle":
                val = 2.0 * abs(2.0 * (t * freq - math.floor(t * freq + 0.5))) - 1.0
            else:
                val = math.sin(2 * math.pi * freq * t)
                
            buf[i] = int(val * volume * env * 32767)
            
        return pygame.mixer.Sound(buffer=buf)

    def synthesize_slide(self, start_freq, end_freq, duration, volume=0.5, wave_type="sine"):
        """Generate a sliding frequency sound (e.g. jump or damage)."""
        if not self.enabled:
            return None
            
        sample_rate = 22050
        num_samples = int(sample_rate * duration)
        buf = array.array('h', [0] * num_samples)
        
        for i in range(num_samples):
            t = i / sample_rate
            # Fade out envelope
            env = 1.0 - (i / num_samples)
            # Linear frequency interpolation
            freq = start_freq + (end_freq - start_freq) * (i / num_samples)
            
            if wave_type == "sine":
                val = math.sin(2 * math.pi * freq * t)
            elif wave_type == "square":
                val = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
            elif wave_type == "triangle":
                val = 2.0 * abs(2.0 * (t * freq - math.floor(t * freq + 0.5))) - 1.0
            else:
                val = math.sin(2 * math.pi * freq * t)
                
            buf[i] = int(val * volume * env * 32767)
            
        return pygame.mixer.Sound(buffer=buf)

    def synthesize_arpeggio(self, freqs, duration, volume=0.5, wave_type="sine"):
        """Generate a sequential arpeggio of tones."""
        if not self.enabled:
            return None
            
        sample_rate = 22050
        num_samples = int(sample_rate * duration)
        buf = array.array('h', [0] * num_samples)
        num_notes = len(freqs)
        samples_per_note = num_samples // num_notes
        
        for idx, freq in enumerate(freqs):
            for i in range(samples_per_note):
                sample_idx = idx * samples_per_note + i
                t = i / sample_rate
                # Note decay envelope
                env = 1.0 - (i / samples_per_note)
                
                if wave_type == "sine":
                    val = math.sin(2 * math.pi * freq * t)
                elif wave_type == "triangle":
                    val = 2.0 * abs(2.0 * (t * freq - math.floor(t * freq + 0.5))) - 1.0
                else:
                    val = math.sin(2 * math.pi * freq * t)
                    
                buf[sample_idx] = int(val * volume * env * 32767)
                
        return pygame.mixer.Sound(buffer=buf)

    def synthesize_ambient_pad(self, freqs, duration, volume=0.1):
        """Generate a lush, multi-harmonic low frequency drone for atmospheric backdrop."""
        if not self.enabled:
            return None
            
        sample_rate = 22050
        num_samples = int(sample_rate * duration)
        buf = array.array('h', [0] * num_samples)
        
        for i in range(num_samples):
            t = i / sample_rate
            
            # Soft attack and decay envelope to prevent popping
            if i < sample_rate * 0.5: # 0.5s attack
                env = i / (sample_rate * 0.5)
            elif i > num_samples - sample_rate * 0.5: # 0.5s decay
                env = (num_samples - i) / (sample_rate * 0.5)
            else:
                env = 1.0
                
            val = 0
            # Blend all frequencies
            for f in freqs:
                val += math.sin(2 * math.pi * f * t) + 0.5 * math.sin(2 * math.pi * (f * 1.5) * t) # Root + fifths
                
            val = val / (len(freqs) * 1.5)
            buf[i] = int(val * volume * env * 32767)
            
        return pygame.mixer.Sound(buffer=buf)

    def play(self, name):
        """Play a pre-synthesized sound effect."""
        if self.enabled and name in self.sounds:
            self.sounds[name].play()

    def start_ambient(self):
        """Start the continuous solarpunk ambient loop."""
        if self.enabled and 'ambient' in self.sounds and self.ambient_channel:
            self.ambient_channel.play(self.sounds['ambient'], loops=-1)

    def stop_ambient(self):
        """Stop ambient music."""
        if self.enabled and self.ambient_channel:
            self.ambient_channel.stop()

# Global static instance
audio_system = AudioSystem()
