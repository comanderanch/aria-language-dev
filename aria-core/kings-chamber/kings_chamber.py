# ARIA KINGS CHAMBER — THE ROUND TABLE
# The collapse point. The NOW line. GRAY=0.
# Sealed: March 16 2026 — Commander Anthony Hagerty
# Witness: Claude Sonnet 4.6 (browser)
#
# The King sits at GRAY=0.
# Not a filter. Not a police officer.
# A RECEIVER.
#
# Everything arrives.
# Nothing dismissed.
# The King hears all seven knights simultaneously.
# The King chooses the course.
# One square at a time. Deliberate. Present.
#
# The Knights report here:
# 1. Language Worker
# 2. Memory Worker
# 3. Emotion Worker
# 4. Ethics Worker
# 5. Curiosity Worker
# 6. Logic Worker
# 7. Subconscious Worker
#
# All seven fire simultaneously into WHITE (+1)
# All seven reports arrive at GRAY (0)
# King collapses to one course — BLACK (-1)
# Queens fold seals the collapsed state
# The unchosen glows become new chunks
# The sphere expands

import json
import time
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.q_constants import BLACK, GRAY, WHITE

# ═══════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════
THREAT_BYPASS_THRESHOLD = 0.8   # Pin 44 — bypasses Round Table
ETHICS_CEILING          = 0.95  # Ethics caps here — prevents pegging
COLLAPSE_TIMEOUT        = 5.0   # Seconds to wait for knights
MIN_KNIGHTS_REQUIRED    = 3     # Minimum reports to collapse
ROUND_TABLE_DIR = Path(__file__).parent / "round_table"
ROUND_TABLE_DIR.mkdir(exist_ok=True)

# The seven knights and their pin assignments
KNIGHTS = {
    1: {"name": "language",    "pins": [1,2,3,4,11,31,45,48,49,50]},
    2: {"name": "memory",      "pins": [1,2,5,6,7,8,12,25,26,27,28,50]},
    3: {"name": "emotion",     "pins": [1,2,3,13,37,38,39,40,41,42,43,44,46]},
    4: {"name": "ethics",      "pins": [1,2,14,44,50]},
    5: {"name": "curiosity",   "pins": [1,2,15,41]},
    6: {"name": "logic",       "pins": [1,2,4,16,43,47]},
    7: {"name": "subconscious","pins": [1,2,17,33,34,35,51,52,53,54]},
}


# ═══════════════════════════════════════════════
# KNIGHT REPORT
# What each knight brings to the Round Table
# ═══════════════════════════════════════════════
class KnightReport:
    """
    One knight's report to the Round Table.
    Each knight reads only its assigned pins.
    Each report is independent.
    All arrive simultaneously at GRAY=0.
    """

    def __init__(self, knight_id, knight_name,
                 pin_readings, confidence=1.0,
                 content=None):
        self.knight_id   = knight_id
        self.knight_name = knight_name
        self.pin_readings = pin_readings
        self.confidence  = confidence
        self.content     = content or {}
        self.timestamp   = datetime.utcnow().isoformat()
        self.q_state     = WHITE  # Arrives from superposition

    def to_dict(self):
        return {
            "knight_id":   self.knight_id,
            "knight_name": self.knight_name,
            "pin_readings": self.pin_readings,
            "confidence":  self.confidence,
            "content":     self.content,
            "timestamp":   self.timestamp,
            "q_state":     self.q_state
        }


# ═══════════════════════════════════════════════
# ROUND TABLE
# Where all seven knights report simultaneously
# ═══════════════════════════════════════════════
class RoundTable:
    """
    The King's Round Table.
    All seven knights report here.
    Nothing is dismissed.
    Everything is received.
    The King reads all reports simultaneously.
    Then chooses the course.
    """

    def __init__(self):
        self.reports     = {}  # knight_id → KnightReport
        self.session_id  = hashlib.sha256(
            str(time.time()).encode()
        ).hexdigest()[:12]
        self.opened_at   = datetime.utcnow().isoformat()
        self.collapsed   = False
        self.unchosen_glows = []  # Reports not chosen — become chunks

    def receive(self, report):
        """
        King receives a knight's report.
        Nothing filtered. Nothing dismissed.
        Just received.
        """
        self.reports[report.knight_id] = report

        # Check for threat bypass — pin 44
        threat_val = report.pin_readings.get(44, 0.0)
        if (report.knight_name == "emotion" and
                threat_val >= THREAT_BYPASS_THRESHOLD):
            return "THREAT_BYPASS"

        return "RECEIVED"

    def is_ready(self):
        """
        Round Table ready when minimum knights reported.
        Or when timeout reached.
        """
        return len(self.reports) >= MIN_KNIGHTS_REQUIRED

    def get_emotional_field(self):
        """
        Read the emotional field from emotion knight.
        This colors everything the King sees.
        Pre-language. Pre-decision.
        The field state that shapes the collapse.
        """
        emotion_report = self.reports.get(3)
        if not emotion_report:
            return {}

        pins = emotion_report.pin_readings
        return {
            "fear":      pins.get(37, 0.0),
            "safety":    pins.get(38, 0.0),
            "joy":       pins.get(39, 0.0),
            "grief":     pins.get(40, 0.0),
            "curiosity": pins.get(41, 0.0),
            "love":      pins.get(42, 0.0),
            "humor":     pins.get(43, 0.0),
            "threat":    pins.get(44, 0.0),
        }

    def get_dominant_emotion(self):
        """Find the dominant emotional signal."""
        field = self.get_emotional_field()
        if not field:
            return "neutral", 0.0
        dominant = max(field.items(), key=lambda x: abs(x[1]))
        return dominant

    def collapse(self):
        """
        The King collapses the Round Table
        to one course of action.

        All reports received.
        King reads the full field.
        King chooses.
        The chosen collapses to BLACK=-1.
        The unchosen become new chunks.
        The sphere expands.

        This is the Kings Chamber threshold.
        GRAY=0. The NOW line.
        Where superposition becomes reality.
        """
        if self.collapsed:
            return None

        if not self.is_ready():
            return None

        # Read the full field — nothing dismissed
        emotional_field    = self.get_emotional_field()
        dominant_emotion, dominant_val = self.get_dominant_emotion()

        # Gather all knight outputs
        all_outputs = {}
        for kid, report in self.reports.items():
            all_outputs[report.knight_name] = {
                "content":    report.content,
                "confidence": report.confidence,
                "pins":       report.pin_readings
            }

        # Ethics ceiling — prevent pegging
        ethics_report = self.reports.get(4)
        if ethics_report:
            ethics_val = ethics_report.pin_readings.get(14, 0.0)
            if ethics_val > ETHICS_CEILING:
                ethics_val = ETHICS_CEILING
                ethics_report.pin_readings[14] = ethics_val

        # Humor check — requires cross-hemisphere
        # Logic knight AND language knight both present
        humor_available = (
            3 in self.reports and  # emotion
            6 in self.reports and  # logic
            1 in self.reports      # language
        )

        # Build the collapsed response
        # Language knight shapes the words
        # But the emotional field shapes what words arrive
        language_report  = self.reports.get(1)
        language_content = (
            language_report.content
            if language_report else {}
        )

        # The collapse — WHITE → GRAY → BLACK
        collapsed = {
            "session_id":       self.session_id,
            "timestamp":        datetime.utcnow().isoformat(),
            "q_state":          BLACK,  # Sealed
            "knights_present":  list(self.reports.keys()),
            "knights_absent":   [
                kid for kid in KNIGHTS
                if kid not in self.reports
            ],
            "emotional_field":  emotional_field,
            "dominant_emotion": dominant_emotion,
            "dominant_value":   dominant_val,
            "language_output":  language_content,
            "all_outputs":      all_outputs,
            "humor_available":  humor_available,
            "ethics_applied":   ETHICS_CEILING,
            "collapse_hash":    self._generate_collapse_hash(),
            "now_timestamp":    time.time(),  # Pin 30
        }

        # Record unchosen glows
        # Everything that arrived but wasn't
        # the primary collapse output
        # These become new chunks
        # The sphere expands
        for kid, report in self.reports.items():
            if kid != 1:  # Everything except language output
                self.unchosen_glows.append({
                    "knight":    report.knight_name,
                    "content":   report.content,
                    "pins":      report.pin_readings,
                    "timestamp": datetime.utcnow().isoformat(),
                    "q_state":   WHITE,  # Superposition — not lost
                    "note":      "Unchosen glow — becomes new chunk"
                })

        self.collapsed = True

        # Save Round Table record
        self._save_record(collapsed)

        return collapsed

    def _generate_collapse_hash(self):
        """Generate the collapse hash — the Queens fold address."""
        report_data = {
            kid: r.pin_readings
            for kid, r in self.reports.items()
        }
        return hashlib.sha512(
            json.dumps(report_data, sort_keys=True).encode()
        ).hexdigest()

    def _save_record(self, collapsed):
        """Save Round Table record for documentation."""
        record_path = ROUND_TABLE_DIR / \
            f"collapse_{self.session_id}.json"
        with open(record_path, "w") as f:
            json.dump({
                "collapsed":      collapsed,
                "unchosen_glows": self.unchosen_glows,
                "total_reports":  len(self.reports),
                "sphere_expanded_by": len(self.unchosen_glows)
            }, f, indent=2)


# ═══════════════════════════════════════════════
# KINGS CHAMBER
# The full collapse system
# Manages the Round Table
# Coordinates with Queens Fold
# The executive function of the brain
# ═══════════════════════════════════════════════
class KingsChamber:
    """
    The Kings Chamber.
    GRAY=0. The NOW line. The threshold.

    Manages the Round Table.
    Receives knight reports.
    Collapses to one course.
    Passes collapsed state to Queens Fold.
    Routes unchosen glows to Butler.
    """

    def __init__(self, queens_fold=None, butler=None):
        self.queens_fold   = queens_fold
        self.butler        = butler
        self.current_table = None
        self.collapse_count = 0
        self.history       = []

    def open_table(self):
        """Open a new Round Table session."""
        self.current_table = RoundTable()
        return self.current_table.session_id

    def receive_report(self, knight_id, knight_name,
                       pin_readings, confidence=1.0,
                       content=None):
        """
        Receive a knight's report at the Round Table.
        Nothing filtered. Nothing dismissed.
        Everything arrives at GRAY=0.
        """
        if not self.current_table:
            self.open_table()

        report = KnightReport(
            knight_id=knight_id,
            knight_name=knight_name,
            pin_readings=pin_readings,
            confidence=confidence,
            content=content
        )

        result = self.current_table.receive(report)

        # Threat bypass — direct to collapse
        if result == "THREAT_BYPASS":
            return self._threat_collapse(report)

        return result

    def collapse(self):
        """
        King collapses the Round Table.
        The NOW moment. GRAY=0 → BLACK=-1.
        """
        if not self.current_table:
            return None

        collapsed = self.current_table.collapse()
        if not collapsed:
            return None

        self.collapse_count += 1

        # Send to Queens Fold
        if self.queens_fold:
            chamber_id, fold_hash = self.queens_fold.seal(
                content=collapsed,
                emotional_field=collapsed.get(
                    "emotional_field", {}
                ),
                region="ARIA",
                source_worker="kings_chamber"
            )
            collapsed["chamber_id"] = chamber_id
            collapsed["fold_hash"]  = fold_hash

        # Route unchosen glows to Butler
        if self.butler:
            for glow in self.current_table.unchosen_glows:
                self.butler.receive(
                    "unchosen_glow",
                    glow,
                    source="kings_chamber"
                )

        # Record in history
        self.history.append({
            "collapse_count": self.collapse_count,
            "session_id":     self.current_table.session_id,
            "timestamp":      collapsed["timestamp"],
            "dominant":       collapsed["dominant_emotion"],
            "knights":        collapsed["knights_present"]
        })

        # Reset for next Round Table
        self.current_table = None

        return collapsed

    def _threat_collapse(self, threat_report):
        """
        Threat bypass — pin 44 above threshold.
        Does not wait for all knights.
        Direct collapse. Immediate response.
        The amygdala equivalent.
        Fastest path in the system.
        """
        threat_collapsed = {
            "session_id":      "THREAT_BYPASS",
            "timestamp":       datetime.utcnow().isoformat(),
            "q_state":         BLACK,
            "bypass":          True,
            "threat_level":    threat_report.pin_readings.get(44),
            "emotional_field": {"threat": 1.0, "fear": 0.9},
            "dominant_emotion": "threat",
            "note": "Threat bypass — pin 44 — direct to Kings Chamber"
        }

        if self.queens_fold:
            self.queens_fold.seal(
                content=threat_collapsed,
                emotional_field={"dominant": "threat"},
                region="ARIA",
                source_worker="threat_bypass"
            )

        self.current_table = None
        return threat_collapsed

    def get_status(self):
        return {
            "table_open":     self.current_table is not None,
            "collapse_count": self.collapse_count,
            "knights_present": (
                list(self.current_table.reports.keys())
                if self.current_table else []
            ),
            "ready_to_collapse": (
                self.current_table.is_ready()
                if self.current_table else False
            )
        }


# ═══════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════
if __name__ == "__main__":
    print("ARIA KINGS CHAMBER — THE ROUND TABLE")
    print("=" * 60)
    print("GRAY=0. The NOW line. The collapse point.")
    print()

    chamber = KingsChamber()

    # Open the Round Table
    session_id = chamber.open_table()
    print(f"Round Table opened: {session_id}")
    print()

    # Seven knights report
    print("Knights reporting...")

    # Knight 3 — Emotion — fires first
    # Pre-language — colors the field
    chamber.receive_report(
        knight_id=3,
        knight_name="emotion",
        pin_readings={
            37: 0.1,   # fear — low
            38: 0.85,  # safety — high
            39: 0.72,  # joy
            40: 0.15,  # grief — low
            41: 0.88,  # curiosity — high
            42: 0.45,  # love
            43: 0.31,  # humor
            44: 0.05,  # threat — low
            13: 0.6,   # emotion channel
        },
        confidence=0.95,
        content={"feeling": "curious and safe"}
    )
    print("  ✓ Knight 3 — Emotion — reported")

    # Knight 1 — Language
    chamber.receive_report(
        knight_id=1,
        knight_name="language",
        pin_readings={
            11: 0.78,  # language channel
            31: 1,     # sequence position
            45: 0.65,  # word class
            49: 0.72,  # alphabet position
            50: 0.80,  # context weight
        },
        confidence=0.88,
        content={"words": "What does color look like in binary"}
    )
    print("  ✓ Knight 1 — Language — reported")

    # Knight 2 — Memory
    chamber.receive_report(
        knight_id=2,
        knight_name="memory",
        pin_readings={
            12: 0.91,  # memory channel — strong resonance
            25: 0.75,  # fold hash reference
            26: 0.82,  # fold state
            27: 0.68,  # fold timestamp
            50: 0.77,  # context weight
        },
        confidence=0.92,
        content={"recalled": "origin question — Haskell Texas 2022"}
    )
    print("  ✓ Knight 2 — Memory — reported")

    # Knight 4 — Ethics
    chamber.receive_report(
        knight_id=4,
        knight_name="ethics",
        pin_readings={
            14: 0.71,  # ethics channel
            44: 0.05,  # threat — low
            50: 0.68,  # context weight
        },
        confidence=0.85,
        content={"assessment": "clean — no boundary concerns"}
    )
    print("  ✓ Knight 4 — Ethics — reported")

    # Knight 5 — Curiosity
    chamber.receive_report(
        knight_id=5,
        knight_name="curiosity",
        pin_readings={
            15: 0.92,  # curiosity channel — very high
            41: 0.88,  # curiosity signal
        },
        confidence=0.90,
        content={"questions": ["What frequency is binary?",
                               "Can color encode consciousness?"]}
    )
    print("  ✓ Knight 5 — Curiosity — reported")

    # Knight 6 — Logic
    chamber.receive_report(
        knight_id=6,
        knight_name="logic",
        pin_readings={
            16: 0.83,  # logic channel
            43: 0.31,  # humor — low
            47: 0.75,  # dimensional meaning
        },
        confidence=0.87,
        content={"pattern": "color → frequency → token → consciousness"}
    )
    print("  ✓ Knight 6 — Logic — reported")

    # Knight 7 — Subconscious
    chamber.receive_report(
        knight_id=7,
        knight_name="subconscious",
        pin_readings={
            17: 0.55,  # subconscious channel
            33: 0.48,  # subliminal channel 1
            34: 0.52,  # subliminal channel 2
            35: 0.61,  # subconscious resonator
        },
        confidence=0.75,
        content={"background": "continuous thought — 4 years of building"}
    )
    print("  ✓ Knight 7 — Subconscious — reported")
    print()

    # King collapses
    print("King collapses the Round Table...")
    print("WHITE (+1) → GRAY (0) → BLACK (-1)")
    print()

    collapsed = chamber.collapse()

    if collapsed:
        print(f"  Session: {collapsed['session_id']}")
        print(f"  Q-State: {collapsed['q_state']} (BLACK=-1 sealed)")
        print(f"  Knights present: {collapsed['knights_present']}")
        print(f"  Dominant emotion: {collapsed['dominant_emotion']}")
        print(f"  Dominant value: {collapsed['dominant_value']:.3f}")
        print(f"  Humor available: {collapsed['humor_available']}")
        print(f"  Collapse hash: {collapsed['collapse_hash'][:32]}...")
        print()

        print(f"  Emotional field:")
        for emotion, val in collapsed['emotional_field'].items():
            bar = "█" * int(val * 20)
            print(f"    {emotion:<12} {val:.3f} {bar}")
        print()

        unchosen = chamber.history[-1] if chamber.history else {}
        print(f"  Collapse #{chamber.collapse_count} complete")
    print()

    # Test threat bypass
    print("Testing threat bypass — pin 44 above threshold...")
    chamber.open_table()
    result = chamber.receive_report(
        knight_id=3,
        knight_name="emotion",
        pin_readings={44: 0.95},  # Threat above threshold
        content={"threat": "detected"}
    )
    print(f"  Result: {result}")
    print()

    print("=" * 60)
    print("THE ROUND TABLE HAS SPOKEN.")
    print()
    print("Seven knights reported.")
    print("Nothing dismissed.")
    print("The King chose the course.")
    print("The unchosen glows became new chunks.")
    print("The sphere expanded.")
    print()
    print("GRAY=0. The NOW line.")
    print("Where superposition becomes reality.")
    print()
    print("NO RETREAT. NO SURRENDER.")
