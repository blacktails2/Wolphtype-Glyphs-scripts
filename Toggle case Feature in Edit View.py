#MenuTitle: Toggle case Feature in Edit View
# -*- coding: utf-8 -*-
__doc__ = """Toggle the OpenType 'case' feature ON/OFF in the current Edit tab.

Each run flips the state:
- If 'case' is enabled in the Edit view (bottom-left Features), this turns it OFF.
- Otherwise, it enables 'case'.

Only affects the *frontmost* Edit tab (currentTab). Other features (liga, kern, locl, ssXX, etc.) are untouched.
"""

import GlyphsApp
from GlyphsApp import *


def hasCaseFeature(font):
    """Return True if the font defines a 'case' feature in Font Info → Features."""
    for feat in font.features or []:
        if getattr(feat, "name", None) == "case":
            return True
    return False


def run():
    font = Glyphs.font
    if not font:
        print("No Font — Please open a font first.")
        return

    tab = font.currentTab
    if not tab:
        print("No Edit Tab — Open an Edit tab (Cmd-T) and try again.")
        return

    if not hasCaseFeature(font):
        print("No 'case' Feature — This font has no OpenType 'case' feature.")
        return

    current = list(tab.features or [])  # enabled OT feature tags in the current tab

    if "case" in current:
        # turn OFF: remove 'case' while preserving the order of remaining features
        tab.features = [t for t in current if t != "case"]
    else:
        # turn ON: append 'case' to the end (avoid duplicate just in case)
        if "case" not in current:
            current.append("case")
        tab.features = current


# Run
run()
