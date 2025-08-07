# add code here# MenuTitle: move fixed distance

from __future__ import print_function, division, unicode_literals
__doc__="""
(GUI) Move selected object with fixed distance
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

class MoveFixedDistance( object ):
	def __init__(self):
		spaceX = 20
		spaceY= 10
		buttonSizeX = 60
		buttonSizeY = 20
		textSizeX = 120
		textSizeY = 20
		inputSizeX = 60
		inputSizeY = 20
		windowWidth = spaceX*2+inputSizeX+textSizeX
		windowHeight = spaceY*10+buttonSizeY*11
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Move Fixed Distance", # window title
			autosaveName = "com.Wolphtype.Make Small Characters.mainwindow" # stores last window position and size
		)
		
		# Text Field
		self.w.TextD = vanilla.TextBox((spaceX, spaceY*2, textSizeX, textSizeY), "Distance")
		self.w.TextS = vanilla.TextBox((spaceX, spaceY*3+textSizeY, textSizeX, textSizeY), "Small Distance")
		self.w.TextE = vanilla.TextBox((spaceX, spaceY*4+textSizeY*2, textSizeX, textSizeY), "Additional")
		
		# Input Field
		self.w.inputDistance = ArrowEditText( (spaceX+textSizeX, spaceY*2, inputSizeX, inputSizeY), "10", sizeStyle='regular', callback=self.textChange)
		self.w.inputSmallDistance = ArrowEditText( (spaceX+textSizeX, spaceY*3+inputSizeY, inputSizeX, inputSizeY), "10", sizeStyle='regular', callback=self.textChange)
		self.w.inputAdditionalDistance = ArrowEditText( (spaceX+textSizeX, spaceY*4+inputSizeY*2, inputSizeX, inputSizeY), "10", sizeStyle='regular', callback=self.textChange)
		
		# Radio Button
		self.w.distanceSelector = vanilla.RadioGroup( (spaceX, spaceY*5+inputSizeY*3, textSizeX+inputSizeX, textSizeY*4), ["Normal", "Half", "Small", "Two"], sizeStyle='regular', isVertical=True )
		
		# Run Button:
		self.w.topButton = vanilla.Button((spaceX*2, spaceY*9+inputSizeY*6, buttonSizeX*2+spaceX, buttonSizeY), "1 Top", sizeStyle='regular', callback=self.MoveDistanceMain )
		self.w.rightButton = vanilla.Button((spaceX*3+buttonSizeX, spaceY*10+inputSizeY*7, buttonSizeX, buttonSizeY), "2 Right", sizeStyle='regular', callback=self.MoveDistanceMain )
		self.w.bottomButton = vanilla.Button((spaceX*2, spaceY*11+inputSizeY*8, buttonSizeX*2+spaceX, buttonSizeY), "3 Bottom", sizeStyle='regular', callback=self.MoveDistanceMain )
		self.w.leftButton = vanilla.Button((spaceX*2, spaceY*10+inputSizeY*7, buttonSizeX, buttonSizeY), "4 Left", sizeStyle='regular', callback=self.MoveDistanceMain )

		# Assign keyboard shortcuts
		self.w.topButton.bind('1', []) # enterなら動いたけど、のちのsetDefaultButtonだけでも機能したよ
		self.w.rightButton.bind('2', [])
		self.w.bottomButton.bind('3', [])
		self.w.leftButton.bind('4', [])

		# ウインドウを可視化させる前にユーザー設定値をテキストフィールドに放り込む
		# LoadPreferences()には、ついでにロード成功の是非をTrueかFalseで返すようにしているので、
		# 以下のようにロード失敗時のメッセージを出すこともできる
		if not self.LoadPreferences():
			print("Note: 'Move Fixed Distance' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.distanceSelector.set(0)
		self.w.makeKey()

	def SavePreferences( self, sender ):
		try:
			# 以下のようなコードを書くことで、Preferences Listファイルに好きな値を保存できる
			# このスクリプトのウインドウサイズや位置もそこに保存されている
			# ちなみにファイルの在処は　/~/Library/Preferences/com.GeorgSeifert.Glyphs3.plist
			Glyphs.defaults["com.Wolphtype.Move Fixed Distance.distance"] = int(self.w.inputDistance.get())
			Glyphs.defaults["com.Wolphtype.Move Fixed Distance.smallDistance"] = int(self.w.inputSmallDistance.get())
			Glyphs.defaults["com.Wolphtype.Move Fixed Distance.twoDistance"] = int(self.w.inputAdditionalDistance.get())
		except:
			return False
			
		return True

	# Preferences Listファイルからパラメータを引っ張ってきて、UIエレメントに代入する
	# ロードに成功したかどうか気になるので、終わりにTrueかFalseを返させる
	def LoadPreferences( self ):
		try:
			# Preferences Listファイル内の当該パラメータを引っ張ってきて、UIのテキストフィールドを差し替える
			self.w.inputDistance.set(Glyphs.defaults["com.Wolphtype.Move Fixed Distance.distance"] )
			self.w.inputSmallDistance.set(Glyphs.defaults["com.Wolphtype.Move Fixed Distance.smallDistance"])
			self.w.inputAdditionalDistance.set(Glyphs.defaults["com.Wolphtype.Move Fixed Distance.twoDistance"])
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
        
	def MoveDistanceMain(self, sender):
		try: # エラーが起きるかもしれないコードを、とりあえず実行してみるため。後述のexceptでエラー対処しやすくなる。
			inputDistance = int(self.w.inputDistance.get())
			inputHalfDistance = int((inputDistance)*0.5)
			inputSmallDistance = int(self.w.inputSmallDistance.get())
			inputTwoDistance = int(self.w.inputAdditionalDistance.get())			
			f = Glyphs.font
			# allGlyphNames = [ g.name for g in f.glyphs ] # 使われてないし出番もなさそうなので省略
			sel = f.selectedLayers[0]
			selection = sel.selection
#			f.disableUpdateInterface()
			for obj in selection:
				if isinstance(obj, GSComponent):
					trans = NSAffineTransform()
					if sender == self.w.topButton: #Move Top
						if self.w.distanceSelector.get() == 0:
							trans.translateXBy_yBy_(0, (inputDistance))
						elif self.w.distanceSelector.get() == 1:
							trans.translateXBy_yBy_(0, (inputHalfDistance))
						elif self.w.distanceSelector.get() == 2:
							trans.translateXBy_yBy_(0, (inputSmallDistance))
						else: #Two
							trans.translateXBy_yBy_(0, (inputTwoDistance))
					elif sender == self.w.rightButton: #Move Right
						if self.w.distanceSelector.get() == 0:
							trans.translateXBy_yBy_((inputDistance), 0)
						elif self.w.distanceSelector.get() == 1:
							trans.translateXBy_yBy_((inputHalfDistance), 0)
						elif self.w.distanceSelector.get() == 2:
							trans.translateXBy_yBy_((inputSmallDistance), 0)
						else: #Two
							trans.translateXBy_yBy_((inputTwoDistance), 0)
					elif sender == self.w.bottomButton: #Move Top
						if self.w.distanceSelector.get() == 0:
							trans.translateXBy_yBy_(0, -(inputDistance))
						elif self.w.distanceSelector.get() == 1:
							trans.translateXBy_yBy_(0, -(inputHalfDistance))
						elif self.w.distanceSelector.get() == 2:
							trans.translateXBy_yBy_(0, -(inputSmallDistance))
						else: #Two
							trans.translateXBy_yBy_(0, -(inputTwoDistance))
					else: #Move Left
						if self.w.distanceSelector.get() == 0:
							trans.translateXBy_yBy_(-(inputDistance), 0)
						elif self.w.distanceSelector.get() == 1:
							trans.translateXBy_yBy_(-(inputHalfDistance), 0)
						elif self.w.distanceSelector.get() == 2:
							trans.translateXBy_yBy_(-(inputSmallDistance), 0)
						else: #Two
							trans.translateXBy_yBy_(-(inputTwoDistance), 0)
				obj.applyTransform(trans.transformStruct())
#			f.enableUpdateInterface() # UI機能復活

		except: # なにかエラーが起きて中断したらこちらに流れる。tryとexceptはペアで使う
			print(traceback.format_exc())
			self.w.close()
#			f.enableUpdateInterface()
MoveFixedDistance()
