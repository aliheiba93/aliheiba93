# Real Video Profile

The supplied file `ScreenRecording_08-25-202609-48-24_1(2).mov` is a valid QuickTime/MOV container with H.264 video and AAC audio. The video stream is 1288x634, approximately 60 FPS, 366 frames, and 6.118 seconds.

Visual inspection shows a fixed top-down camera, a dark purple-gray stone background, three visually similar wooden barrels, and a faceted glowing red jewel that acts as the ball evidence. The barrels move quickly and occlude one another during the shuffle. There are no visible UI labels or text in the source.

Implementation implications: use `cup_or_barrel` for the wooden barrels and `ball` for the jewel; the jewel's red appearance is only an optional evidence cue and must not be the sole decision rule. The production detector should be trained on this rendered style, including barrel rim, body, motion blur, overlap, and jewel glow. The current bundled detector remains a test-only backend and does not claim accuracy on this video.
