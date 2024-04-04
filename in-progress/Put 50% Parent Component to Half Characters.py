# Put a 50% width component for .half alternates from full-width glyphs (current master)
f = Glyphs.font
allGlyphNames = [ g.name for g in f.glyphs ]
sel = f.selectedLayers

for l in sel:
	g = l.parent
	parentGlyphName = g.name.replace(".half", "")
	newGlyphName = '%s.half' % g.name
	pg = f.glyphs[parentGlyphName]
	l.clear()
	newComp = GSComponent( pg )
	l.shapes.append(newComp)
	l.shapes[0].alignment = False
	l.applyTransform([
	    0.5, # x scale factor
	    0, # x skew factor
	    0, # y skew factor
	    1.0, # y scale factor
	    0, # x position
	    0  # y position
	])
	l.background = l.copy()
	l.decomposeComponents()
		