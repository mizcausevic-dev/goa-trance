"""Goa Trance construction kits.

Container lengths are fixed before any note is written.
Each kit is 8-bar parts in 4/4, plus one 32-bar arrangement.
Odd-step groups are local cycles. They do not move the bar line.
A bar is 3840 ticks. PPQ is 960. Offsets are 0. Nothing is random.
"""

from __future__ import annotations

from tools.midi_io import BAR_TICKS_4_4, PPQ, bpm_to_us, effective_bpm

GENERATOR_VERSION = "1.0.0"
PACK_ID = "goa-trance"
PACK_NAME = "Goa Trance"
BAR = BAR_TICKS_4_4
PART_BARS = 8
ARRANGEMENT_BARS = 32
EXCERPT_BARS = 16

ROLE_ORDER = (
    "drums",
    "bass",
    "primary-sequence",
    "secondary-sequence",
    "motif",
    "harmonic-field",
)
SHORT = {
    "drums": "drums",
    "bass": "bass",
    "primary-sequence": "primary",
    "secondary-sequence": "secondary",
    "motif": "motif",
    "harmonic-field": "field",
}
ROLE_NAME = {
    "drums": "Drums",
    "bass": "Bass",
    "primary-sequence": "Primary Sequence",
    "secondary-sequence": "Secondary Sequence",
    "motif": "Motif",
    "harmonic-field": "Harmonic Field",
}
CHANNEL = {
    "drums": 9,
    "bass": 4,
    "primary-sequence": 0,
    "secondary-sequence": 1,
    "motif": 2,
    "harmonic-field": 3,
}
LIMITS = {
    "drums": (36, 49, 4, False),
    "bass": (28, 47, 1, True),
    "primary-sequence": (55, 84, 1, True),
    "secondary-sequence": (48, 79, 1, True),
    "motif": (60, 86, 1, True),
    "harmonic-field": (45, 76, 4, False),
}
DRUM_MAP = {
    36: "Acoustic Bass Drum",
    37: "Side Stick",
    38: "Acoustic Snare",
    39: "Hand Clap",
    40: "Electric Snare",
    42: "Closed Hi-Hat",
    46: "Open Hi-Hat",
    49: "Crash Cymbal 1",
}


class Part:
    def __init__(self, kit, role, variation):
        lo, hi, poly, mono = LIMITS[role]
        self.kit = kit
        self.role = role
        self.variation = variation
        self.part_id = f"{kit['id']}.{SHORT[role]}.{variation}"
        self.channel = CHANNEL[role]
        self.monophonic = mono
        self.max_poly = poly
        self.lo = lo
        self.hi = hi
        self.container_ticks = PART_BARS * BAR
        self.notes = []

    def add(self, start, duration, pitch, velocity, departure=False):
        end = start + duration
        if start < 0 or duration <= 0 or end > self.container_ticks:
            raise ValueError(f"{self.part_id} boundary {start}+{duration}")
        if not self.lo <= pitch <= self.hi:
            raise ValueError(f"{self.part_id} pitch {pitch}")
        if self.role == "drums" and pitch not in DRUM_MAP:
            raise ValueError(f"{self.part_id} unmapped drum {pitch}")
        if not 1 <= velocity <= 127:
            raise ValueError(f"{self.part_id} velocity {velocity}")
        active = 1
        for other in self.notes:
            o0 = other["performed_start"]
            o1 = o0 + other["duration"]
            if start < o1 and o0 < end:
                if other["pitch"] == pitch or self.monophonic:
                    raise ValueError(f"{self.part_id} overlap {pitch}@{start} with {other['pitch']}@{o0}")
                active += 1
        if active > self.max_poly:
            raise ValueError(f"{self.part_id} poly {active}")
        self.notes.append({
            "nominal_start": start,
            "offset": 0,
            "performed_start": start,
            "duration": duration,
            "pitch": pitch,
            "velocity": velocity,
            "channel": self.channel,
            "departure": departure,
        })

    def finish(self):
        ordered = sorted(self.notes, key=lambda note: (note["performed_start"], note["pitch"]))
        if len(ordered) < 8:
            raise ValueError(f"{self.part_id} too few notes")
        for index, note in enumerate(ordered, 1):
            note["id"] = f"{self.part_id}.n{index:04d}"
        return {
            "id": self.part_id,
            "study_id": self.kit["id"],
            "kit_id": self.kit["id"],
            "slug": self.kit["slug"],
            "role": self.role,
            "variation": self.variation,
            "core": True,
            "channel": self.channel,
            "file_slug": f"{SHORT[self.role]}-{self.variation}",
            "path": f"midi/{self.kit['slug']}/{SHORT[self.role]}-{self.variation}.mid",
            "monophonic": self.monophonic,
            "max_poly": self.max_poly,
            "container_ticks": self.container_ticks,
            "container_bars": PART_BARS,
            "bpm": self.kit["bpm"],
            "tempo_us": self.kit["tempo_us"],
            "notes": ordered,
        }


def vel(index, base=84):
    return min(118, base + (index % 4) * 6)


def expand(pattern, bars=PART_BARS, extra=None):
    events = []
    for bar_index in range(bars):
        origin = bar_index * BAR
        for offset, duration, pitch, velocity in pattern:
            events.append((origin + offset, duration, pitch, velocity, False))
        if extra:
            for offset, duration, pitch, velocity, departure in extra(bar_index):
                events.append((origin + offset, duration, pitch, velocity, departure))
    return events


def stepped(step, duration, phase, skip, pitches, departure_at=None, base=86):
    events = []
    container = PART_BARS * BAR
    index = 0
    written = 0
    while True:
        start = phase + index * step
        if start >= container:
            break
        if start + duration <= container and not skip(index):
            pitch = pitches[written % len(pitches)]
            departure = False
            if departure_at is not None and start == departure_at[0]:
                pitch = departure_at[1]
                departure = True
            events.append((start, duration, pitch, vel(written, base), departure))
            written += 1
        index += 1
        if index > 4000:
            raise RuntimeError("stepped sequence did not end")
    return events


def paint(part, events):
    for start, duration, pitch, velocity, departure in events:
        part.add(start, duration, pitch, velocity, departure=departure)


def kits():
    common = {
        "meter": "4/4",
        "bar_ticks": BAR,
        "ppq": PPQ,
        "part_bars": PART_BARS,
        "arrangement_bars": ARRANGEMENT_BARS,
        "stochastic_draws": 0,
    }
    rows = [
        {
            **common,
            "id": "k01",
            "slug": "k01-seven-gate",
            "title": "Seven Gate",
            "bpm": 142,
            "tonic": "E",
            "tonal_reference": "E",
            "collection_name": "E Phrygian dominant",
            "pitch_classes": [4, 5, 8, 9, 11, 0, 2],
            "spell": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
            "seed": 14201,
            "identity": "Seven Gate locks a 7-sixteenth primary sequence to a 4-on-the-floor kit and a 3-note bass group. Variation B drops the kick to half time, moves the lead onto a late eighth grid, and answers with a two-note secondary.",
            "limitations": "Play variation A parts together, or variation B parts together. The arrangement is the only place those sets trade. Odd groups do not change the 4/4 bar.",
            "departures": ["Primary B has one G4 (67) at tick 5160. G is outside E Phrygian dominant. It is one attack, then the line returns."],
            "cycles": [
                "Primary A groups 7 sixteenth notes, 1680 ticks. Seven bars hold 112 sixteenths, and 112 divides by 7, so the cycle meets the downbeat again at bar 8. The part ends after the first bar of the next pass. Meter stays 4/4.",
                "Secondary A waits one sixteenth, then groups 5. Five bars realign that delayed grid. The wait is not a meter change.",
                "Bass A sounds three sixteenths and rests the fourth. That group resets every bar because 4 sixteenths fill one beat, four times.",
                "Drums A reset every bar. Motif A resets every 2 bars. The harmonic field changes every 2 bars.",
            ],
        },
        {
            **common,
            "id": "k02",
            "slug": "k02-fifth-lattice",
            "title": "Fifth Lattice",
            "bpm": 146,
            "tonic": "A",
            "tonal_reference": "A",
            "collection_name": "A harmonic minor",
            "pitch_classes": [9, 11, 0, 2, 4, 5, 8],
            "spell": ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "G#", "A", "Bb", "B"],
            "seed": 14602,
            "identity": "Fifth Lattice starts on the secondary sequence and a galloping kick. The primary line is a 5-step lattice that enters later. Variation B answers in quarters and flags one Bb.",
            "limitations": "The opening eight bars have no primary sequence and no motif. That silence is written. It is not a missing file. Bb is a departure, not a new key.",
            "departures": [
                "Primary B bar 8, tick 28320, is Bb4 (70) for 200 ticks.",
                "Secondary B bar 8, tick 28800, is Bb4 (70) for 1000 ticks. These two notes do not overlap. Bb is outside A harmonic minor.",
            ],
            "cycles": [
                "Primary A groups 5 sixteenth notes, 1200 ticks. Five bars hold 80 sixteenths, so the cycle meets the downbeat at bar 6. The 8-bar part then carries 3 bars of the next pass. Meter stays 4/4.",
                "Secondary A groups 3 sixteenth notes. Sixteen sixteenths leave a remainder of 1, so the group does not reset each bar. It resets every 3 bars, where 48 sixteenths divide by 3.",
                "Bass A is the offbeat eighth, one bar long. Drums A gallop inside the bar. The field changes every bar.",
            ],
        },
        {
            **common,
            "id": "k03",
            "slug": "k03-nine-pulse",
            "title": "Nine Pulse",
            "bpm": 140,
            "tonic": "F",
            "tonal_reference": "F",
            "collection_name": "F Phrygian",
            "pitch_classes": [5, 6, 8, 10, 0, 1, 3],
            "spell": ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"],
            "seed": 14003,
            "identity": "Nine Pulse shifts a 9-step primary by 120 ticks and hangs a 4-bar field under it. The bass enters only at bar 9 of the arrangement. Variation B is three held attacks per bar plus one G.",
            "limitations": "The 120-tick phase sits inside the sixteenth grid. It does not move the downbeat. The 9-step cycle does not finish inside the 8-bar part.",
            "departures": ["Primary B bar 6, tick 21120, is G4 (67) for 1440 ticks. G is outside F Phrygian."],
            "cycles": [
                "Primary A groups 9 sixteenth notes, 2160 ticks, and sounds 120 ticks after each selected step. Nine and 16 are coprime, so the group does not reset inside one bar. It would meet the downbeat every 9 bars. The part ends at bar 8, and the cycle resets only when the part starts again. Meter stays 4/4.",
                "Secondary A waits 360 ticks, then groups 5 sixteenths. That late grid realigns every 5 bars. The wait does not move the bar line, and it does not copy the primary 9-step.",
                "Motif A places one attack every 2160 ticks, the same 9-sixteenth span, and resets with the part.",
                "The field holds 4 bars, then 4 bars. Drums A reset every bar on a shifted hat grid.",
            ],
        },
        {
            **common,
            "id": "k04",
            "slug": "k04-return-spiral",
            "title": "Return Spiral",
            "bpm": 148,
            "tonic": "B",
            "tonal_reference": "B",
            "collection_name": "B Phrygian",
            "pitch_classes": [11, 0, 2, 4, 6, 7, 9],
            "spell": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
            "seed": 14804,
            "identity": "Return Spiral builds the bar as 3+3+2 sixteenths, twice. The kick follows that tresillo. Variation B moves the lead to the off-sixteenths and flags one C#.",
            "limitations": "3+3+2+3+3+2 equals 16 sixteenths, so the odd groups reset every bar. They do not create a new meter. C# is one attack at the end of variation B.",
            "departures": ["Primary B bar 8, tick 30480, is C#5 (73) for 150 ticks. C# is outside B Phrygian."],
            "cycles": [
                "Primary A attacks on groups of 3, 3, and 2 sixteenths, then the same groups again. The sum is 16 sixteenths, so the pattern resets every bar. The bar remains 3840 ticks and the meter remains 4/4.",
                "Drums A place the kick on the tresillo eighths, which is the same 3+3+2 shape in eighth notes, and that also resets every bar.",
                "Secondary A resets every bar. Motif A alternates even and odd bars. The field staggers inside the bar and restarts each bar in variation A.",
            ],
        },
    ]
    for row in rows:
        row["tempo_us"] = bpm_to_us(row["bpm"])
        row["effective_bpm"] = effective_bpm(row["tempo_us"])
    return rows


def _events(kit):
    kid = kit["id"]
    if kid == "k01":
        return {
            "drums": {
                "a": expand(
                    [(0, 180, 36, 114), (960, 180, 36, 110), (1920, 180, 36, 112), (2880, 180, 36, 108),
                     (480, 90, 42, 72), (1440, 90, 42, 76), (2400, 90, 42, 74), (3360, 90, 42, 70),
                     (960, 200, 38, 104), (2880, 200, 38, 100)],
                    extra=lambda bar: [(0, 480, 49, 96, False)] if bar == 7 else [],
                ),
                "b": expand(
                    [(0, 320, 36, 116), (1680, 100, 36, 90), (1920, 320, 36, 112),
                     (960, 400, 40, 108), (2880, 400, 40, 104),
                     (1440, 240, 46, 84), (3360, 240, 46, 80),
                     (480, 70, 37, 68), (2400, 70, 37, 66)],
                ),
            },
            "bass": {
                "a": stepped(240, 190, 0, lambda i: i % 4 == 3, [40, 28, 28, 28, 28, 28, 28, 28]),
                "b": stepped(480, 220, 240, lambda i: False, [29, 35]),
            },
            "primary-sequence": {
                "a": stepped(240, 210, 0, lambda i: i % 7 == 6, [64, 68, 71, 74, 76, 72, 69, 65]),
                "b": stepped(480, 300, 360, lambda i: False, [76, 71, 68, 64, 65, 62], (5160, 67)),
            },
            "secondary-sequence": {
                "a": stepped(240, 180, 240, lambda i: i % 5 == 4, [60, 62, 64, 65, 68, 69, 71]),
                "b": expand([(0, 1440, 64, 88), (1920, 900, 72, 92)]),
            },
            "motif": {
                "a": [],
                "b": [],
            },
            "harmonic-field": {"a": [], "b": []},
        }
    if kid == "k02":
        return {
            "drums": {
                "a": expand(
                    [(0, 150, 36, 116), (480, 150, 36, 100), (1920, 150, 36, 114), (2400, 150, 36, 98),
                     (240, 70, 42, 70), (480, 70, 42, 68), (1200, 70, 42, 72), (1440, 70, 42, 74),
                     (2160, 70, 42, 70), (2400, 70, 42, 66), (3120, 70, 42, 72), (3360, 70, 42, 64),
                     (960, 260, 38, 106), (2880, 260, 38, 102)],
                ),
                "b": expand(
                    [(0, 100, 36, 112), (960, 100, 36, 108), (1920, 100, 36, 114), (2880, 100, 36, 110),
                     (720, 200, 46, 80), (1680, 200, 46, 78), (2640, 200, 46, 82), (3600, 200, 46, 76),
                     (1920, 500, 40, 104), (480, 120, 39, 96)],
                ),
            },
            "bass": {
                "a": expand([(480, 400, 33, 100), (1440, 400, 40, 92), (2400, 400, 33, 98), (3360, 400, 40, 90)]),
                "b": expand([(0, 700, 33, 104), (1920, 500, 36, 96), (2880, 300, 40, 88)]),
            },
            "primary-sequence": {
                "a": stepped(240, 180, 0, lambda i: i % 5 == 4, [69, 76, 72, 81, 77, 74, 71, 80]),
                "b": [],
            },
            "secondary-sequence": {
                "a": stepped(240, 200, 0, lambda i: i % 3 == 2, [57, 60, 64, 59, 62, 65, 68]),
                "b": [],
            },
            "motif": {
                "a": expand([(960, 720, 69, 100), (2880, 240, 76, 108)]),
                "b": expand([(480, 1800, 72, 90), (2880, 600, 65, 96)]),
            },
            "harmonic-field": {"a": [], "b": []},
        }
    if kid == "k03":
        return {
            "drums": {
                "a": expand(
                    [(0, 240, 36, 116), (1920, 240, 36, 112),
                     (120, 80, 42, 74), (600, 80, 42, 70), (1080, 80, 42, 72), (1560, 80, 42, 68),
                     (2040, 80, 42, 74), (2520, 80, 42, 70), (3000, 80, 42, 72), (3480, 80, 42, 66),
                     (960, 160, 39, 102), (2880, 160, 39, 98)],
                ),
                "b": expand(
                    [(0, 140, 36, 114), (960, 140, 36, 110), (1920, 140, 36, 116), (2880, 140, 36, 108),
                     (480, 110, 42, 76), (1440, 110, 42, 74), (2400, 110, 42, 78), (3360, 110, 42, 72),
                     (960, 280, 40, 104), (2880, 280, 40, 100)],
                    extra=lambda bar: [(0, 700, 49, 92, False)] if bar in (3, 7) else [],
                ),
            },
            "bass": {
                "a": expand([(0, 500, 29, 108), (960, 280, 32, 90), (1440, 500, 36, 104), (2400, 280, 39, 88), (2880, 500, 29, 100)]),
                "b": expand([(480, 350, 30, 96), (1440, 350, 34, 92), (2400, 700, 37, 100), (3360, 200, 41, 84)]),
            },
            "primary-sequence": {
                "a": stepped(240, 160, 120, lambda i: i % 9 in (3, 8), [65, 68, 70, 73, 75, 77, 72, 66]),
                "b": [],
            },
            "secondary-sequence": {
                "a": stepped(240, 220, 360, lambda i: i % 5 == 4, [56, 58, 60, 61, 63, 65, 66]),
                "b": [],
            },
            "motif": {
                "a": stepped(2160, 400, 0, lambda i: False, [77, 73, 68]),
                "b": [],
            },
            "harmonic-field": {"a": [], "b": []},
        }
    if kid == "k04":
        return {
            "drums": {
                "a": expand(
                    [(0, 220, 36, 116), (1440, 220, 36, 108), (2880, 220, 36, 112),
                     (240, 60, 42, 70), (480, 60, 42, 68), (960, 60, 42, 72), (1200, 60, 42, 74),
                     (1680, 60, 42, 70), (1920, 60, 42, 66), (2400, 60, 42, 72), (2640, 60, 42, 68),
                     (3120, 60, 42, 70), (3360, 60, 42, 64),
                     (2880, 300, 40, 104)],
                    extra=lambda bar: [(3360, 200, 46, 86, False)] if bar % 2 == 0 else [],
                ),
                "b": expand(
                    [(0, 180, 36, 114), (1920, 180, 36, 110),
                     (960, 240, 38, 106), (2880, 240, 38, 102)]
                    + [(step * 240, 50, 42, 64 + (step % 3) * 4) for step in range(16)],
                ),
                },
            "bass": {
                "a": expand(
                    [(0, 1200, 35, 110)]
                    + [(1920 + step * 240, 150, pitch, 92) for step, pitch in enumerate([38, 40, 42, 43, 45, 42, 40])],
                ),
                "b": expand([(step * 480, 160, 35 if step % 2 == 0 else 40, 96) for step in range(8)]),
            },
            "primary-sequence": {
                "a": expand(
                    [(0, 640, 71, 100), (720, 640, 74, 96), (1440, 400, 78, 104),
                     (1920, 640, 81, 98), (2640, 640, 83, 108), (3360, 400, 79, 94)],
                ),
                "b": [],
            },
            "secondary-sequence": {
                "a": expand([(0, 360, 64, 90), (720, 160, 67, 84), (960, 360, 71, 96), (1920, 360, 66, 88), (2640, 160, 62, 82), (2880, 360, 69, 94)]),
                "b": expand([(0, 2880, 71, 86), (3360, 200, 67, 98)]),
            },
            "motif": {
                "a": [],
                "b": expand([(1920, 960, 69, 100), (3360, 360, 78, 108)]),
            },
            "harmonic-field": {"a": [], "b": []},
        }
    raise KeyError(kid)


def _finish_specials(kit, bucket):
    kid = kit["id"]
    if kid == "k01":
        motif_a = []
        for bar in range(PART_BARS):
            origin = bar * BAR
            if bar % 2 == 0:
                motif_a.append((origin, 960, 76, 104, False))
                motif_a.append((origin + 1920, 480, 71, 96, False))
            else:
                motif_a.append((origin + 960, 1440, 68, 90, False))
        bucket["motif"]["a"] = motif_a
        motif_b = []
        for bar in (2, 6):
            origin = bar * BAR
            for offset, pitch in ((0, 65), (240, 64), (480, 62), (960, 60), (1200, 69), (1440, 68)):
                motif_b.append((origin + offset, 140, pitch, 92, False))
        bucket["motif"]["b"] = motif_b
        field_a = []
        for origin, duration, pitches in (
            (0, 7000, (52, 56, 59, 62)),
            (2 * BAR, 7000, (57, 60, 64, 69)),
            (4 * BAR, 6400, (59, 62, 65, 68)),
            (6 * BAR, 7000, (52, 57, 60, 64)),
        ):
            for pitch in pitches:
                field_a.append((origin, duration, pitch, 78, False))
        bucket["harmonic-field"]["a"] = field_a
        field_b = []
        voicings = (
            (52, 59, 64, 71),
            (53, 57, 65, 69),
            (56, 60, 68, 72),
            (50, 57, 62, 69),
        )
        for block, pitches in enumerate(voicings):
            origin = block * 2 * BAR
            for offset, pitch in zip((0, 480, 960, 1440), pitches):
                field_b.append((origin + offset, 2400, pitch, 82, False))
        bucket["harmonic-field"]["b"] = field_b
    elif kid == "k02":
        primary_b = []
        for bar in range(PART_BARS):
            origin = bar * BAR
            specs = ((0, 800, 69), (960, 200, 72), (1440, 200, 76), (2400, 600, 81))
            for offset, duration, pitch in specs:
                departure = bar == 7 and offset == 1440
                primary_b.append((origin + offset, duration, 70 if departure else pitch, 98, departure))
        bucket["primary-sequence"]["b"] = primary_b
        secondary_b = []
        for bar in range(PART_BARS):
            origin = bar * BAR
            secondary_b.append((origin + 480, 600, 64, 90, False))
            departure = bar == 7
            secondary_b.append((origin + 1920, 1000, 70 if departure else 68, 94, departure))
        bucket["secondary-sequence"]["b"] = secondary_b
        field_a = []
        chords = (
            (57, 60, 64, 69),
            (50, 57, 62, 65),
            (52, 56, 59, 64),
            (45, 60, 64, 76),
        )
        for bar in range(PART_BARS):
            for pitch in chords[bar % 4]:
                field_a.append((bar * BAR, 3360, pitch, 76, False))
        bucket["harmonic-field"]["a"] = field_a
        field_b = []
        long = (
            (0, (48, 52, 57, 64)),
            (2 * BAR, (50, 53, 62, 69)),
            (4 * BAR, (56, 59, 68, 71)),
            (6 * BAR, (45, 60, 65, 72)),
        )
        for origin, pitches in long:
            for pitch in pitches:
                field_b.append((origin, 7200, pitch, 74, False))
        bucket["harmonic-field"]["b"] = field_b
    elif kid == "k03":
        primary_b = []
        cycle = (77, 70, 65)
        written = 0
        for bar in range(PART_BARS):
            origin = bar * BAR
            for offset, duration in ((0, 480), (960, 480), (1920, 1440)):
                departure = bar == 5 and offset == 1920
                pitch = 67 if departure else cycle[written % 3]
                primary_b.append((origin + offset, duration, pitch, 96, departure))
                written += 1
        bucket["primary-sequence"]["b"] = primary_b
        secondary_b = []
        for bar in range(PART_BARS):
            origin = bar * BAR
            runs = (240, 480, 720, 960, 1200) if bar % 2 == 0 else (2160, 2400, 2640, 2880, 3120)
            for index, offset in enumerate(runs):
                secondary_b.append((origin + offset, 120, (65, 68, 72, 65, 68)[index], 88, False))
        bucket["secondary-sequence"]["b"] = secondary_b
        motif_b = []
        for bar in (0, 4):
            origin = bar * BAR
            for offset, duration, pitch in (
                (0, 300, 66), (480, 600, 70), (1440, 400, 72), (2400, 200, 75), (3360, 300, 77),
            ):
                motif_b.append((origin + offset, duration, pitch, 98, False))
        bucket["motif"]["b"] = motif_b
        field_a = []
        for origin, pitches in ((0, (53, 56, 60, 63)), (4 * BAR, (49, 53, 56, 60))):
            for pitch in pitches:
                field_a.append((origin, 14400, pitch, 72, False))
        bucket["harmonic-field"]["a"] = field_a
        field_b = []
        stab = (
            (58, 61, 65, 68),
            (58, 61, 65, 68),
            (51, 56, 60, 66),
            (51, 56, 60, 66),
            (53, 56, 63, 58),
            (53, 56, 63, 70),
            (49, 56, 61, 65),
            (49, 56, 61, 65),
        )
        for bar, pitches in enumerate(stab):
            for pitch in pitches:
                field_b.append((bar * BAR + 480, 600, pitch, 84, False))
        bucket["harmonic-field"]["b"] = field_b
    elif kid == "k04":
        primary_a = []
        cycle = (71, 74, 78, 81, 83, 79, 76, 72)
        pattern = ((0, 640), (720, 640), (1440, 400), (1920, 640), (2640, 640), (3360, 400))
        written = 0
        for bar in range(PART_BARS):
            origin = bar * BAR
            for offset, duration in pattern:
                primary_a.append((origin + offset, duration, cycle[written % len(cycle)], 100, False))
                written += 1
        bucket["primary-sequence"]["a"] = primary_a
        primary_b = []
        pitches = (83, 79, 76, 74)
        written = 0
        for bar in range(PART_BARS):
            origin = bar * BAR
            for step in range(8):
                offset = 240 + step * 480
                departure = bar == 7 and step == 7
                pitch = 73 if departure else pitches[written % 4]
                primary_b.append((origin + offset, 150, pitch, 94, departure))
                written += 1
        bucket["primary-sequence"]["b"] = primary_b
        motif_a = []
        for bar in range(PART_BARS):
            origin = bar * BAR
            if bar % 2 == 0:
                motif_a.append((origin, 1440, 71, 102, False))
            else:
                motif_a.append((origin + 480, 200, 76, 96, False))
                motif_a.append((origin + 960, 200, 74, 90, False))
                motif_a.append((origin + 1440, 200, 71, 94, False))
        bucket["motif"]["a"] = motif_a
        field_a = []
        for bar in range(PART_BARS):
            origin = bar * BAR
            for offset, pitch in ((0, 47), (240, 52), (720, 54), (1200, 57)):
                field_a.append((origin + offset, 1800, pitch, 76, False))
        bucket["harmonic-field"]["a"] = field_a
        field_b = []
        holds = (
            (0, (59, 64, 67, 71)),
            (2 * BAR, (60, 62, 66, 69)),
            (4 * BAR, (52, 55, 59, 64)),
            (6 * BAR, (47, 54, 59, 66)),
        )
        for origin, pitches in holds:
            for pitch in pitches:
                field_b.append((origin, 6000, pitch, 74, False))
        bucket["harmonic-field"]["b"] = field_b


FORMS = {
    "k01": [
        ("Gate", 0, [("drums", "a"), ("bass", "a"), ("primary-sequence", "a"), ("motif", "a")]),
        ("Open", 8, [("drums", "a"), ("bass", "a"), ("primary-sequence", "a"), ("secondary-sequence", "a"), ("motif", "a"), ("harmonic-field", "a")]),
        ("Turn", 16, [("drums", "b"), ("bass", "b"), ("primary-sequence", "b"), ("secondary-sequence", "b"), ("motif", "b")]),
        ("Return", 24, [("drums", "b"), ("bass", "a"), ("primary-sequence", "a"), ("secondary-sequence", "a"), ("motif", "b"), ("harmonic-field", "b")]),
    ],
    "k02": [
        ("Lattice", 0, [("drums", "a"), ("bass", "a"), ("secondary-sequence", "a")]),
        ("Fifth", 8, [("drums", "a"), ("bass", "a"), ("primary-sequence", "a"), ("secondary-sequence", "a"), ("motif", "a")]),
        ("Break", 16, [("drums", "b"), ("bass", "b"), ("primary-sequence", "b"), ("secondary-sequence", "b"), ("motif", "b"), ("harmonic-field", "a")]),
        ("Close", 24, [("drums", "a"), ("bass", "b"), ("primary-sequence", "a"), ("motif", "b"), ("harmonic-field", "b")]),
    ],
    "k03": [
        ("Pulse", 0, [("drums", "a"), ("primary-sequence", "a"), ("harmonic-field", "a")]),
        ("Answer", 8, [("drums", "a"), ("bass", "a"), ("primary-sequence", "a"), ("secondary-sequence", "a"), ("motif", "a")]),
        ("Shift", 16, [("drums", "b"), ("bass", "b"), ("primary-sequence", "b"), ("secondary-sequence", "b"), ("harmonic-field", "b")]),
        ("Spiral", 24, [("drums", "b"), ("bass", "a"), ("secondary-sequence", "b"), ("motif", "b"), ("harmonic-field", "a")]),
    ],
    "k04": [
        ("Root", 0, [("drums", "a"), ("bass", "a"), ("motif", "a")]),
        ("Weave", 8, [("drums", "a"), ("bass", "a"), ("primary-sequence", "a"), ("secondary-sequence", "a"), ("harmonic-field", "a")]),
        ("Other", 16, [("drums", "b"), ("bass", "b"), ("primary-sequence", "b"), ("motif", "b")]),
        ("Return", 24, [("drums", "a"), ("bass", "b"), ("primary-sequence", "a"), ("secondary-sequence", "b"), ("motif", "a"), ("harmonic-field", "b")]),
    ],
}


def _sig(notes):
    return tuple(sorted((note["performed_start"], note["pitch"], note["duration"]) for note in notes))


def _attacks(notes):
    return tuple(sorted((note["performed_start"], note["pitch"]) for note in notes))


def assert_collections(catalog_kits, parts):
    allowed = {kit["id"]: set(kit["pitch_classes"]) for kit in catalog_kits}
    departures = []
    for part in parts:
        if part["role"] == "drums":
            continue
        pool = allowed[part["kit_id"]]
        for note in part["notes"]:
            inside = (note["pitch"] % 12) in pool
            if note["departure"] and inside:
                raise ValueError(f"{part['id']} departure {note['pitch']} is inside the collection")
            if not note["departure"] and not inside:
                raise ValueError(f"{part['id']} note {note['pitch']} left the collection")
            if note["departure"]:
                departures.append((part["id"], note["pitch"], note["performed_start"]))
    expected = {
        ("k01.primary.b", 67, 5160),
        ("k02.primary.b", 70, 28320),
        ("k02.secondary.b", 70, 28800),
        ("k03.primary.b", 67, 21120),
        ("k04.primary.b", 73, 30480),
    }
    if set(departures) != expected:
        raise ValueError(f"departures {departures}")


def assert_identities(parts):
    by_role = {}
    signatures = {}
    for part in parts:
        by_role.setdefault(part["role"], {}).setdefault(part["kit_id"], {})[part["variation"]] = part
        signature = _sig(part["notes"])
        if signature in signatures:
            raise ValueError(f"{part['id']} duplicates {signatures[signature]}")
        signatures[signature] = part["id"]
    report = []
    for role, kits_map in by_role.items():
        attack_seen = {}
        start_seen = {}
        for kit_id, variations in kits_map.items():
            left = variations["a"]["notes"]
            right = variations["b"]["notes"]
            starts_a = {note["performed_start"] for note in left}
            starts_b = {note["performed_start"] for note in right}
            pitches_a = {note["pitch"] for note in left}
            pitches_b = {note["pitch"] for note in right}
            durations_a = {note["duration"] for note in left}
            durations_b = {note["duration"] for note in right}
            if starts_a == starts_b or pitches_a == pitches_b or durations_a == durations_b:
                raise ValueError(f"{kit_id} {role} variation is not distinct in start, pitch, and duration")
            if len(starts_a ^ starts_b) < 4:
                raise ValueError(f"{kit_id} {role} start sets barely differ")
            attacks = _attacks(left)
            starts = tuple(sorted(note["performed_start"] for note in left))
            if attacks in attack_seen:
                raise ValueError(f"{kit_id} {role} A attacks repeat {attack_seen[attacks]}")
            if starts in start_seen:
                raise ValueError(f"{kit_id} {role} A starts repeat {start_seen[starts]}")
            attack_seen[attacks] = kit_id
            start_seen[starts] = kit_id
            report.append({
                "kit_id": kit_id,
                "role": role,
                "a": len(left),
                "b": len(right),
                "start_delta": len(starts_a ^ starts_b),
                "pitch_delta": len(pitches_a ^ pitches_b),
                "duration_delta": len(durations_a ^ durations_b),
            })
    return {
        "kits": report,
        "method": "Per core role, A and B differ in start, pitch, and duration. Variation A attack tuples are not shared across kits. Velocity is not the difference.",
    }


def _arrangement(kit, parts_by_id):
    sections = []
    placements = {role: [] for role in ROLE_ORDER}
    for name, start, voices in FORMS[kit["id"]]:
        present = []
        for role, variation in voices:
            part_id = f"{kit['id']}.{SHORT[role]}.{variation}"
            if part_id not in parts_by_id:
                raise KeyError(part_id)
            placements[role].append({"source_part": part_id, "start_bar": start, "variation": variation})
            present.append(part_id)
        sections.append({"name": name, "start_bar": start, "bars": 8, "parts": present})
    for role, items in placements.items():
        spans = []
        for item in items:
            span = (item["start_bar"], item["start_bar"] + PART_BARS)
            for other in spans:
                if span[0] < other[1] and other[0] < span[1]:
                    raise ValueError(f"{kit['id']} {role} placements overlap")
            spans.append(span)
        if not items:
            raise ValueError(f"{kit['id']} {role} missing from the arrangement")
    tracks = [{"name": "Conductor", "source_part": None, "placements": None, "channel": None, "role": None}]
    for role in ROLE_ORDER:
        tracks.append({
            "name": ROLE_NAME[role],
            "role": role,
            "channel": CHANNEL[role],
            "source_part": None,
            "placements": placements[role],
        })
    return {
        "id": f"{kit['id']}-arrangement",
        "kit_id": kit["id"],
        "path": f"midi/{kit['slug']}/arrangement.mid",
        "format": 1,
        "container_ticks": ARRANGEMENT_BARS * BAR,
        "container_bars": ARRANGEMENT_BARS,
        "bpm": kit["bpm"],
        "tempo_us": kit["tempo_us"],
        "meter": "4/4",
        "description": f"{kit['title']} 32-bar arrangement. Parts are placed in 8-bar sections. Tempo and meter stay on the conductor.",
        "sections": sections,
        "tracks": tracks,
    }


def _excerpt_ok(arrangement, parts_by_id):
    end = EXCERPT_BARS * BAR
    for track in arrangement["tracks"]:
        for placement in track.get("placements") or []:
            part = parts_by_id[placement["source_part"]]
            shift = placement["start_bar"] * BAR
            for note in part["notes"]:
                start = note["performed_start"] + shift
                stop = start + note["duration"]
                if start < end < stop:
                    raise ValueError(f"excerpt split {part['id']} at {start}")


def compose():
    catalog_kits = kits()
    parts = []
    for kit in catalog_kits:
        bucket = _events(kit)
        _finish_specials(kit, bucket)
        for role in ROLE_ORDER:
            for variation in ("a", "b"):
                part = Part(kit, role, variation)
                paint(part, bucket[role][variation])
                parts.append(part.finish())
    assert_collections(catalog_kits, parts)
    identity = assert_identities(parts)
    if len(parts) != 48 or any(not part["core"] for part in parts):
        raise ValueError("expected 48 core parts")
    by_id = {part["id"]: part for part in parts}
    arrangements = [_arrangement(kit, by_id) for kit in catalog_kits]
    for arrangement in arrangements:
        _excerpt_ok(arrangement, by_id)
    preview = arrangements[0]
    excerpt_ticks = EXCERPT_BARS * BAR
    excerpt_seconds = (excerpt_ticks / PPQ) * (preview["tempo_us"] / 1_000_000)
    full_seconds = (preview["container_ticks"] / PPQ) * (preview["tempo_us"] / 1_000_000)
    if not 10 <= excerpt_seconds <= 40:
        raise ValueError(f"excerpt {excerpt_seconds}")
    if full_seconds <= 40:
        raise ValueError("32-bar arrangement unexpectedly fits the preview limit")
    catalog = {
        "pack_id": PACK_ID,
        "pack_name": PACK_NAME,
        "catalog_version": GENERATOR_VERSION,
        "generator_version": GENERATOR_VERSION,
        "kind": "construction-kit",
        "ppq": PPQ,
        "c4": 60,
        "meter": {"numerator": 4, "denominator": 4, "bar_ticks": BAR},
        "part_bars": PART_BARS,
        "arrangement_bars": ARRANGEMENT_BARS,
        "excerpt_bars": EXCERPT_BARS,
        "drum_channel_index": 9,
        "drum_channel_number": 10,
        "drum_map": {str(pitch): name for pitch, name in sorted(DRUM_MAP.items())},
        "channels": CHANNEL,
        "core_roles": list(ROLE_ORDER),
        "note_policy": "Note-only MIDI. No program changes, controllers, pitch bend, or sound-design messages.",
        "microtiming": "offset is 0; performed_start = nominal_start",
        "odd_step": "Odd-step grouping is a local cycle. It does not change the 4/4 meter. A bar stays 3840 ticks.",
        "stochastic_draws": 0,
        "seed_meaning": "Seeds identify kits. Nothing is random.",
        "core_part_count": 48,
        "reference_part_count": 0,
        "range_statement": (
            "Drums use MIDI channel index 9, the GM channel 10, and only the mapped pitches "
            "36 kick, 37 side stick, 38 acoustic snare, 39 clap, 40 electric snare, 42 closed hat, "
            "46 open hat, and 49 crash. Bass is monophonic, MIDI 28 to 47, channel 4. "
            "Primary sequence is monophonic, MIDI 55 to 84, channel 0. "
            "Secondary sequence is monophonic, MIDI 48 to 79, channel 1. "
            "Motif is monophonic, MIDI 60 to 86, channel 2. "
            "Harmonic field allows four notes, MIDI 45 to 76, channel 3. C4 is 60."
        ),
        "kits": [{
            key: kit[key] for key in (
                "id", "slug", "title", "bpm", "tempo_us", "effective_bpm", "part_bars", "arrangement_bars",
                "meter", "bar_ticks", "tonic", "tonal_reference", "collection_name", "pitch_classes",
                "spell", "departures", "seed", "identity", "limitations", "cycles", "stochastic_draws",
            )
        } for kit in catalog_kits],
        "parts": [{
            "id": part["id"],
            "study_id": part["study_id"],
            "kit_id": part["kit_id"],
            "role": part["role"],
            "variation": part["variation"],
            "core": part["core"],
            "channel": part["channel"],
            "path": part["path"],
            "notes": len(part["notes"]),
            "container_bars": part["container_bars"],
            "bpm": part["bpm"],
            "monophonic": part["monophonic"],
        } for part in parts],
        "arrangements": arrangements,
        "arrangement": preview,
        "preview_excerpt": {
            "kit_id": "k01",
            "arrangement_path": preview["path"],
            "bars": "1-16 of the 32-bar arrangement",
            "start_tick": 0,
            "end_tick": excerpt_ticks,
            "score_seconds": excerpt_seconds,
            "full_arrangement_seconds": full_seconds,
            "reason": "The 32-bar arrangement is longer than 40 seconds, so the primary preview is the first 16 bars.",
        },
        "stack_warning": "Use either the combined arrangement or the separate parts. Do not stack the part files on top of the combined file.",
    }
    score = {
        "pack_id": PACK_ID,
        "generator_version": GENERATOR_VERSION,
        "ppq": PPQ,
        "parts": parts,
        "arrangements": arrangements,
        "arrangement": preview,
        "excerpt": catalog["preview_excerpt"],
        "identity_check": identity,
    }
    return {"catalog": catalog, "score": score}
