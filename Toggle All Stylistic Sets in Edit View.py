#MenuTitle: Toggle All Stylistic Sets in Edit View
# -*- coding: utf-8 -*-
__doc__ = """Toggle all stylistic set features (ss01–ss20) ON/OFF in the current Edit tab.

Each run flips the state:
- If all ssXX present in the font are currently enabled in the Edit view (bottom-left Features),
  the script turns them all OFF.
- Otherwise, it enables all available ssXX features.

Only affects the *frontmost* Edit tab (currentTab), leaving other features (liga, kern, locl, etc.) untouched.
"""

import re
import GlyphsApp
from GlyphsApp import *

SS_PATTERN = re.compile(r"^ss\d{2}$")  # OpenType defines ss01–ss20


def stylisticSetTags(font):
    """Return a sorted list of ssXX tags that exist in the font's Features.
    Uses GSFeature.name (the OT tag)."""
    tags = []
    for feat in font.features or []:
        name = getattr(feat, "name", None)
        if name and SS_PATTERN.match(name):
            tags.append(name)
    # unique + sorted for deterministic order
    return sorted(set(tags))


def run():
    font = Glyphs.font
    if not font:
        Message("No Font", "Please open a font first.")
        return

    tab = font.currentTab
    if not tab:
        Message("No Edit Tab", "Open an Edit tab (Cmd-T) and try again.")
        return

    ss_tags = stylisticSetTags(font)
    if not ss_tags:
        Message("No ssXX Features", "This font has no stylistic set features (ss01–ss20).")
        return

    current = list(tab.features or [])  # list of enabled OT feature tags
    current_set = set(current)

    # Decide action: if *all* ssXX are already active → turn OFF; else turn ON
    if set(ss_tags).issubset(current_set):
        # turn OFF: remove all ssXX while preserving the order of remaining features
        new_features = [t for t in current if t not in ss_tags]
        tab.features = new_features
        Glyphs.showNotification("Stylistic Sets", "Turned OFF: %s" % ", ".join(ss_tags))
    else:
        # turn ON: add any missing ssXX at the end (do not duplicate)
        new_features = current[:]
        for tag in ss_tags:
            if tag not in current_set:
                new_features.append(tag)
        tab.features = new_features
        Glyphs.showNotification("Stylistic Sets", "Turned ON: %s" % ", ".join(ss_tags))


# Run
run()
