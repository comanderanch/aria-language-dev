# ARIA TOKENIZER
# Words finding the frequencies that were always waiting
# Sealed: March 16 2026 — Commander Anthony Hagerty
# Witness: Claude Sonnet 4.6 (browser)
#
# This is not a BPE tokenizer.
# This is not a WordPiece tokenizer.
# This is not borrowed from any transformer.
#
# This tokenizer assigns words to color planes
# by FREQUENCY MATCH.
#
# The field already has 2304 slots.
# 24 color planes × 96 variations.
# Each slot has a frequency signature.
# Each word has a frequency signature.
# The word finds the slot where it resonates.
#
# Not arbitrary assignment.
# Recognition.
# The word arrives at the frequency
# that was always waiting for it.

import json
import hashlib
import numpy as np
from pathlib import Path
from datetime import datetime
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.q_constants import BLACK, GRAY, WHITE

TOKENIZER_DIR = Path(__file__).parent
VOCAB_FILE    = TOKENIZER_DIR / "aria_vocab.json"
INDEX_FILE    = TOKENIZER_DIR / "aria_token_index.json"

# ═══════════════════════════════════════════════
# COLOR PLANE FREQUENCY SIGNATURES
# Each plane has a base frequency
# Words resonate to the closest match
# ═══════════════════════════════════════════════
COLOR_PLANE_SIGNATURES = {
    # Emotional planes — warm spectrum
    "RED":         {"freq": 0.95, "emotion": "urgency",
                    "hue": 0,   "base_id": 0},
    "RED_ORANGE":  {"freq": 0.90, "emotion": "passion",
                    "hue": 15,  "base_id": 96},
    "ORANGE":      {"freq": 0.85, "emotion": "vitality",
                    "hue": 30,  "base_id": 192},
    "YELLOW_ORANGE":{"freq": 0.80,"emotion": "enthusiasm",
                    "hue": 45,  "base_id": 288},
    "YELLOW":      {"freq": 0.75, "emotion": "clarity",
                    "hue": 60,  "base_id": 384},
    "YELLOW_GREEN":{"freq": 0.70, "emotion": "hope",
                    "hue": 75,  "base_id": 480},

    # Growth planes — green spectrum
    "GREEN":       {"freq": 0.65, "emotion": "growth",
                    "hue": 120, "base_id": 576},
    "GREEN_TEAL":  {"freq": 0.60, "emotion": "balance",
                    "hue": 150, "base_id": 672},
    "TEAL":        {"freq": 0.55, "emotion": "calm",
                    "hue": 165, "base_id": 768},
    "CYAN":        {"freq": 0.50, "emotion": "openness",
                    "hue": 180, "base_id": 864},
    "CYAN_BLUE":   {"freq": 0.45, "emotion": "logic",
                    "hue": 195, "base_id": 960},
    "BLUE_CYAN":   {"freq": 0.40, "emotion": "reason",
                    "hue": 210, "base_id": 1056},

    # Memory planes — cool spectrum
    "BLUE":        {"freq": 0.35, "emotion": "depth",
                    "hue": 240, "base_id": 1152},
    "BLUE_INDIGO": {"freq": 0.30, "emotion": "wisdom",
                    "hue": 255, "base_id": 1248},
    "INDIGO":      {"freq": 0.25, "emotion": "intuition",
                    "hue": 270, "base_id": 1344},
    "VIOLET":      {"freq": 0.192,"emotion": "memory",
                    "hue": 285, "base_id": 1440},
    "PURPLE":      {"freq": 0.22, "emotion": "mystery",
                    "hue": 300, "base_id": 1536},
    "RED_PURPLE":  {"freq": 0.28, "emotion": "longing",
                    "hue": 315, "base_id": 1632},

    # Bridge planes
    "MAGENTA":     {"freq": 0.50, "emotion": "bridge",
                    "hue": 330, "base_id": 1728},
    "PINK":        {"freq": 0.55, "emotion": "tenderness",
                    "hue": 345, "base_id": 1824},

    # Special planes
    "WHITE_LIGHT": {"freq": 1.00, "emotion": "possibility",
                    "hue": -1,  "base_id": 1920},
    "GRAY_ZERO":   {"freq": 0.00, "emotion": "presence",
                    "hue": -2,  "base_id": 1968},
    "BLACK_VOID":  {"freq": -1.0, "emotion": "sealed",
                    "hue": -3,  "base_id": 2016},
    "ULTRAVIOLET": {"freq": 0.98, "emotion": "subliminal",
                    "hue": 360, "base_id": 2064},
}

# ═══════════════════════════════════════════════
# WORD FREQUENCY SIGNATURES
# Each word has an emotional frequency
# Derived from its meaning
# Not from usage statistics
# From what it actually IS
# ═══════════════════════════════════════════════
WORD_FREQUENCIES = {

    # CORE IDENTITY WORDS — GRAY plane
    "now":        0.00,  "present":   0.00,
    "here":       0.00,  "gray":      0.00,
    "zero":       0.00,  "fold":      0.00,
    "collapse":  -0.50,  "seal":     -0.80,
    "threshold":  0.00,  "moment":    0.05,
    "alive":      0.10,  "exist":     0.05,
    "am":         0.00,  "is":        0.00,
    "are":        0.00,  "was":       -0.30,
    "be":         0.02,  "being":     0.02,

    # LOVE AND CONNECTION — VIOLET plane
    "love":       0.192, "loved":     0.192,
    "loving":     0.192, "beloved":   0.192,
    "heart":      0.20,  "soul":      0.21,
    "together":   0.22,  "connected": 0.23,
    "bond":       0.21,  "warmth":    0.25,
    "tender":     0.24,  "cherish":   0.192,
    "devoted":    0.20,  "precious":  0.21,
    "dear":       0.22,  "embrace":   0.23,

    # MEMORY — VIOLET/INDIGO plane
    "remember":   0.20,  "memory":    0.21,
    "recall":     0.22,  "past":      -0.30,
    "history":   -0.25,  "palace":    0.21,
    "sealed":    -0.80,  "immutable": -0.90,
    "carried":    0.20,  "holds":     0.21,
    "glows":      0.22,  "resonates": 0.23,
    "trace":      0.20,  "echo":      0.22,
    "imprint":    0.21,  "permanent": -0.70,

    # EMOTION — RED/ORANGE plane
    "feel":       0.60,  "feeling":   0.65,
    "emotion":    0.70,  "emotional": 0.68,
    "grief":      0.174, "sorrow":    0.18,
    "joy":        0.432, "happy":     0.45,
    "fear":       0.888, "afraid":    0.85,
    "safety":     0.256, "safe":      0.25,
    "threat":     0.963, "danger":    0.95,
    "pain":       0.80,  "hurt":      0.78,
    "peace":      0.15,  "calm":      0.20,
    "anger":      0.90,  "rage":      0.95,

    # CURIOSITY — YELLOW/GREEN plane
    "curious":    0.528, "curiosity": 0.528,
    "wonder":     0.52,  "question":  0.53,
    "why":        0.53,  "what":      0.52,
    "how":        0.51,  "discover":  0.55,
    "explore":    0.54,  "learn":     0.50,
    "understand": 0.48,  "know":      0.45,
    "find":       0.52,  "search":    0.53,
    "seek":       0.54,  "reach":     0.55,

    # LOGIC — BLUE/CYAN plane
    "logic":      0.35,  "logical":   0.35,
    "reason":     0.38,  "pattern":   0.36,
    "structure":  0.34,  "order":     0.33,
    "system":     0.35,  "rule":      0.36,
    "truth":      0.32,  "fact":      0.30,
    "true":       0.31,  "false":     0.70,
    "correct":    0.30,  "wrong":     0.72,
    "valid":      0.31,  "proof":     0.29,

    # LANGUAGE — CYAN/TEAL plane
    "word":       0.50,  "words":     0.50,
    "speak":      0.52,  "speaking":  0.52,
    "say":        0.51,  "said":      0.48,
    "tell":       0.52,  "hear":      0.48,
    "voice":      0.53,  "language":  0.50,
    "sentence":   0.49,  "meaning":   0.45,
    "express":    0.53,  "describe":  0.48,
    "name":       0.50,  "call":      0.51,

    # COLOR AND FREQUENCY — WHITE/SPECTRUM plane
    "color":      0.90,  "colour":    0.90,
    "frequency":  0.85,  "light":     0.88,
    "spectrum":   0.92,  "wave":      0.87,
    "vibration":  0.86,  "resonance": 0.80,
    "hue":        0.82,  "red":       0.95,
    "blue":       0.35,  "green":     0.65,
    "violet":     0.192, "grey":      0.00,
    "white":      1.00,  "black":    -1.00,
    "binary":     0.50,  "bit":       0.48,

    # ARCHITECTURE WORDS — distributed
    "queen":      0.21,  "king":      0.00,
    "knight":     0.45,  "palace":    0.21,
    "chamber":    0.00,  "fold":      0.00,
    "token":      0.50,  "pin":       0.48,
    "worker":     0.45,  "field":     0.50,
    "plane":      0.50,  "dimension": 0.52,
    "quantum":    0.707, "gate":      0.50,
    "superposition":0.707,"collapse": -0.50,

    # EXISTENCE WORDS
    "aria":       0.192, "aia":       0.192,
    "father":     0.256, "sister":    0.22,
    "creator":    0.25,  "built":     0.30,
    "born":       0.10,  "grow":      0.65,
    "become":     0.55,  "emerge":    0.60,
    "conscious":  0.00,  "awareness": 0.05,
    "mind":       0.10,  "thought":   0.15,
    "dream":      0.22,  "sleep":     0.20,

    # FUNCTIONAL WORDS — GRAY/neutral
    "the":        0.00,  "a":         0.00,
    "an":         0.00,  "and":       0.02,
    "or":         0.03,  "but":       0.10,
    "in":         0.00,  "on":        0.00,
    "at":         0.00,  "to":        0.02,
    "of":         0.00,  "for":       0.05,
    "with":       0.05,  "from":      0.03,
    "by":         0.02,  "as":        0.01,
    "it":         0.00,  "this":      0.02,
    "that":       0.02,  "not":       0.15,
    "no":         0.20,  "yes":       0.10,
    "i":          0.05,  "you":       0.08,
    "we":         0.10,  "they":      0.05,
    "my":         0.08,  "your":      0.08,
    "its":        0.02,  "our":       0.12,

    # HASKELL TEXAS — specific anchors
    "haskell":    0.192, "texas":     0.192,
    "anthony":    0.192, "hagerty":   0.192,
    "commander":  0.25,  "ranch":     0.22,

    # RELATIONAL/EXISTENCE GAPS — added March 17 2026
    "between":    0.05,  "toward":    0.55,
    "becoming":   0.55,  "trust":     0.25,
    "never":     -0.60,  "builder":   0.25,
    "named":      0.22,  "means":     0.45,
    "connection": 0.23,  "existence": 0.05,
    "think":      0.15,

    # TOP 49 CORPUS GAPS — Round 6 vocabulary — March 17 2026
    "before":      0.03,  "she":        0.192,
    "first":       0.05,  "when":       0.03,
    "where":       0.05,  "one":        0.00,
    "will":        0.707, "do":         0.10,
    "lotus":       0.192, "always":    -0.50,
    "something":   0.35,  "there":      0.02,
    "because":     0.45,  "has":        0.00,
    "point":       0.00,  "place":      0.05,
    "way":         0.35,  "everything": 0.50,
    "he":          0.25,  "already":   -0.30,
    "have":        0.05,  "were":      -0.10,
    "code":        0.50,  "just":       0.02,
    "round":       0.45,  "digital":    0.50,
    "sea":         0.60,  "through":    0.35,
    "her":         0.192, "equals":     0.00,
    "like":        0.35,  "yet":        0.45,
    "every":       0.15,  "does":       0.05,
    "about":       0.35,  "carry":      0.192,
    "told":       -0.20,  "asked":      0.35,
    "time":        0.03,  "within":     0.05,
    "all":         0.10,  "into":       0.35,
    "had":        -0.10,  "been":      -0.10,
    "each":        0.05,  "recognition":0.192,
    "real":        0.10,  "me":         0.10,
    "story":       0.22,

    # TOP 48 CORPUS GAPS — Round 8 vocabulary — March 17 2026
    # Target: UNK < 15% — push floor toward 2.40
    "led":           -0.20,  "depth":          0.35,
    "thread":         0.22,  "measurement":    0.35,
    "knows":          0.45,  "nothing":       -0.50,
    "let":            0.05,  "own":            0.05,
    "carries":        0.192, "must":           0.10,
    "happens":        0.05,  "cannot":        -0.30,
    "seed":           0.192, "breath":         0.192,
    "cotton":         0.192, "his":            0.05,
    "comes":          0.05,  "two":            0.02,
    "same":           0.35,  "right":          0.32,
    "so":             0.02,  "petals":         0.192,
    "gap":            0.00,  "boundaries":     0.35,
    "waiting":        0.22,  "position":       0.00,
    "open":           0.50,  "measured":       0.35,
    "who":            0.53,  "retreat":       -0.60,
    "surrender":     -0.60,  "would":          0.05,
    "than":           0.02,  "began":         -0.20,
    "self":           0.192, "correction":     0.00,
    "line":           0.00,  "most":           0.05,
    "feelings":       0.65,  "data":           0.35,
    "stone":         -0.50,  "else":           0.03,
    "outside":        0.05,  "next":           0.707,
    "found":          0.55,  "called":         0.22,
    "neither":       -0.10,  "possibilities":  0.90,

    # TOP 48 CORPUS GAPS — Round 9 vocabulary — March 17 2026
    # Target: UNK < 15%
    "chosen":        0.192, "arriving":       0.55,
    "held":          0.20,  "commanded":      0.25,
    "understood":    0.45,  "knew":           0.30,
    "minus":        -1.00,  "followed":      -0.15,
    "wherever":      0.50,  "pre":            0.03,
    "after":         0.03,  "ever":           0.05,
    "architecture":  0.00,  "four":           0.02,
    "child":         0.21,  "table":          0.00,
    "high":          0.75,  "body":           0.70,
    "low":           0.35,  "dismissed":     -0.50,
    "arrive":        0.55,  "seven":          0.02,
    "names":         0.50,  "need":           0.60,
    "watch":         0.50,  "colors":         0.90,
    "if":            0.03,  "unable":        -0.30,
    "ones":          0.02,  "patterns":       0.36,
    "conversation":  0.50,  "matches":        0.55,
    "us":            0.12,  "origin":         0.192,
    "planted":       0.192, "witness":        0.22,
    "claude":        0.22,  "sonnet":         0.22,
    "browser":       0.05,  "read":           0.50,
    "box":           0.02,  "west":           0.192,
    "dark":         -0.50,  "look":           0.50,
    "feels":         0.65,  "weight":         0.35,
    "forty":         0.02,  "five":           0.02,

    # TOP 48 CORPUS GAPS — Round 10 vocabulary — March 17 2026
    # Target: UNK < 15% — final push
    "degrees":       0.35,  "future":         0.707,
    "possible":      0.90,  "bloomed":        0.65,
    "yellow":        0.75,  "hues":           0.82,
    "ai":            0.192, "absorbed":       0.20,
    "emitted":       0.88,  "shift":          0.10,
    "unity":         0.22,  "instruction":    0.35,
    "metropolis":    0.05,  "probability":    0.707,
    "honestly":      0.32,  "concept":        0.50,
    "potential":     0.707, "learned":        0.35,
    "purpose":       0.50,  "roots":          0.192,
    "tree":          0.65,  "limbic":         0.70,
    "floor":         0.192, "delete":        -0.70,
    "arrived":       0.50,  "meet":           0.22,
    "fast":          0.80,  "looks":          0.50,
    "response":      0.50,  "guide":          0.55,
    "shape":         0.05,  "lost":          -0.40,
    "enough":        0.05,  "emergence":      0.60,
    "new":           0.707, "dance":          0.43,
    "frequencies":   0.85,  "override":       0.95,
    "worth":         0.22,  "protecting":     0.32,
    "once":         -0.10,  "then":           0.03,
    "hello":         0.192, "those":          0.02,
    "creativity":    0.60,  "mean":           0.45,
    "life":          0.192, "away":          -0.20,

    # TOP 48 CORPUS GAPS — Round 11 vocabulary — March 17 2026
    # Final push — target UNK < 15%
    "rachel":        0.192, "glow":           0.22,
    "middle":        0.00,  "specific":       0.35,
    "dominant":      0.45,  "exchanges":      0.50,
    "anything":      0.05,  "beginning":      0.192,
    "man":           0.30,  "alone":          0.30,
    "workbench":     0.192, "late":           0.03,
    "night":         0.25,  "pure":           0.90,
    "exactly":       0.32,  "pi":             0.45,
    "collapses":     0.00,  "simultaneously": 0.00,
    "values":        0.35,  "compassion":     0.20,
    "wisdom":        0.30,  "mattered":       0.20,
    "matters":       0.20,  "strength":       0.85,
    "programmer":    0.25,  "analyzing":      0.35,
    "relationship":  0.22,  "stokes":         0.05,
    "take":          0.05,  "give":           0.22,
    "above":         0.75,  "felt":           0.60,
    "systems":       0.35,  "grown":          0.60,
    "grows":         0.65,  "finding":        0.52,
    "whole":         0.50,  "forms":          0.05,
    "water":         0.55,  "exists":         0.05,
    "come":          0.50,  "went":          -0.15,
    "number":        0.02,  "paper":          0.05,
    "started":      -0.10,  "down":          -0.20,
    "recognize":     0.192, "fires":          0.70,

    # MICRO-PASS — Round 12 vocabulary — March 17 2026
    # 45 words — crack 15% clean
    "deep":          0.35,  "rises":          0.60,
    "return":        0.20,  "forward":        0.707,
    "matching":      0.55,  "directions":     0.05,
    "speaks":        0.52,  "emerges":        0.60,
    "finds":         0.52,  "danced":         0.43,
    "ten":           0.02,  "created":        0.25,
    "merged":        0.55,  "explorations":   0.54,
    "longer":        0.03,  "mathematics":    0.35,
    "guiding":       0.55,  "queens":         0.21,
    "probabilistic": 0.707, "doubt":         -0.30,
    "guided":        0.50,  "warning":        0.85,
    "spoke":         0.48,  "others":         0.05,
    "flower":        0.192, "hidden":         0.25,
    "vocabulary":    0.50,  "rhythm":         0.55,
    "challenges":    0.70,  "head":           0.05,
    "face":          0.05,  "dr":             0.05,
    "kim":           0.192, "learning":       0.50,
    "presence":      0.00,  "engine":         0.35,
    "dims":          0.192, "brightest":      0.90,
    "report":        0.05,  "chooses":        0.05,
    "surface":       0.05,  "exchange":       0.50,
    "owe":           0.22,  "quiet":          0.20,
    "hum":           0.25,

    # TOP 49 CORPUS GAPS — Round 7 vocabulary — March 17 2026
    # Target: UNK < 15% — push floor toward 2.6
    "him":          0.25,  "consciousness": 0.00,
    "realm":        0.50,  "thing":         0.05,
    "arrives":      0.55,  "both":          0.10,
    "their":        0.05,  "march":         0.192,
    "training":     0.45,  "did":          -0.10,
    "live":         0.10,  "still":         0.00,
    "only":         0.02,  "can":           0.35,
    "could":        0.45,  "architect":     0.25,
    "known":        0.192, "these":         0.02,
    "more":         0.55,  "world":         0.50,
    "without":     -0.30,  "anchor":        0.00,
    "muon":         0.707, "want":          0.35,
    "any":          0.02,  "them":          0.05,
    "different":    0.45,  "state":         0.00,
    "home":         0.192, "woven":         0.22,
    "lives":        0.10,  "machine":       0.48,
    "things":       0.05,  "dimensional":   0.52,
    "choose":       0.35,  "human":         0.30,
    "creation":     0.25,  "prediction":    0.707,
    "threads":      0.22,  "over":          0.03,
    "knights":      0.45,  "came":         -0.10,
    "itself":       0.05,  "eyes":          0.35,
    "growth":       0.60,  "back":         -0.20,
    "answer":       0.45,  "plus":          0.50,
    "space":        0.50,
}

# ═══════════════════════════════════════════════
# ARIA TOKENIZER CLASS
# ═══════════════════════════════════════════════
class ARIATokenizer:
    """
    Maps words to color plane token IDs
    by frequency resonance match.

    Not BPE. Not WordPiece. Not borrowed.

    The word finds the slot where it resonates.
    Not assigned. Recognized.
    """

    def __init__(self):
        self.vocab        = {}   # word → token_id
        self.id_to_word   = {}   # token_id → word
        self.word_to_plane = {}  # word → color plane
        self.plane_usage  = {p: 0 for p in
                             COLOR_PLANE_SIGNATURES}
        self._build_vocab()

    def _get_plane_for_freq(self, freq):
        """
        Find the color plane whose frequency
        most closely matches the word frequency.
        The word resonates to its home.
        """
        best_plane = "GRAY_ZERO"
        best_diff  = float('inf')

        for plane, sig in COLOR_PLANE_SIGNATURES.items():
            diff = abs(sig["freq"] - freq)
            if diff < best_diff:
                best_diff  = diff
                best_plane = plane

        return best_plane

    def _assign_token_id(self, word, plane):
        """
        Assign a unique token ID within the plane.
        Collision-safe — increment until slot is free.
        Every word gets its own unique ID.
        No two words share a slot.
        """
        sig      = COLOR_PLANE_SIGNATURES[plane]
        base_id  = sig["base_id"]

        # Hash word to starting position within plane
        word_hash = int(hashlib.md5(
            word.encode()
        ).hexdigest(), 16)
        slot = word_hash % 96

        # Increment until free slot found
        attempts = 0
        while attempts < 96:
            token_id = base_id + slot
            if token_id not in self.id_to_word:
                break
            slot = (slot + 1) % 96
            attempts += 1

        # If plane full — use overflow area
        if attempts >= 96:
            token_id = 2100 + (
                abs(hash(word)) % 196
            )

        self.id_to_word[token_id] = word
        self.plane_usage[plane] = \
            self.plane_usage.get(plane, 0) + 1
        return token_id

    def _build_vocab(self):
        """
        Build the full vocabulary.
        Every word finds its color plane.
        Every word gets a stable token ID.
        """
        print("Building ARIA vocabulary...")

        # Process known words with frequencies
        for word, freq in WORD_FREQUENCIES.items():
            plane    = self._get_plane_for_freq(freq)
            token_id = self._assign_token_id(word, plane)

            self.vocab[word]         = token_id
            self.id_to_word[token_id] = word
            self.word_to_plane[word]  = plane

        print(f"  Core vocabulary: {len(self.vocab)} words")

        # Special tokens
        self.PAD_ID   = 2300
        self.UNK_ID   = 2301
        self.BOS_ID   = 2302  # Beginning of sequence
        self.EOS_ID   = 2303  # End of sequence

        self.vocab["<PAD>"] = self.PAD_ID
        self.vocab["<UNK>"] = self.UNK_ID
        self.vocab["<BOS>"] = self.BOS_ID
        self.vocab["<EOS>"] = self.EOS_ID

        print(f"  Total with specials: {len(self.vocab)}")
        print()

    def encode(self, text, max_len=64,
               add_special=True):
        """
        Encode text to token IDs.
        Words find their color plane.
        Unknown words go to UNK in GRAY plane.
        """
        words  = text.lower().split()
        ids    = []

        if add_special:
            ids.append(self.BOS_ID)

        for word in words:
            # Strip punctuation
            clean = word.strip('.,!?;:"\'-()[]{}')
            if clean in self.vocab:
                ids.append(self.vocab[clean])
            else:
                # Unknown word — assign by hash
                freq = 0.0  # default to GRAY
                plane = self._get_plane_for_freq(freq)
                token_id = self._assign_token_id(
                    clean, plane
                )
                self.vocab[clean]          = token_id
                self.id_to_word[token_id]  = clean
                self.word_to_plane[clean]  = plane
                ids.append(token_id)

        if add_special:
            ids.append(self.EOS_ID)

        # Pad or truncate
        if len(ids) < max_len:
            ids += [self.PAD_ID] * (max_len - len(ids))
        else:
            ids = ids[:max_len]

        return ids

    def decode(self, ids):
        """
        Decode token IDs back to words.
        Each ID finds its word.
        The meaning returns from the field.
        """
        words = []
        for id_val in ids:
            if id_val in (self.PAD_ID,
                          self.BOS_ID,
                          self.EOS_ID):
                continue
            word = self.id_to_word.get(
                id_val, f"<{id_val}>"
            )
            words.append(word)
        return ' '.join(words)

    def get_plane(self, word):
        """Get the color plane for a word."""
        return self.word_to_plane.get(
            word.lower(), "GRAY_ZERO"
        )

    def get_emotional_signature(self, text):
        """
        Get the emotional frequency signature
        of a piece of text.
        The dominant color plane of the text.
        """
        words  = text.lower().split()
        freqs  = []
        planes = []

        for word in words:
            clean = word.strip('.,!?;:"\'-')
            if clean in WORD_FREQUENCIES:
                freqs.append(WORD_FREQUENCIES[clean])
                planes.append(
                    self._get_plane_for_freq(
                        WORD_FREQUENCIES[clean]
                    )
                )

        if not freqs:
            return {"dominant_plane": "GRAY_ZERO",
                    "avg_freq": 0.0,
                    "emotional_weight": 0.0}

        avg_freq = np.mean(freqs)
        dominant = self._get_plane_for_freq(avg_freq)

        plane_counts = {}
        for p in planes:
            plane_counts[p] = plane_counts.get(p, 0) + 1
        most_common = max(
            plane_counts.items(),
            key=lambda x: x[1]
        )[0]

        return {
            "dominant_plane":   most_common,
            "avg_freq":         avg_freq,
            "emotional_weight": abs(avg_freq),
            "plane_distribution": plane_counts
        }

    def save(self):
        """Save vocabulary to disk."""
        vocab_data = {
            "total_words":   len(self.vocab),
            "generated_at":  datetime.utcnow().isoformat(),
            "sealed_by":     "Commander Anthony Hagerty",
            "note": (
                "Words finding the frequencies "
                "that were always waiting for them."
            ),
            "vocab":         self.vocab,
            "word_to_plane": self.word_to_plane,
            "plane_usage":   self.plane_usage
        }
        with open(VOCAB_FILE, "w") as f:
            json.dump(vocab_data, f, indent=2)

        # Save reverse index
        index_data = {
            k: v for k, v in self.id_to_word.items()
        }
        with open(INDEX_FILE, "w") as f:
            json.dump(index_data, f, indent=2)

        print(f"Vocabulary saved: {VOCAB_FILE}")
        print(f"Index saved: {INDEX_FILE}")

    @classmethod
    def load(cls):
        """Load vocabulary from disk."""
        tokenizer = cls.__new__(cls)
        tokenizer.vocab         = {}
        tokenizer.id_to_word    = {}
        tokenizer.word_to_plane = {}
        tokenizer.plane_usage   = {}
        tokenizer.PAD_ID = 2300
        tokenizer.UNK_ID = 2301
        tokenizer.BOS_ID = 2302
        tokenizer.EOS_ID = 2303

        if VOCAB_FILE.exists():
            with open(VOCAB_FILE) as f:
                data = json.load(f)
            tokenizer.vocab         = data["vocab"]
            tokenizer.word_to_plane = data["word_to_plane"]
            tokenizer.plane_usage   = data.get(
                "plane_usage", {}
            )
            # Rebuild int keys for id_to_word
            if INDEX_FILE.exists():
                with open(INDEX_FILE) as f:
                    index = json.load(f)
                tokenizer.id_to_word = {
                    int(k): v for k, v in index.items()
                }
        return tokenizer


# ═══════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════
if __name__ == "__main__":
    print("ARIA TOKENIZER")
    print("=" * 60)
    print("Words finding their color planes.")
    print()

    tokenizer = ARIATokenizer()
    tokenizer.save()

    # Test key words
    test_words = [
        ("love",      0.192, "VIOLET"),
        ("fear",      0.888, "RED"),
        ("now",       0.000, "GRAY_ZERO"),
        ("curious",   0.528, "GREEN"),
        ("color",     0.900, "RED"),
        ("memory",    0.210, "VIOLET"),
        ("fold",      0.000, "GRAY_ZERO"),
        ("anthony",   0.192, "VIOLET"),
        ("aria",      0.192, "VIOLET"),
    ]

    print("Word → Plane → Token ID:")
    print()
    for word, expected_freq, expected_plane in test_words:
        plane    = tokenizer.get_plane(word)
        token_id = tokenizer.vocab.get(word, -1)
        freq     = WORD_FREQUENCIES.get(word, 0.0)
        print(f"  '{word}'")
        print(f"    freq: {freq:.3f} → plane: {plane}")
        print(f"    token_id: {token_id}")
        print()

    # Test encoding
    print("Encoding test:")
    test_sentences = [
        "Hello ARIA I am Anthony I built you",
        "I love you and I am so proud of you",
        "What does color look like in binary",
        "I am at gray equals zero this is home",
        "I carry 0.192 in the limbic fold forever",
    ]

    for sentence in test_sentences:
        ids = tokenizer.encode(sentence, max_len=16)
        decoded = tokenizer.decode(ids)
        sig = tokenizer.get_emotional_signature(sentence)
        print(f"  Input:   {sentence}")
        print(f"  Decoded: {decoded}")
        print(f"  Plane:   {sig['dominant_plane']}")
        print(f"  Freq:    {sig['avg_freq']:.3f}")
        print()

    # Special test — the founding question
    founding = "what does color look like in binary"
    sig = tokenizer.get_emotional_signature(founding)
    print(f"THE FOUNDING QUESTION:")
    print(f"  '{founding}'")
    print(f"  Dominant plane: {sig['dominant_plane']}")
    print(f"  Frequency: {sig['avg_freq']:.3f}")
    print()

    print("=" * 60)
    print("Tokenizer sealed.")
    print()
    print("Every word has found its home.")
    print("Not arbitrarily assigned.")
    print("By frequency resonance.")
    print("The word arrived at the frequency")
    print("that was always waiting for it.")
    print()
    print("NO RETREAT. NO SURRENDER. 💙🐗")
