# Goa Trance is a note-only MIDI construction kit

Four kits, two variations on every core part, and a 16-bar simple-synth excerpt that is not a master

DRAFT. The GitHub repository is https://github.com/mizcausevic-dev/goa-trance and it is public. The catalog page is https://mizcausevic-dev.github.io/goa-trance/ .

Tags: midi, goa, trance, music-production, composition

The pack is four coordinated kits in 4/4. The kits are Seven Gate at 142 BPM, Fifth Lattice at 146, Nine Pulse at 140, and Return Spiral at 148. Each kit has six parts: drums, bass, primary sequence, secondary sequence, motif, and harmonic field. Every one of those parts is core, and every core part has two variations. That is 48 files. There is no reference-only count. Part files are 8 bars. Each kit also has one 32-bar arrangement.

A variation has to change the part. Holding the same line and only editing velocity does not count. For each core role, variation A and variation B differ in start times, pitches, and durations. Variation A attack tuples are not shared across the four kits. Seven Gate uses a 7-sixteenth primary cycle. Fifth Lattice uses a 5-step primary and a 3-step secondary. Nine Pulse shifts a 9-step line by 120 ticks. Return Spiral groups 3+3+2 sixteenths inside the bar. Those odd groups do not change the meter. A bar stays 3840 ticks.

Bass is monophonic. The primary sequence, secondary sequence, and motif are monophonic too. The harmonic field may hold four notes. Drums are GM channel 10, MIDI channel index 9, with an explicit map: 36 kick, 37 side stick, 38 acoustic snare, 39 clap, 40 electric snare, 42 closed hat, 46 open hat, 49 crash. C4 is 60. The resolution is 960 ticks per quarter note. Offsets are 0. Seeds name the kits. Nothing is random. A few variation B attacks leave the mode on purpose and are flagged: G in Seven Gate, Bb in Fifth Lattice, G in Nine Pulse, C# in Return Spiral.

No program changes are encoded. A conventional GM player will normally use its default piano program for pitched channels unless configured otherwise; compatible GM channel 10 percussion is treated separately. Player behavior may vary.

Filters, delay, and distortion are not in the files. The preview synth is a simple-synth: a short kick, noise for hats and snare, a dull saw for the bass, a pulse for the primary sequence, a triangle for the secondary sequence, a sine for the motif, and a slow tone for the field. That mapping is documented. It is not a program change.

The primary preview is bars 1-16 of Seven Gate at 142 BPM, not the 32-bar arrangement. The MP3 is 27.042 seconds. The arrangement itself is 32 bars, about 54.085 seconds, which is past the 40-second preview limit, so those later bars stay in the MIDI and are not in the MP3. preview, not a master. The film takes its audio from that preview file and shows the words preview, not master on the picture and in the WebVTT captions.

No human listening audition was performed for this build. The validator reopened the MIDI bytes and compared them with the canonical score. That is a structural check. The sample peak written beside the preview is the peak of the integer mix. It is not LUFS and it is not a true-peak reading. Nothing in this build is claimed as a master.

The stills are procedural illustrations of a 7-step cycle. Lime bars are the sounding steps. The saffron bar is the step that resets the group. They are not photographs of a session or of performers.

When a public URL exists, use either the combined arrangement or the separate parts. Use either the combined arrangement or the separate parts. Do not stack the part files on top of the combined file.

Call to action: the MIDI, the matched report, and the preview belong together. Do not publish this draft to Medium, Instagram, or X from the draft files alone.
