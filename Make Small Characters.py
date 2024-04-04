# MenuTitle: make small characters

from __future__ import print_function, division, unicode_literals
__doc__="""
(GUI) Make small characters for Japanese kana
"""

import objc
import vanilla
import GlyphsApp
from Foundation import NSAffineTransform
import traceback # エラーをprintする用

GSSteppingTextField = objc.lookUpClass("GSSteppingTextField")
class ArrowEditText (vanilla.EditText):
	nsTextFieldClass = GSSteppingTextField
	def _setCallback(self, callback):
		super(ArrowEditText, self)._setCallback(callback)
		if callback is not None and self._continuous:
			self._nsObject.setContinuous_(True)
			self._nsObject.setAction_(self._target.action_)
			self._nsObject.setTarget_(self._target)

class MakeSmallCharacters( object ):
	def __init__(self):
		spaceX = 20
		spaceY= 10
		buttonSizeX = 60
		buttonSizeY = 20
		textSizeX = 80
		textSizeY = 20
		inputSizeX = 60
		inputSizeY = 20
		checkSizeX = 140
		windowWidth = spaceX*2+inputSizeX+100
		windowHeight = spaceY*6+buttonSizeY*5
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Make Small Characters", # window title
			autosaveName = "com.Wolphtype.Make Small Characters.mainwindow" # stores last window position and size
		)
		
		# Text Field
		self.w.TextS = vanilla.TextBox((spaceX, spaceY*2, textSizeX, textSizeY), "Size")
		self.w.TextP = vanilla.TextBox((spaceX+textSizeX+inputSizeX, spaceY*2, textSizeX, textSizeY), "%")
		self.w.TextT = vanilla.TextBox((spaceX, spaceY*3+textSizeY, textSizeX, textSizeY), "Translate Y")
		
		# Input Field
		self.w.inputSize = ArrowEditText( (spaceX+textSizeX, spaceY*2, inputSizeX, inputSizeY), "10", sizeStyle='regular', callback=self.textChange)
		self.w.inputTranslateY = ArrowEditText( (spaceX+textSizeX, spaceY*3+inputSizeY, inputSizeX, inputSizeY), "10", sizeStyle='regular', callback=self.textChange)
		
		# Checkbox
		self.w.masterSelector = vanilla.CheckBox( (spaceX, spaceY*4+inputSizeY*2, checkSizeX, textSizeY), "Only Current Master", sizeStyle='regular', value=False )
		
		# Run Button:
		self.w.cancelButton = vanilla.Button((spaceX, spaceY*6+inputSizeY*3, buttonSizeX, buttonSizeY), "Cancel", sizeStyle='regular', callback=self.cancelButton )
		self.w.runButton = vanilla.Button((spaceX*1.5+buttonSizeX, spaceY*6+inputSizeY*3, buttonSizeX, buttonSizeY), "OK", sizeStyle='regular', callback=self.MakeSmallMain )

		# Assign keyboard shortcuts
		self.w.runButton.bind('enter', []) # enterなら動いたけど、のちのsetDefaultButtonだけでも機能したよ
		self.w.cancelButton.bind('escape', [])

		# ウインドウを可視化させる前にユーザー設定値をテキストフィールドに放り込む
		# LoadPreferences()には、ついでにロード成功の是非をTrueかFalseで返すようにしているので、
		# 以下のようにロード失敗時のメッセージを出すこともできる
		if not self.LoadPreferences():
			print("Note: 'Make Small Characters' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		self.w.setDefaultButton(self.w.runButton)

	def SavePreferences( self, sender ):
		try:
			# 以下のようなコードを書くことで、Preferences Listファイルに好きな値を保存できる
			# このスクリプトのウインドウサイズや位置もそこに保存されている
			# ちなみにファイルの在処は　/~/Library/Preferences/com.GeorgSeifert.Glyphs3.plist
			Glyphs.defaults["com.Wolphtype.Make Small Characters.inputSize"] = int(self.w.inputSize.get())
			Glyphs.defaults["com.Wolphtype.Make Small Characters.inputTranslateY"] = int(self.w.inputTranslateY.get())
			Glyphs.defaults["com.Wolphtype.Make Small Characters.masterSelector"] = bool(self.w.masterSelector.get())
		except:
			return False
			
		return True

	# Preferences Listファイルからパラメータを引っ張ってきて、UIエレメントに代入する
	# ロードに成功したかどうか気になるので、終わりにTrueかFalseを返させる
	def LoadPreferences( self ):
		try:
			# Preferences Listファイル内の当該パラメータを引っ張ってきて、UIのテキストフィールドを差し替える
			self.w.inputSize.set(Glyphs.defaults["com.Wolphtype.Make Small Characters.inputSize"] )
			self.w.inputTranslateY.set(Glyphs.defaults["com.Wolphtype.Make Small Characters.inputTranslateY"])
			self.w.masterSelector.set(Glyphs.defaults["com.Wolphtype.Make Small Characters.masterSelector"])
		except: # ロード失敗ルート
			# （初回起動時や、スクリプトおよびパラメータ名を変更した等の理由で、Preferencesファイル内のデータが読み込まれない場合）
			return False

		return True # ロード成功ルート（try:が成功したらexceptは飛ばされる）

	# こういったメソッドは、操作してget値が変化したことにより、UIの他の要素をグレイアウトさせたかったり、
	# 編集ビューでグリフの状態をリアルタイムにアップデートしたり、
	# あとはフィールドの値を逐一セーブするにも使える（今回の改造みたいに）
	def textChange( self, sender ):
		try:
			# inputSizevalue = int(self.w.inputSize.get())
			# inputTranslateYvalue = int(self.w.inputTranslateY.get())
			# 上の二つは何にも使われてないのでコメントアウト
			self.SavePreferences(sender)
		except:
			Glyphs.showMacroWindow()
			print(traceback.format_exc())
	
	def cancelButton(self, sender):
        # Cancelボタンが押されたときの処理をここに記述します
		self.w.close()
		print("canceled")
        
	def MakeSmallMain(self, sender):
		try: # エラーが起きるかもしれないコードを、とりあえず実行してみるため。後述のexceptでエラー対処しやすくなる。
			inputSize = int(self.w.inputSize.get())
			inputTranslateY = int(self.w.inputTranslateY.get())
			
			f = Glyphs.font
			# allGlyphNames = [ g.name for g in f.glyphs ] # 使われてないし出番もなさそうなので省略
			sel = f.selectedLayers

			f.disableUpdateInterface()
			for l in sel:
				g = l.parent				
				m = l.master
				if "small" in g.name:
					parentGlyphName = g.name.replace("small", "")
					# parentGlyph = GSGlyph( parentGlyphName )
					# parentGlyphは使われてないし、GSGlyph()は新規グリフを生成する命令なので出番はなし。
					# GSGlyph()はフォントファイルに即座にグリフを追加するわけではないので、一見すると何も起きてないように見えるかも。 "")
					pg = f.glyphs[parentGlyphName]
					for m in f.masters:
						gl = g.layers[m.id]
						if self.w.masterSelector.get() == 0:
							ag = gl
						else:
							ag = l
						ag.shapes = []
						newComp = GSComponent( pg )
						ag.shapes.append(newComp)
						ag.shapes[0].alignment = False
						bodyCenterX = ag.width / 2
						bodyCenterY = (m.ascender + m.descender) / 2
						c = ag.shapes[0]
						trans = NSAffineTransform()
						trans.scale(inputSize/100, (bodyCenterX,bodyCenterY))
						trans.translateXBy_yBy_(0, -(inputTranslateY/inputSize*100))
						c.transform_(trans) 
				else:
					print(g.name, "is not a small character")

			self.w.close() # ウインドウを閉じる命令は一度のみ、ループが終わった後などで。
			f.enableUpdateInterface() # UI機能復活

		except: # なにかエラーが起きて中断したらこちらに流れる。tryとexceptはペアで使う
			print(traceback.format_exc())
			self.w.close()
			f.enableUpdateInterface()
					
MakeSmallCharacters()
