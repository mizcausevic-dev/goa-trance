# Goa Trance

Original note-only MIDI construction kits. Four kits, six core parts, two variations of each part. The parts are drums, bass, primary sequence, secondary sequence, motif, and harmonic field. Bass is monophonic. Odd-step groups are local cycles inside 4/4. They do not change the bar.

This repository is the pack. The GitHub repository is https://github.com/mizcausevic-dev/goa-trance and it is public. The catalog page is https://mizcausevic-dev.github.io/goa-trance/ .

## What you can open

- `index.html` is the file catalog. Pick a kit, then variation A or B. The lanes are drawn from the fetched MIDI.
- `media.html` is the stills page. The film sits under the pictures.
- Each kit has a 32-bar Format 1 arrangement under `midi/`. Kit 01 is `midi/k01-seven-gate/arrangement.mid`.
- Individual Format 0 parts live beside that arrangement.
- `midi/validation-Cursor.json` is the report from reopening those exact bytes.
- `preview/preview.mp3` is the primary music preview. It is 27.042 seconds in the encoded file. preview, not a master.
- `film/preview.mp4` and `film/preview.vtt` are the film. On-picture and caption text is `preview, not master`.
- `art/hero.jpg` is a 1280x720 illustration. `art/square.jpg` is 1080x1080. Neither is a photograph.

Use either the combined arrangement or the separate parts. Do not stack the part files on top of the combined file.

## Kits

- k01 Seven Gate: 142 BPM, 8 bar parts, 32 bar arrangement, E Phrygian dominant, tonic E.
- k02 Fifth Lattice: 146 BPM, 8 bar parts, 32 bar arrangement, A harmonic minor, tonic A.
- k03 Nine Pulse: 140 BPM, 8 bar parts, 32 bar arrangement, F Phrygian, tonic F.
- k04 Return Spiral: 148 BPM, 8 bar parts, 32 bar arrangement, B Phrygian, tonic B.

Core files: 48. Reference files: 0.

Drums use MIDI channel index 9, the GM channel 10, and only the mapped pitches 36 kick, 37 side stick, 38 acoustic snare, 39 clap, 40 electric snare, 42 closed hat, 46 open hat, and 49 crash. Bass is monophonic, MIDI 28 to 47, channel 4. Primary sequence is monophonic, MIDI 55 to 84, channel 0. Secondary sequence is monophonic, MIDI 48 to 79, channel 1. Motif is monophonic, MIDI 60 to 86, channel 2. Harmonic field allows four notes, MIDI 45 to 76, channel 3. C4 is 60. PPQ is 960. Meter is 4/4. A bar is 3840 ticks. Offsets are 0. Seeds identify kits and are not random draws. Generator 1.0.0.

Odd-step grouping is a local cycle. It does not change the 4/4 meter. A bar stays 3840 ticks.

- k01: Primary A groups 7 sixteenth notes, 1680 ticks. Seven bars hold 112 sixteenths, and 112 divides by 7, so the cycle meets the downbeat again at bar 8. The part ends after the first bar of the next pass. Meter stays 4/4.
- k02: Primary A groups 5 sixteenth notes, 1200 ticks. Five bars hold 80 sixteenths, so the cycle meets the downbeat at bar 6. The 8-bar part then carries 3 bars of the next pass. Meter stays 4/4.
- k03: Primary A groups 9 sixteenth notes, 2160 ticks, and sounds 120 ticks after each selected step. Nine and 16 are coprime, so the group does not reset inside one bar. It would meet the downbeat every 9 bars. The part ends at bar 8, and the cycle resets only when the part starts again. Meter stays 4/4.
- k04: Primary A attacks on groups of 3, 3, and 2 sixteenths, then the same groups again. The sum is 16 sixteenths, so the pattern resets every bar. The bar remains 3840 ticks and the meter remains 4/4.

## Preview path

The preview renders the first 16 bars of the kit 01 arrangement with `simple-synth-1.0.0`. The arrangement is 32 bars, score length 54.084 seconds, which is past the 40 second preview limit. The excerpt score length is 27.042 seconds. Tempo authority is the encoded microsecond value in the MIDI, 422535 us per quarter note. Sample positions use `floor(seconds * 44100 + 0.5)` from tick 0. Intervals are not summed. Sample-exact repeating loops at an arbitrary BPM are not promised.

The synth mapping is a simple-synth: kick and noise drums, a dull saw bass, a pulse primary sequence, a triangle secondary sequence, a sine motif, and a slow field. No program changes are encoded. A conventional GM player will normally use its default piano program for pitched channels unless configured otherwise; compatible GM channel 10 percussion is treated separately. Player behavior may vary. The mapping is not encoded in the MIDI.

Encoded MP3 settings: libmp3lame, 192 kbps. Film audio is AAC at 160 kbps re-encoded from that MP3, so the decoded film audio is not byte-identical to the MP3. Film duration probe: 27.042 seconds. MP3 container probe 27.042 seconds. MP4 probe 27.042 seconds. The film ends on a video frame, so it is slightly shorter than the MP3 container. The music is the same preview, not a different excerpt. The picture is a still illustration with rasterized disclosure text. DejaVu Sans Bold from the build machine supplies the glyphs. The font file is not in this pack.

No human listening audition was performed for this build. A sample peak is recorded in the preview manifest. It is not LUFS and it is not a true peak.

## Build

From the repository root, with Python 3.11+ and ffmpeg (libmp3lame, aac, libx264):

```bash
python3 tools/build_pack.py
python3 -m http.server 43201
```

The page is static. It is served with Python's HTTP server so the MIDI and media keep working relative paths. There is no application server and no package install. Standard library only.

`build/` holds the intermediate WAV, the procedural PPM, and the film plate. Those files are gitignored. The delivered audio is the MP3.

## Checks the validator actually runs

File existence, parse, PPQ, tempo, 4/4, end-of-track boundary, note pairing, ranges, monophonic bass and sequences, field polyphony cap of four, the drum map on channel 10, note-off before note-on at a shared tick, absence of program changes and other channel messages, departure flags against the declared pitch-class set, agreement with the canonical score, and agreement between each arrangement and the placed part files. Arrangement track count is taken from that arrangement spec. Core variations must differ in start, pitch, and duration, and variation A attack tuples must not be shared across kits. A negative overlap fixture is written outside the pack and must be rejected.

## Drafts and publication

Social captions, the X post, and the Medium article are drafts. They are not access controls. If this repository is public, the drafts are public. Do not treat them as posted to Instagram, X, or Medium.

Prepared repository description: Original note-only Goa Trance construction kits, with matched validation and a simple-synth preview.

Prepared topics: midi, goa-trance, trance, music-production, composition.

No release tag was created. `index.html` keeps its name because players and links depend on it. This page is the file catalog the pack requires.

## Limitations

Variation A parts of a kit are one set. Variation B parts are the other set. The 32-bar arrangement is the place those sets trade, in the sections named on the page. Do not stack a part file on the arrangement. The primary MP3 is bars 1-16 of kit 01, not the whole arrangement and not a master. These parts are original. They are not reconstructions of known tracks.
