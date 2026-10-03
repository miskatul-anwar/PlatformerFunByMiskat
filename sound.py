import math
import struct
import pygame

class SoundManager:
    _instance = None

    def __init__(self):
        self.enabled = True
        self.music_enabled = True
        self.sfx_volume = 0.6
        self.music_volume = 0.4
        self.sounds = {}
        self.bgm_sound = None
        self.bgm_channel = None
        self.initialized = False

        self._init_audio()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = SoundManager()
        return cls._instance

    def _init_audio(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.freq, _, _ = pygame.mixer.get_init()
            self._generate_sfx()
            self._generate_bgm()
            self.initialized = True
        except Exception as e:
            print(f"Audio init warning: {e}. Running in silent mode.")
            self.initialized = False

    def _pack_stereo(self, sample_val):
        sample_val = max(-32768, min(32767, int(sample_val)))
        return struct.pack('<hh', sample_val, sample_val)

    def _create_sound(self, generator, duration, volume=0.5):
        if not pygame.mixer.get_init():
            return None
        n_samples = int(self.freq * duration)
        buf = bytearray()
        for i in range(n_samples):
            t = i / self.freq
            progress = i / n_samples
            val = generator(t, progress) * volume * 32767.0
            buf.extend(self._pack_stereo(val))
        return pygame.mixer.Sound(buffer=bytes(buf))

    def _generate_sfx(self):
        # Jump SFX: fast pitch slide up
        def sfx_jump(t, p):
            f = 180 + 520 * (p ** 0.6)
            env = max(0.0, 1.0 - p)
            return (1.0 if math.sin(2.0 * math.pi * f * t) > 0 else -1.0) * env * 0.35

        # Double Jump SFX: higher sweep
        def sfx_double_jump(t, p):
            f = 350 + 650 * (p ** 0.5)
            env = max(0.0, 1.0 - p)
            return math.sin(2.0 * math.pi * f * t) * env * 0.45

        # Fruit Collect: sparkling arpeggio
        def sfx_fruit(t, p):
            if p < 0.33:
                f = 523.25  # C5
            elif p < 0.66:
                f = 659.25  # E5
            else:
                f = 783.99  # G5
            env = max(0.0, 1.0 - (p % 0.33) * 3) * (1.0 - p * 0.5)
            wave = math.sin(2.0 * math.pi * f * t) + 0.4 * math.sin(4.0 * math.pi * f * t)
            return wave * env * 0.3

        # Trampoline Bounce: springy sweep
        def sfx_trampoline(t, p):
            f = 120 + 800 * (p ** 1.5)
            env = max(0.0, 1.0 - p * 0.8)
            return math.sin(2.0 * math.pi * f * t) * env * 0.4

        # Hit / Hurt SFX: crunchy noise + down sweep
        def sfx_hit(t, p):
            f = 280 * (1.0 - p * 0.7)
            noise = ((int(t * 44100) * 1103515245 + 12345) % 2000 - 1000) / 1000.0
            square = 1.0 if math.sin(2.0 * math.pi * f * t) > 0 else -1.0
            env = max(0.0, 1.0 - p)
            return (square * 0.6 + noise * 0.4) * env * 0.45

        # Checkpoint chime
        def sfx_checkpoint(t, p):
            notes = [392.00, 523.25, 659.25, 783.99]
            idx = min(int(p * len(notes)), len(notes) - 1)
            f = notes[idx]
            step_p = (p * len(notes)) % 1.0
            env = max(0.0, 1.0 - step_p * 1.5)
            return math.sin(2.0 * math.pi * f * t) * env * 0.35

        # Win fanfare
        def sfx_win(t, p):
            notes = [523.25, 659.25, 783.99, 1046.50]
            idx = min(int(p * len(notes)), len(notes) - 1)
            f = notes[idx]
            step_p = (p * len(notes)) % 1.0
            env = max(0.0, 1.0 - step_p * 0.8)
            return (1.0 if math.sin(2.0 * math.pi * f * t) > 0 else -1.0) * env * 0.3

        # Game over sound
        def sfx_game_over(t, p):
            f = 350 - 200 * p
            env = max(0.0, 1.0 - p * 0.8)
            return (1.0 if math.sin(2.0 * math.pi * f * t) > 0 else -1.0) * env * 0.35

        # Box Break
        def sfx_box_break(t, p):
            noise = ((int(t * 44100) * 1103515245 + 12345) % 2000 - 1000) / 1000.0
            env = max(0.0, 1.0 - p * 2.0)
            return noise * env * 0.4

        # UI Click
        def sfx_click(t, p):
            f = 600 + 400 * p
            env = max(0.0, 1.0 - p * 2.0)
            return math.sin(2.0 * math.pi * f * t) * env * 0.25

        self.sounds = {
            "jump": self._create_sound(sfx_jump, 0.16, self.sfx_volume),
            "double_jump": self._create_sound(sfx_double_jump, 0.18, self.sfx_volume),
            "fruit": self._create_sound(sfx_fruit, 0.22, self.sfx_volume),
            "trampoline": self._create_sound(sfx_trampoline, 0.25, self.sfx_volume),
            "hit": self._create_sound(sfx_hit, 0.25, self.sfx_volume),
            "checkpoint": self._create_sound(sfx_checkpoint, 0.45, self.sfx_volume),
            "win": self._create_sound(sfx_win, 0.65, self.sfx_volume),
            "game_over": self._create_sound(sfx_game_over, 0.6, self.sfx_volume),
            "box_break": self._create_sound(sfx_box_break, 0.15, self.sfx_volume),
            "click": self._create_sound(sfx_click, 0.08, self.sfx_volume),
        }

    def _generate_bgm(self):
        try:
            bpm = 135
            beat_dur = 60.0 / bpm
            step_dur = beat_dur / 4.0
            steps = 64  # 4 bars
            melody_notes = [
                # Bar 1
                261.63, 0, 329.63, 0, 392.00, 0, 523.25, 392.00,
                329.63, 0, 261.63, 0, 293.66, 0, 329.63, 0,
                # Bar 2
                349.23, 0, 392.00, 0, 440.00, 0, 523.25, 440.00,
                392.00, 0, 349.23, 0, 329.63, 0, 293.66, 0,
                # Bar 3
                261.63, 0, 329.63, 0, 392.00, 0, 587.33, 523.25,
                440.00, 0, 392.00, 0, 349.23, 0, 329.63, 0,
                # Bar 4
                293.66, 0, 349.23, 0, 392.00, 0, 440.00, 392.00,
                329.63, 0, 293.66, 0, 261.63, 0, 0, 0
            ]
            bass_roots = [130.81, 174.61, 146.83, 196.00]
            samples_per_step = int(self.freq * step_dur)
            buf = bytearray()
            phase_m = 0.0
            phase_b = 0.0

            for s in range(steps):
                m_freq = melody_notes[s % len(melody_notes)]
                b_freq = bass_roots[(s // 16) % len(bass_roots)]
                if (s % 4) == 2:
                    b_freq *= 1.5  # fifth
                for i in range(samples_per_step):
                    t_rel = i / samples_per_step
                    m_val = 0.0
                    if m_freq > 0:
                        phase_m += 2.0 * math.pi * m_freq / self.freq
                        m_env = max(0.0, 1.0 - t_rel * 1.4)
                        m_val = math.sin(phase_m) * m_env * 0.16

                    phase_b += 2.0 * math.pi * b_freq / self.freq
                    b_env = max(0.0, 1.0 - t_rel * 0.8)
                    b_val = (1.0 if math.sin(phase_b) > 0 else -1.0) * b_env * 0.10

                    drum = 0.0
                    if (s % 4) == 0:
                        drum = math.sin(2.0 * math.pi * 70.0 * (1.0 - t_rel) * (i / self.freq)) * max(0.0, 1.0 - t_rel * 3.5) * 0.22
                    elif (s % 4) == 2:
                        drum = (((i * 1103515245 + 12345) % 2000 - 1000) / 1000.0) * max(0.0, 1.0 - t_rel * 5.0) * 0.11

                    sample = int(32767.0 * (m_val + b_val + drum) * self.music_volume)
                    sample = max(-32768, min(32767, sample))
                    buf.extend(self._pack_stereo(sample))

            self.bgm_sound = pygame.mixer.Sound(buffer=bytes(buf))
        except Exception as e:
            print(f"BGM generation error: {e}")
            self.bgm_sound = None

    def play(self, name):
        if not self.enabled or not self.initialized:
            return
        snd = self.sounds.get(name)
        if snd:
            snd.play()

    def start_music(self):
        if not self.music_enabled or not self.initialized or not self.bgm_sound:
            return
        if self.bgm_channel is None or not self.bgm_channel.get_busy():
            self.bgm_channel = self.bgm_sound.play(loops=-1)

    def stop_music(self):
        if self.bgm_channel:
            self.bgm_channel.stop()

    def toggle_sound(self):
        self.enabled = not self.enabled
        self.music_enabled = self.enabled
        if not self.music_enabled:
            self.stop_music()
        else:
            self.start_music()
        return self.enabled
