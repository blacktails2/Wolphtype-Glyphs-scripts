#MenuTitle: Monospaced Figure from Components…
# -*- coding: utf-8 -*-
__doc__ = """Create monospaced figure glyphs (.tf or .tosf) for *selected masters* by
placing the corresponding source glyph as a component and distributing the
width difference evenly to left and right sidebearings.

This version remembers your settings using **Glyphs.defaults** in the same
style as other Wolphtype scripts—*only the preference save/load logic has been
added; all layout values (spaceX, spaceY, etc.) remain untouched.*
"""

import GlyphsApp
from GlyphsApp import *  # noqa: F403
from vanilla import FloatingWindow, RadioGroup, EditText, Button, TextBox, CheckBox

PREF_PREFIX = "com.Wolphtype.MonospacedFigures."
PREF_ONLY_CURRENT = PREF_PREFIX + "onlyCurrent"
# width keys will be f"{PREF_PREFIX}width.<masterID>"
DEFAULT_WIDTH = 600


class MonospacedFiguresMaker(object):
    # GUIのレイアウト
    def __init__(self):
        font = Glyphs.font
        if not font:
            Message("No Font", u"Please open a font first.")
            return

        self.font = font
        self.masters = font.masters
        self.currentMasterIndex = font.masterIndex
        masterCount = len(self.masters)

        # ── load stored prefs ──
        self.storedWidths = {}
        for m in self.masters:
            key = f"{PREF_PREFIX}width.{m.id}"
            val = Glyphs.defaults[key]
            if val is not None:
                try:
                    self.storedWidths[m.id] = int(val)
                except Exception:
                    pass
        self.prefOnlyCurrent = bool(Glyphs.defaults[PREF_ONLY_CURRENT]) if Glyphs.defaults[PREF_ONLY_CURRENT] is not None else False

        # レイアウト変数を定義
        spaceX = 20
        spaceY = 10
        buttonSizeX = 60
        buttonSizeY = 20
        textSizeX = 180
        textSizeY = 20
        inputSizeX = 60
        inputSizeY = 20
        checkSizeX = 140

        windowWidth = 100 + max(0, masterCount - 1) * 100
        windowHeight = spaceY * 8 + textSizeY * 9

        self.w = FloatingWindow((windowWidth, windowHeight), "Monospaced Figures")

        # ---- source set radio ----
        self.w.text1 = TextBox((spaceX, spaceY * 2, textSizeX, textSizeY), "Source figure set:")
        self.w.radio = RadioGroup(
            (spaceX, spaceY * 2 + textSizeY, textSizeX, textSizeY * 3), [u"default", u"lining (.lf)", u"oldstyle (.osf)"]
        )
        self.w.radio.set(0)

        # ---- width fields ----
        self.w.text2 = TextBox((spaceX, spaceY * 3 + textSizeY * 4, textSizeX, textSizeY), "Monospaced width:")

        self.widthFields = []
        for idx, master in enumerate(self.masters):
            multiMasterX = spaceX + idx * (inputSizeX + spaceX)
            setattr(
                self.w,
                f"lab{idx}",
                TextBox((multiMasterX, spaceY * 3 + textSizeY * 5 + 5, textSizeX, textSizeY), master.name, sizeStyle="small"),
            )
            initVal = str(self.storedWidths.get(master.id, DEFAULT_WIDTH))
            field = EditText((multiMasterX, spaceY * 3 + textSizeY * 6, inputSizeX, inputSizeY), initVal)
            setattr(self.w, f"wf{idx}", field)
            self.widthFields.append(field)

        self.w.onlyCurrent = CheckBox(
            (spaceX, spaceY * 4 + textSizeY * 7, checkSizeX, textSizeY),
            "Only Current Master",
            value=self.prefOnlyCurrent,
            callback=self.toggleOnlyCurrent,
        )

        self.w.cancelButton = Button(
            (spaceX, spaceY * 6 + textSizeY * 8, buttonSizeX, buttonSizeY), "Cancel", callback=lambda s: self.w.close()
        )
        self.w.makeButton = Button(
            (spaceX * 1.5 + buttonSizeX, spaceY * 6 + textSizeY * 8, buttonSizeX, buttonSizeY), "Make", callback=self.make
        )

        self.toggleOnlyCurrent()

        self.w.open()
        self.w.center()
        self.w.makeKey()
        self.w.setDefaultButton(self.w.makeButton)

    # ヘルパー
    def toggleOnlyCurrent(self, sender=None):
        onlyCurrent = self.w.onlyCurrent.get()
        for idx, field in enumerate(self.widthFields):
            field.enable(not onlyCurrent or idx == self.currentMasterIndex)

    def radioSuffix(self):
        i = self.w.radio.get()
        if i == 1:
            return ".lf"
        elif i == 2:
            return ".osf"
        return ""

    @staticmethod
    def baseName(glyphName):
        if glyphName.endswith(".tf"):
            return glyphName[:-3]
        if glyphName.endswith(".tosf"):
            return glyphName[:-5]
        return None

    # 値を次回以降のために保存
    def SavePreferences(self):
        try:
            # per‑master widths
            for idx, master in enumerate(self.masters):
                key = f"{PREF_PREFIX}width.{master.id}"
                try:
                    Glyphs.defaults[key] = int(self.widthFields[idx].get())
                except Exception:
                    pass
            # only‑current flag
            Glyphs.defaults[PREF_ONLY_CURRENT] = bool(self.w.onlyCurrent.get())
        except Exception:
            return False
        return True

    # メインの処理
    def make(self, sender):
        onlyCurrent = self.w.onlyCurrent.get()
        suffix = self.radioSuffix()

        targetWidths = []
        for idx, field in enumerate(self.widthFields):
            if onlyCurrent and idx != self.currentMasterIndex:
                targetWidths.append(None)
                continue
            try:
                w = int(float(field.get()))
                targetWidths.append(w)
            except Exception:
                Message("Width must be integer", u"Please enter valid integers for the enabled masters.")
                return

        self.SavePreferences()

        font = self.font
        font.disableUpdateInterface()
        try:
            for g in {l.parent for l in font.selectedLayers}:  # unique glyphs
                base = self.baseName(g.name)
                if not base:
                    continue
                sourceName = base + suffix
                sourceGlyph = font.glyphs[sourceName]
                if not sourceGlyph:
                    Message("Missing source glyph", u"Could not find “%s” for %s." % (sourceName, g.name))
                    continue

                for idx, master in enumerate(self.masters):
                    if onlyCurrent and idx != self.currentMasterIndex:
                        continue
                    targetWidth = targetWidths[idx]
                    if targetWidth is None:
                        continue

                    layer = g.layers[master.id]
                    sourceLayer = sourceGlyph.layers[master.id]

                    # rebuild component
                    layer.shapes = []
                    comp = GSComponent(sourceGlyph)
                    comp.automaticAlignment = False
                    layer.shapes.append(comp)

                    origLeft = sourceLayer.LSB
                    origRight = sourceLayer.RSB
                    origWidth = sourceLayer.width
                    diff = targetWidth - origWidth

                    leftDelta = diff // 2
                    rightDelta = diff - leftDelta

                    if diff % 2:
                        if origLeft <= origRight:
                            if diff > 0:
                                leftDelta += 1
                                rightDelta -= 1
                            else:
                                leftDelta -= 1
                                rightDelta += 1
                        else:
                            if diff > 0:
                                leftDelta -= 1
                                rightDelta += 1
                            else:
                                leftDelta += 1
                                rightDelta -= 1

                    layer.LSB = origLeft + leftDelta
                    layer.RSB = origRight + rightDelta
        finally:
            font.enableUpdateInterface()

        self.w.close()

MonospacedFiguresMaker()
