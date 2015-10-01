import math
import urllib
import contextlib # for urllib.urlopen
import copy
import os
import tkMessageBox
import tkSimpleDialog
from datetime import datetime
from datetime import date
from Tkinter import *
import time
import webbrowser
from eventBasedAnimationClass import EventBasedAnimationClass

class Matrix(object):
	def __init__(self, rows, cols, A):
		self.rows = rows
		self.cols = cols
		self.entries = [[0 for j in xrange(cols)] for i in xrange(rows)]
		for i in xrange(rows):
			for j in xrange(cols):
				self.entries[i][j] = A[i][j]
		self.D = None
		self.T = None
		
	def __mul__(self, other):
		if type(other) == Matrix:
			return self.matrixMatrixMultiplication(other)
		elif type(other) == Vector:
			return self.matrixVectorMultiplication(other)
		elif type(other) == int or type(other) == float:
			return self.matrixScalarMultiplication(other)

	def matrixMatrixMultiplication(self, other):
		if other.rows == self.cols:
			multiplied = ([[0 for i in xrange(self.rows)] 
				for j in xrange(other.cols)])
			for row in xrange(self.rows):
				vec1 = Vector(self.cols, self.entries[row])
				for col in xrange(other.cols):
					vec2entries = ([other.entries[r][col] 
						for r in xrange(other.rows)])
					vec2 = Vector(other.rows, vec2entries)
					multiplied[row][col] = vec1 * vec2
			return Matrix(self.rows, other.cols, multiplied)
		else:
			raise Exception("Cannot be multiplied")

	def matrixVectorMultiplication(self, other):
		if other.dimension == self.cols:
			multiplied = [0 for i in xrange(self.rows)]
			for row in xrange(self.rows):
				vec1 = Vector(self.cols, self.entries[row])
				vec2 = other
				multiplied[row] = vec1 * vec2
			return Vector(self.rows, multiplied)
		else:
			raise Exception("Cannot be multiplied")

	def matrixScalarMultiplication(self, other):
		multiplied = copy.deepcopy(self.entries)
		for row in xrange(self.rows):
			for col in xrange(self.cols):
				multiplied[row][col] *= other
		return Matrix(self.rows, self.cols, multiplied)

	def __rmul__(self, other):
		return self * other

	def __div__(self, other):
		newMatrix = Matrix(self.rows, self.cols, self.entries)
		if isinstance(other, int) or isinstance(other, float):
			for row in xrange(self.rows):
				for col in xrange(self.cols):
					newMatrix.entries[row][col] = (float(
						newMatrix.entries[row][col])/other)
			return newMatrix

	def determinant(self):
		if self.rows == self.cols:
			n, self.D = self.rows, 0
			if n == 1:
				return self.entries[0][0]
			else:
				for i in xrange(self.cols):
					self.D += (self.entries[0][i] * self.cofactor(0, i))
				return self.D

	def inverse(self):
		if self.D == 0:
			raise Exception("Inverse doesn't exist")
		else:
			return self.adjoint()/self.determinant()

	def cofactor(self, a, b):
		assert (self.rows == self.cols)
		n = self.rows
		residualMatrix = [[0 for j in xrange(n-1)] for i in xrange(n-1)]
		crow = 0
		for i in xrange(n):
			if i != a:
				ccol = 0
				for j in xrange(n):
					if j != b:
						residualMatrix[crow][ccol] = self.entries[i][j]
						ccol += 1
				crow += 1
		return ((-1)**(a+b)) * (Matrix(self.rows - 1, self.cols - 1, 
			residualMatrix)).determinant()

	def cofactorMatrix(self):
		assert self.rows == self.cols
		n = self.rows
		cofMatrix = [[0 for j in xrange(n)] for i in xrange(n)]
		for i in xrange(n):
			for j in xrange(n):
				cofMatrix[i][j] = self.cofactor(i, j)
		return Matrix(n, n, cofMatrix)

	def adjoint(self):
		assert self.rows == self.cols
		n = self.rows
		return self.cofactorMatrix().transpose()

	def transpose(self):
		B = [[0 for col in xrange(self.rows)] for row in xrange(self.cols)]
		for row in xrange(self.rows):
			for col in xrange(self.cols):
				B[col][row] = self.entries[row][col]
		self.T = Matrix(self.cols, self.rows, B)
		return self.T

	def append(self, n):
		# appends a column of n's to the right of matrix
		newMatrix = ([[0 for i in xrange(self.cols + 1)] 
			for j in xrange(self.rows)])
		for row in xrange(self.rows):
			for col in xrange(self.cols):
				newMatrix[row][col] = self.entries[row][col]
			newMatrix[row][self.cols] = n
		return Matrix(self.rows, self.cols+1, newMatrix)

class Vector(Matrix):
	def __init__(self, dimension, b):
		self.dimension = dimension
		self.entries = b

	def __mul__(self, other):
		if type(other) == Vector:
			product = 0
			assert self.dimension == other.dimension
			for i in xrange(self.dimension):
				product += self.entries[i] * other.entries[i]
			return product
		elif type(other) == Matrix:
			return other * self

def leastSquares(A, b):
	# matrix A, vector b. returns vector with slope and intercept
	return (A.transpose() * A).inverse() * (A.transpose() * b)

# CITATION: function rgbString taken from Course notes
def rgbString(red, green, blue):
	return "#%02x%02x%02x" % (red, green, blue)

# CITATION: function readWebPage taken from Course notes
def readWebPage(url):
	# reads from url and returns it
	assert(url.startswith("https://"))
	with contextlib.closing(urllib.urlopen(url)) as fin:
		return fin.read()

def writeFile(filename, contents, mode = "a"):
	# writes contents to filename
	fout = open(filename, mode)
	if type(contents) == list:
		for i in xrange(len(contents)):
			fout.write(str(contents[i]))
	else: fout.write(str(contents))
	fout.close()

def makeFileIntoArray(filename):
	with open(filename, "rt") as fin:
			contents = fin.read()
	contents = contents.split("\n")
	return contents

def getSpotRate():
	# returns the spot rate at that moment. returns a STRING
	url = "https://api.coinbase.com/v1/prices/spot_rate"
	priceAndCurrency = readWebPage(url)
	priceAndCurrency = priceAndCurrency.split("\"")
	priceIndex = 3
	price = priceAndCurrency[priceIndex]
	return price

class Application(EventBasedAnimationClass):
	def __init__(self):
		self.width, self.height = 1200, 600
		self.spotRate, self.timerCount = 0, 0
		self.lastEntry = 0.0
		super(Application, self).__init__(self.width, self.height)
		
	def change(self, activePage):
		self.activePage = activePage(self.change)

	def initAnimation(self):
		self.timerDelay = 1000
		self.activePage = HomePage(self.change)
		self.root.bind("<Motion>", lambda event: self.onMouseMotion(event))

	def onTimerFired(self):
		self.timerCount += 1
		self.spotRate = getSpotRate()
		if self.activePage.data:
			self.callCreateDataFile()
		if self.activePage.chartIntermediate:
			self.changeToChartPage()
		if self.timerCount >= 120:
			# two minutes up, look for new data
			self.newEntry = self.activePage.getNewEntry()
			if (self.activePage == PredictPage and self.activePage.frozen and 
				self.activePage.promptToBuy and self.newEntry > self.lastEntry):
				self.displayDialog("BUY NOW!")
				# was frozen and it's time to BUY NOW!
			elif (self.activePage == PredictPage and self.activePage.frozen and 
				self.activePage.promptToSell and self.newEntry<self.lastEntry):
				self.displayDialog("SELL NOW!")
				# was frozen and it's time to SELL NOW!
			self.lastEntry = self.newEntry
			self.timerCount = 0
		self.redrawAll()

	def callCreateDataFile(self):
		self.redrawAll()
		self.activePage.data = False
		self.activePage.createDataFile()

	def changeToChartPage(self):
		self.redrawAll()
		self.activePage.change(ChartPage)
		self.activePage.chartIntermediate = False

	def displayDialog(self, msg):
		message = msg
		title = "Info box"
		tkMessageBox.showinfo(title, message)

	def onKeyPressed(self, event):
		self.activePage.onKeyPressed(event)
		self.redrawAll()

	def onMousePressed(self, event):
		self.activePage.onMousePressed(event)
		self.redrawAll()

	def onMouseMotion(self, event):
		self.activePage.onMouseMotion(event)
		self.redrawAll()

	def redrawAll(self):
		self.activePage.draw(self.canvas, self.spotRate)

class Page(object):
	def __init__(self, change):
		self.pageWidth, self.pageHeight = 1200, 600
		self.appNameX, self.appNameY = self.pageWidth/4, self.pageHeight/8
		wby2, h = 50, 40
		self.initializeBooleanVariables()
		self.change = change
		self.initializeAllButtonVariables()
		filename = "tempDir" + os.sep + "bitcoinHistory2.txt"
		(self.days1Month, self.prices1Month) = self.getNMonthsData(filename,1)
		self.initializeChartStuff()
		self.want1Month = True
		self.want6Months, self.want3Months, self.want1Year = False, False, False
		self.justStarted = False
		self.chartIntermediate = False
		
	def initializeBooleanVariables(self):
		self.predict = False 
		self.chart = False
		self.data = False

	def initializeAllButtonVariables(self):
		wby2, h, mgn, space = 50, 40, 80, 120
		self.predictX1 = self.pageWidth/2 - wby2 - mgn
		self.predictY1 = self.pageHeight - h
		self.predictX2 = self.pageWidth/2 + wby2 - mgn
		self.predictY2 = self.pageHeight
		self.chartX1, self.chartX2 = self.predictX1-space, self.predictX2-space
		self.chartY1, self.chartY2 = self.predictY1, self.predictY2
		self.dataX1, self.dataX2 = self.predictX1+space, self.predictX2 + space
		self.dataY1, self.dataY2 = self.predictY1, self.predictY2
		self.homeX1, self.homeX2 = self.predictX1-2*space,self.predictX2-2*space
		self.homeY1, self.homeY2 = self.predictY1, self.predictY2
		self.personalizedX1 = self.predictX1 + 2*space
		self.personalizedX2 = self.predictX2 + 2*space
		self.personalizedY1, self.personalizedY2 = self.predictY1,self.predictY2
		self.helpX1 = self.predictX1 + 3*space
		self.helpX2 = self.predictX2 + 3*space
		self.helpY1, self.helpY2 = self.predictY1, self.predictY2

	def initializeChartStuff(self):
		self.lengthOfXAxisInPixels, self.lengthOfYAxisInPixels = 1000, 300
		self.chartWidth = self.lengthOfXAxisInPixels 
		self.chartHeight = self.lengthOfYAxisInPixels
		leftMargin, botMargin = 150, 100
		self.originX = leftMargin
		self.originY = self.pageHeight - botMargin
		self.days, self.prices = self.days1Month, self.prices1Month
		self.xmax, self.ymax = len(self.days), max(self.prices)
		self.horizScalingFactor = float(self.lengthOfXAxisInPixels)/self.xmax
		# pixel per day
		self.vertScalingFactor = float(self.lengthOfYAxisInPixels)/self.ymax
		# pixel per dollar

	def createDataFile(self):
		# creates a file containing data of approximately
		# last one year
		self.data = True
		url = "https://api.coinbase.com/v1/prices/historical?page="
		path =  "tempDir" + os.sep + "bitcoinHistory2.txt"
		if os.path.exists(path):
			writeFile(path, "", "wt")
		else:
			os.makedirs("tempDir")
			writeFile(path, "", "wt")
		reachedLastYear = False
		pageNo = 1
		while not reachedLastYear:
			urlWithPage = url + str(pageNo)
			urlContents = readWebPage(urlWithPage)
			dateLen = 10
			reachedLastYear = self.checkLastYear(str(urlContents[0:dateLen]))
			normalizedContents = self.normalize(urlContents)
			writeFile(path, normalizedContents)
			pageNo += 1
		self.data = False

	def getNewEntry(self):
		# gets new entry if released by coinbase
		url = "https://api.coinbase.com/v1/prices/historical?page=1"
		path =  "tempDir" + os.sep + "bitcoinHistory2.txt"
		with open(path, "rt") as fin:
			originalContents = fin.read()
		contents = makeFileIntoArray(path)
		urlContents = readWebPage(url)
		urlContents = urlContents.split("\n")
		urlContents = urlContents[0]
		possibleNewEntry = self.normalize(urlContents)
		if possibleNewEntry[0].split("\n")[0] != contents[0]:
			newContents = (str(possibleNewEntry[0].split("\n")[0]) + 
				"\n" + str(originalContents))
			writeFile(path, newContents, "wt")

	def normalize(self, urlContents):
		# normalizes all timestamps to CMU's timezone, 
		# i.e. UTC-5
		# reason for having this fn: coinbase randomizes the timezone it 
		# displays its data in, every instant.
		cmuTimezone = -5 # relative to UTC
		newContents = "" # the contents as we want them
		urlContents = urlContents.split("\n")
		hIndex, hhmmLength, tzIndex, dateLen = 11, 5, 21, 10
		for i in xrange(len(urlContents)):
			timestamp = urlContents[i][hIndex : hIndex + hhmmLength]
			# in hh:mm format
			coinbaseTimezone = int(urlContents[i][tzIndex - 2 : tzIndex + 1])
			mIdx, hrsInDay, priceIdx = 3, 24, 26
			hour, minute = int(timestamp[0 : 2]), timestamp[mIdx : mIdx + 2]
			normalizedHour = (str((hour + cmuTimezone - coinbaseTimezone) 
				% hrsInDay))
			newDate = urlContents[i][0 : dateLen]
			if len(normalizedHour) == 1: normalizedHour = "0" + normalizedHour
			if int(normalizedHour) + coinbaseTimezone - cmuTimezone >= 24:
				newDate = self.timezoneTooPositiveDecreaseDate(newDate)
				# timezone was so positive that date changed
			elif int(normalizedHour) + coinbaseTimezone - cmuTimezone < 0:
				newDate = self.timezoneTooNegativeIncreaseDate(newDate)
				# timezone was so negative that date changed
			urlContents[i] = (newDate + normalizedHour
				+ ":" + str(minute) + str(urlContents[i][priceIdx:]) + "\n")
		return urlContents

	def timezoneTooNegativeIncreaseDate(self, d):
		# returns a string of the newDate
		d = date(int(d[:4]), int(d[5:7]), int(d[8:]))
		dayLengthList = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
		dayCopy = d.day + 1
		if dayCopy > dayLengthList[d.month-1]:
			newDay = 1
			if d.month == 12:
				newMonth = 1
				newYear = d.year + 1
			else:
				newMonth = d.month + 1
				newYear = d.year
		else:
			newDay = dayCopy
			newMonth = d.month
			newYear = d.year
		newDate = date(newYear, newMonth, newDay)
		dateString = str(newDate)
		return dateString

	def timezoneTooPositiveDecreaseDate(self, d):
		# returns a string of the newDate
		d = date(int(d[:4]), int(d[5:7]), int(d[8:]))
		dayLengthList = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
		dayCopy = d.day - 1
		if dayCopy == 0:
			newDay = dayLengthList[(d.month - 1) - 1]
			if d.month == 1:
				newMonth = 12
				newYear = d.year - 1
			else:
				newMonth = d.month - 1
				newYear = d.year
		else:
			newDay = dayCopy
			newMonth = d.month
			newYear = d.year
		newDate = date(newYear, newMonth, newDay)
		dateString = str(newDate)
		return dateString

	def checkLastYear(self, dateOnPage):
		# returns True if dateOnPage is older than one year before
		# today's date
		dateOnPage = dateOnPage.split("-")
		today = str(date.today()).split("-")
		if (int(dateOnPage[0]) == int(today[0]) - 1 and
			((int(dateOnPage[1]) < int(today[1])) or
			(int(dateOnPage[1]) == int(today[1]) and 
				int(dateOnPage[2]) < int(today[2])))):
			return True
		return False

	def onMousePressed(self, event):
		x, y = event.x, event.y
		if (self.predictX1 < x < self.predictX2 and 
			self.predictY1 < y < self.predictY2):
			self.predict, self.chart, self.data = True, False, False
			self.change(PredictPage)
		elif (self.chartX1 < x < self.chartX2 and self.chartY1<y<self.chartY2):
			self.chart, self.chartIntermediate = True, True
			self.predict, self.data = False, False
		elif (self.dataX1 < x < self.dataX2 and self.dataY1 < y < self.dataY2):
			self.data = True
		elif (self.homeX1 < x < self.homeX2 and self.homeY1 < y < self.homeY2):
			self.predict, self.data, self.chart = False, False, False
			self.change(HomePage)
		elif (self.personalizedX1 < x < self.personalizedX2 and
			self.personalizedY1 < y < self.personalizedY2):
			self.predict, self.data, self.chart = False, False, False
			self.change(PersonalizedCharts)
		elif (self.helpX1 < x < self.helpX2 and self.helpY1 < y < self.helpY2):
			self.predict, self.data, self.chart = False, False, False
			self.change(Help)

	def draw(self, canvas, spotRate):
		canvas.delete(ALL)
		self.makePredictButton(canvas)
		self.makeChartsButton(canvas)
		self.makeLoadDataButton(canvas)
		self.makeHomeButton(canvas)
		self.makePersonalizedChartsButton(canvas)
		self.makeAboutButton(canvas)

	# rgbString(30, 104, 255) is the dodger blue color which is the main color
	# I use in my app.

	def makeChartsButton(self, canvas):
		wby2, h = 50, 40
		canvas.create_rectangle(self.chartX1, self.chartY1,
								self.chartX2, self.chartY2,
								fill = rgbString(30, 104, 255), 
								outline = rgbString(30, 104, 255))
		canvas.create_text(self.chartX1 + wby2, self.chartY1 + h/2,
								text = "View Charts", fill = "snow")

	def makePredictButton(self, canvas):
		wby2, h = 50, 40
		canvas.create_rectangle(self.predictX1, self.predictY1,
								self.predictX2, self.predictY2,
								fill = rgbString(30, 104, 255), 
								outline = rgbString(30, 104, 255))
		canvas.create_text(self.predictX1 + wby2, self.predictY1 + h/2,
								text = "Predict!", fill = "snow")
	
	def makeLoadDataButton(self, canvas):
		wby2, h = 50, 40
		canvas.create_rectangle(self.dataX1, self.dataY1,
								self.dataX2, self.dataY2,
								fill = rgbString(30, 104, 255),
								outline = rgbString(30, 104, 255))
		canvas.create_text(self.dataX1 + wby2, self.dataY1 + h/2,
								text = "Refresh Data", fill = "snow")

	def makeHomeButton(self, canvas):
		wby2, h = 50, 40
		canvas.create_rectangle(self.homeX1, self.homeY1,
								self.homeX2, self.homeY2,
								fill = rgbString(30, 104, 255),
								outline = rgbString(30, 104, 255))
		canvas.create_text(self.homeX1 + wby2, self.homeY1 + h/2,
								text = "Home", fill = "snow")

	def makePersonalizedChartsButton(self, canvas):
		wby2, h = 50, 40
		canvas.create_rectangle(self.personalizedX1, self.personalizedY1,
								self.personalizedX2, self.personalizedY2, 
								fill = rgbString(30, 104, 255), 
								outline = rgbString(30, 104, 255))
		canvas.create_text(self.personalizedX1 + wby2, 
							self.personalizedY1 + h/2,
							text = "Personalize", fill = "snow")

	def makeAboutButton(self, canvas):
		wby2, h = 50, 40
		canvas.create_rectangle(self.helpX1, self.helpY1, 
								self.helpX2, self.helpY2, 
								fill = rgbString(30, 104, 255), 
								outline = rgbString(30, 104, 255))
		canvas.create_text(self.helpX1 + wby2, 
							self.helpY1 + h/2,
							text = "About", fill = "snow")

	def drawLoadingScreen(self, canvas):
		canvas.create_rectangle(0, 0, self.pageWidth, self.pageHeight,
			fill = "black")
		canvas.create_text(self.pageWidth/2, self.pageHeight/2, 
			text = "Loading... Please be patient..",
			font = "Arial 40 bold", fill = "snow")
		
	def drawBanner(self, canvas):
		canvas.create_rectangle(0, 0, self.pageWidth, self.pageHeight/4,
			fill = rgbString(30, 104, 255), outline = rgbString(30, 104, 255))
		# dodger blue color
		canvas.create_text(self.appNameX, self.appNameY, 
			text = "bitPredict", fill = "snow", 
			font = "Trebuchet 100 bold italic")

	def getPriceArray(self, filename):
		priceIdx = 15
		with open(filename, "rt") as fin:
			contents = fin.read()
		contents = contents.split("\n")
		for i in xrange(len(contents)):
			contents[i] = contents[i][priceIdx:]
		return contents

	def getLastNMaximas(self, N):
		filename = "tempDir" + os.sep + "bitcoinHistory2.txt"
		self.priceArray = self.getPriceArray(filename)
		self.maximas, noOfMax, i = [], 0, 1
		while noOfMax < N:
			if (float(self.priceArray[i]) >= float(self.priceArray[i - 1]) and 
				float(self.priceArray[i]) >= float(self.priceArray[i + 1])):
				self.maximas += [float(self.priceArray[i])]
				noOfMax += 1
			i += 1
		return self.maximas

	def getLastNMinimas(self, N):
		filename = "tempDir" + os.sep + "bitcoinHistory2.txt"
		self.priceArray = self.getPriceArray(filename)
		self.minimas, noOfMin, i = [], 0, 1
		while noOfMin < N:
			if (float(self.priceArray[i]) <= float(self.priceArray[i - 1]) and 
				float(self.priceArray[i]) <= float(self.priceArray[i + 1])):
				self.minimas += [float(self.priceArray[i])]
				noOfMin += 1
			i += 1
		return self.minimas

	def getResistanceLine(self):
		N, S, avg = 10, 0, 0
		self.maximas = self.getLastNMaximas(N)
		for i in xrange(len(self.maximas)):
			S += self.maximas[i]
		avg = float(S)/N
		return avg

	def getSupportLine(self):
		N, S, avg = 10, 0, 0
		self.minimas = self.getLastNMinimas(N)
		for i in xrange(len(self.minimas)):
			S += self.minimas[i]
		avg = float(S)/N
		return avg

	def getNMonthsData(self, filename, N):
		# sifts through the file and creates two arrays of time coordinate and
		# varying bitcoin price.
		days, prices = [date.today()], [float(getSpotRate())]
		with open(filename, "rt") as fin:
			contents = fin.read()
		contents = contents.split("\n")
		current = date.today()
		yrIdx, mIdx, dIdx, hIdx, minIdx, priceIdx = 4, 5, 8, 10, 13, 15
		i = 0
		month = date.today().month
		while (((date.today().month - month) % 12 < N) or
			((date.today().month - month) % 12 == N and 
				day >= date.today().day)):
			year = int(contents[i][0 : yrIdx])
			month = int(contents[i][mIdx : mIdx + 2])
			day = int(contents[i][dIdx : dIdx + 2])
			if (date(year, month, day) != current):
				days = [date(year, month, day)] + days
				prices = [float(contents[i][priceIdx:])] + prices
				current = date(year, month, day)
			i += 1
		return (days, prices)

	def getOneYearData(self, filename):
		# sifts through the file and creates two arrays of time coordinate and
		# varying bitcoin price.
		days, prices = [date.today()], [float(getSpotRate())]
		with open(filename, "rt") as fin:
			contents = fin.read()
		contents = contents.split("\n")
		current = date.today()
		yrIdx, mIdx, dIdx, hIdx, minIdx, priceIdx = 4, 5, 8, 10, 13, 15
		for i in xrange(len(contents)):
			year = int(contents[i][0 : yrIdx])
			month = int(contents[i][mIdx : mIdx + 2])
			day = int(contents[i][dIdx : dIdx + 2])
			if (current >= date(date.today().year - 1, 
				date.today().month, date.today().day)):
				if (date(year, month, day) != current):
					days = [date(year, month, day)] + days
					prices = [float(contents[i][priceIdx:])] + prices
					current = date(year, month, day)
			else:
				break
		return (days, prices)
		
	def drawScaledAxes(self, canvas):
		# draws the Axes scaled according to parameters given as input.
		canvas.create_line(self.originX, self.originY, 
			self.originX, self.originY - self.chartHeight)
		# draws Y axis
		canvas.create_line(self.originX, self.originY, 
			self.originX + self.chartWidth, self.originY)
		# draws X axis
		self.hashXAxis(canvas)
		self.hashYAxis(canvas)

	def hashXAxis(self, canvas):
		spacing = 10
		i = 0
		if self.want1Year: step = 30
		elif self.want6Months: step = 20
		elif self.want3Months: step = 15
		elif self.want1Month: step = 3
		while (i <= len(self.days) - step): 
			canvas.create_text(self.originX + i * self.horizScalingFactor,
				self.originY + spacing, text = self.display(self.days[i]))
			i += step
		canvas.create_text(self.originX + self.lengthOfXAxisInPixels,
			self.originY + spacing, text = self.display(self.days[-1]))
		# display today's date

	def hashYAxis(self, canvas):
		spacing = 30
		canvas.create_text(self.originX - spacing,
			self.originY - self.lengthOfYAxisInPixels, 
			text = "$ " + str(self.ymax))
		i = 0
		while i <= self.ymax:
			canvas.create_text(self.originX - spacing,
			self.originY - i * self.vertScalingFactor, 
			text = "$ " + str(i))
			i += 200

	def plotChart(self, canvas, noOfMonths):
		filename = "tempDir" + os.sep + "bitcoinHistory2.txt"
		if self.justStarted: self.justStarted = False
		elif noOfMonths == 12:
			self.days, self.prices = self.days1Year, self.prices1Year
		elif noOfMonths == 6:
			self.days, self.prices = self.days6Months, self.prices6Months
		elif noOfMonths == 3:
			self.days, self.prices = self.days3Months, self.prices3Months
		elif noOfMonths == 1:
			self.days, self.prices = self.days1Month, self.prices1Month
		self.adjustScale()
		self.drawScaledAxes(canvas)
		oldScreenX = self.originX
		oldScreenY = self.originY - self.vertScalingFactor * self.prices[0]
		for i in xrange(len(self.days)):
			screenX = (self.originX + i*self.horizScalingFactor)
			screenY = self.originY - (self.prices[i]*self.vertScalingFactor)
			canvas.create_line(screenX, screenY, oldScreenX, oldScreenY)
			oldScreenX, oldScreenY = screenX, screenY

	def adjustScale(self):
		self.xmax, self.ymax = len(self.days), max(self.prices)
		self.horizScalingFactor = float(self.lengthOfXAxisInPixels)/self.xmax
		# pixel per day
		self.vertScalingFactor = float(self.lengthOfYAxisInPixels)/self.ymax
		# pixel per dollar

	def display(self, date):
		months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", 
			"Oct", "Nov", "Dec"]
		month = months[date.month - 1]
		day = date.day
		return str(month) + " " + str(day)

	def displaySpotRateInCorner(self, canvas, spotRate):
		lineSpace = 100
		canvas.create_text(self.pageWidth, 0, anchor = NE, 
			text = "$ " + spotRate, font = "Helvetica 50 bold")

	def inChart(self, x, y):
		return ((self.originX < x < self.originX + self.chartWidth) and 
			(self.originY - self.chartHeight < y < self.originY))

	def getDaysIndexFromChartX(self, x):
		index = (x - self.originX)/self.horizScalingFactor
		return index

	def getChartYFromPricesIndex(self, index):
		return (self.originY - self.prices[index] * self.vertScalingFactor)

class HomePage(Page):
	def __init__(self, change):
		super(HomePage, self).__init__(change)
		self.spotRateX, self.spotRateY = self.pageWidth/2, self.pageHeight*5/8
		self.lastRate = 0.0
	
	def draw(self, canvas, spotRate):
		if self.chartIntermediate:
			self.drawLoadingScreen(canvas)
		elif self.data:
			self.drawLoadingScreen(canvas)
		else:
			super(HomePage, self).draw(canvas, spotRate)
			canvas.create_rectangle(0, 0, self.pageWidth, self.pageHeight/4,
				fill = rgbString(30, 104, 255), outline=rgbString(30, 104, 255))
			canvas.create_text(self.appNameX, self.appNameY, 
				text = "bitPredict", fill = "snow", 
				font = "Trebuchet 100 bold italic")
			if self.chart:
				self.change(ChartPage)
			else:
				canvas.create_text(self.spotRateX, self.spotRateY, 
					text = "$ "+spotRate, fill = "black", 
					font = "Helvetica 200 bold")
				self.lastRate = float(spotRate)
			self.makeLogInButton(canvas)

	def makeLogInButton(self, canvas):
		lineSpace, vertR, horizR = 40, 20, 60
		self.butX, self.butY = self.pageWidth*3/4, self.pageHeight/8
		canvas.create_rectangle(self.butX - horizR, self.butY - vertR,
			self.butX + horizR, self.butY + vertR, fill = rgbString(0, 0, 128))
		canvas.create_text(self.butX, self.butY, text = "Log into Coinbase", 
			fill = "snow")

	def onMousePressed(self, event):
		x, y = event.x, event.y
		inpFieldVertR, inpFieldHorizR, butVertR, butHorizR = 10, 100, 20, 60
		if (self.butX - butHorizR < x < self.butX + butHorizR and 
			self.butY - butVertR < y < self.butY + butVertR):
			browser = webbrowser.get()
			browser.open_new_tab("https://www.coinbase.com")
		else:
			super(HomePage, self).onMousePressed(event)

	def onMouseMotion(self, event):
		pass

	def onKeyPressed(self, event):
		pass

class PredictPage(Page):
	def __init__(self, change):
		super(PredictPage, self).__init__(change)
		self.predict = True
		self.intention, self.intentionRecorded, self.trend = None, False, None
		self.frozen = False
		wby2, h, spacing = 50, 40, 100
		self.originX = float(self.pageWidth)/4 
		self.originY = float(self.pageHeight)*3/4
		self.horizPixelLimit = self.pageWidth/2
		self.vertPixelLimit = self.pageHeight/2
		path = "tempDir" + os.sep + "bitcoinHistory2.txt"
		(self.xi, self.yi) = self.getPastOneDayData(path)
		self.ymax, self.ymin = max(self.yi) + 5, min(self.yi) - 5 # in dollars
		self.xmax = -1 * self.xi[-1] # in seconds
		self.horizScalingFactor = float(self.horizPixelLimit)/self.xmax
		self.vertScalingFactor = (float(self.vertPixelLimit)/(self.ymax - 
			self.ymin))
		self.initializeFrozenAndPromptVariables()

	def initializeFrozenAndPromptVariables(self):
		wby2, h, spacing = 50, 40, 100
		self.freezeX1 = self.pageWidth/2 - wby2
		self.freezeX2 = self.pageWidth/2 + wby2
		self.freezeY1 = self.pageHeight - spacing - h/2
		self.freezeY2 = self.pageHeight - spacing + h/2
		self.promptToBuy, self.promptToSell = False, False

	def draw(self, canvas, spotRate):
		if self.chartIntermediate:
			self.drawLoadingScreen(canvas)
		elif self.data:
			self.drawLoadingScreen(canvas)
		else:
			super(PredictPage, self).draw(canvas, spotRate)
			if not self.intentionRecorded:
				self.drawBanner(canvas)
				self.displaySpotRateInSnow(canvas, spotRate)
				self.drawWhenIntentionNotRecorded(canvas)
			else:
				self.displaySpotRateInCorner(canvas, spotRate)
				if self.wait:
					self.drawWaitPrediction(canvas)
				elif self.buy:
					self.drawBuyPrediction(canvas)
				elif self.sell:
					self.drawSellPrediction(canvas)
				self.plotLinRegChart(canvas)
				self.showLegend(canvas)

	def showLegend(self, canvas):
		startX = self.originX + self.horizPixelLimit
		canvas.create_text(startX, 200, anchor = W,
			text = "Resistance Line: $ " + str(self.resistanceLine), 
			fill = rgbString(0, 100, 0))
		canvas.create_text(startX, 300, anchor = W,
			text = ("Linear regression curve: \ny = "+str(self.slope)+"x + " +
				str(self.intercept)), fill = "blue")
		canvas.create_text(startX, 400, anchor = W,
			text = "Support Line: $ " + str(self.supportLine),
			fill = "red")
		#canvas.create_text()

	def drawWaitPrediction(self, canvas):
		self.trend = self.determineRecentTrend()
		if ((self.intention == "b" or self.intention == "f") and 
			self.trend == "decreasing"):
			message = self.getWaitMessageForSimilarTrendAndIntention()
		elif ((self.intention == "b") and self.trend == "increasing"):
			message = self.getWaitMessageForOppositeTrendAndIntention()
		elif (self.intention == "s" and self.trend == "decreasing"):
			message = self.getWaitMessageForOppositeTrendAndIntention()
		elif ((self.intention == "s" or self.intention == "f") and 
			self.trend == "increasing"):
			message = self.getWaitMessageForSimilarTrendAndIntention()
		canvas.create_text(self.pageWidth/2, self.pageHeight/8, text = message, 
			font = "Helvetica 14 bold")

	def getWaitMessageForSimilarTrendAndIntention(self):
		# decreasing -> buy
		# increasing -> sell
		if self.trend == "decreasing":
			limitLine = str(self.supportLine)
		else:
			limitLine = str(self.resistanceLine)
		if self.intention == "b" or self.intention == "f":
			activity = "buy"
		else:
			activity = "sell"
		behavior = "drop" if self.trend == "decreasing" else "rise"
		message = ("Please wait for a while, the price is in a %s\n" + 
			"trend. As the prices %s further upto $%s, \n" + 
			"you should %s.") %(self.trend, behavior, limitLine, activity)
		return message

	def getWaitMessageForOppositeTrendAndIntention(self):
		# decreasing -> sell
		# increasing -> buy
		if self.intention == "f":
			for intent in "bs":
				message += self.setValuesAndGetMessage(intent)
			return message
		else:
			message = self.setValuesAndGetMessage(self.intention)
			return message

	def setValuesAndGetMessage(self, intent):
		activity = "buy" if intent == "b" else "sell"
		behavior = "rise" if self.trend == "decreasing" else "drop"
		hilo = "high" if self.trend == "decreasing" else "low"
		if self.trend == "decreasing":
			limitLine = str(self.resistanceLine)
		else:
			limitLine = str(self.supportLine)
		message = ("At the moment, prices are %s. This is not a\n" + 
				" bad time to %s, but it may not be a very good time to %s \n" + 
				" as we anticipate the price to %s further than the current\n" + 
				" price eventually, i.e. at least as %s as $%s \n") %(self.trend, 
				activity, activity, behavior, hilo, limitLine)
		return message

	def drawBuyPrediction(self, canvas):
		self.trend = self.determineRecentTrend()
		if ((self.intention == "b" or self.intention == "f") 
			and self.trend == "decreasing"):
			message = self.getBuyPredictionWithFreezeForDecreasingTrend(canvas)
		elif ((self.intention == "b" or self.intention == "f") 
			and self.trend == "increasing"):
			message = ("Current price is low, but it's rising. BUY NOW!")
		elif (self.intention == "s" and self.trend == "decreasing"):
			message = self.getBuyPredictionForSellIntentionAndDecreasingTrend()
		elif (self.intention == "s" and self.trend == "increasing"):
			message = ("Prices are lower than usual right now, and increasing." 
				+ "\n This is the time to wait to sell. Although you want to" + 
				" sell," + "\nthis is a great time to buy.")
		canvas.create_text(self.pageWidth/2, self.pageHeight/8, text = message,
			font = "Helvetica 14 bold")

	def getBuyPredictionWithFreezeForDecreasingTrend(self, canvas):
		message = ("This is a good time to buy. But the trend is\n" + 
				" decreasing, so prices will fall further. Click FREEZE if\n" + 
				" you want to be prompted when to buy." )
		wby2, h = 50, 40
		canvas.create_rectangle(self.freezeX1, self.freezeY1, 
			self.freezeX2, self.freezeY2, fill = rgbString(30, 104, 255))
		canvas.create_text(self.freezeX1 + wby2, self.freezeY1 + h/2, 
			text = "FREEZE!", fill = "snow")
		self.promptToBuy = True
		return message

	def getBuyPredictionForSellIntentionAndDecreasingTrend(self):
		message = ("This is not a bad time to sell because prices are\n" + 
				" decreasing, but we anticipate" + " the price to rise as\n" + 
				" high as " + str(self.resistanceLine) + " eventually.\n" + 
				" Although you want to sell, this might be a good\n" +
				" time to buy or wait for the prices to fall further.")
		return message

	def drawSellPrediction(self, canvas):
		self.trend = self.determineRecentTrend()
		wby2, h = 50, 40
		if ((self.intention == "s" or self.intention == "f") and 
			self.trend == "decreasing"):
			message = ("Current price is high, but it's dropping. SELL NOW!")
		elif ((self.intention == "s" or self.intention == "f") and 
			self.trend == "increasing"):
			message = self.getSellPredictionWithFreezeForIncreasingTrend(canvas)
		elif self.intention == "b" and self.trend == "decreasing":
			message = ("Prices are higher than usual right now, and decreasing."
				+ " \nThis is the time to wait to buy. Although you want to" + 
				" buy, \nthis is a great time to sell.")
		elif self.intention == "b" and self.trend == "increasing":
			message = self.getSellPredictionForBuyIntentionAndIncreasingTrend()
		canvas.create_text(self.pageWidth/2, self.pageHeight/8, text = message,
			font = "Helvetica 14 bold")

	def getSellPredictionWithFreezeForIncreasingTrend(self, canvas):
		message = ("This is a good time to sell. But the price is \n" + 
				"increasing, so prices will rise further. Click FREEZE if\n" + 
				" you want to be prompted when to sell.")
		canvas.create_rectangle(self.freezeX1, self.freezeY1, 
			self.freezeX2, self.freezeY2, fill = rgbString(30, 104, 255))
		canvas.create_text(self.freezeX1 + wby2, self.freezeY1 + h/2, 
			text = "FREEZE!", fill = "snow")
		self.promptToSell = True
		return message

	def getSellPredictionForBuyIntentionAndIncreasingTrend(self):
		message = ("This is not a bad time to buy because prices are\n" + 
				" increasing, but we anticipate" + " the price to fall as\n" + 
				" low as " + str(self.supportLine) + " eventually.\n" + 
				" Although you want to buy, this might be a good\n" +
				" time to sell or wait for the prices to rise further.")
		return message

	def drawWhenIntentionNotRecorded(self, canvas):
		intentMessage = ("What do you intend to do?\n" + 
			"Press B if you intend to buy\n"+"Press S if you intend to sell\n"+
			"Press F if you're flexible.")
		canvas.create_text(self.pageWidth/2, self.pageHeight/2,
			text = intentMessage, font = "Georgia 20 bold")

	def onKeyPressed(self, event):
		if not self.intentionRecorded:
			if event.char == "b" or event.char == "s" or event.char == "f":
				self.intention = event.char
				self.intentionRecorded = True
				self.prediction()

	def onMousePressed(self, event):
		x, y = event.x, event.y
		if (self.intentionRecorded and 
			(self.freezeX1 < x < self.freezeX2) and 
			(self.freezeY1 < y < self.freezeY2)):
			self.frozen = True
		else:
			super(PredictPage, self).onMousePressed(event)

	def prediction(self):
		self.resistanceLine = self.getResistanceLine()
		self.supportLine = self.getSupportLine()
		self.spotRate = float(getSpotRate())
		margin = 0.1 # in dollars
		if (self.supportLine + margin <= self.spotRate <= 
			self.resistanceLine - margin):
			self.wait, self.buy, self.sell = True, False, False
		elif self.spotRate < self.supportLine + margin:
			self.wait, self.buy, self.sell = False, True, False
		elif self.spotRate > self.resistanceLine + margin:
			self.wait, self.buy, self.sell = False, False, True
		
	def onMouseMotion(self, event): 
		pass

	def getPastOneDayData(self, filename):
		# sifts through the file and creates two arrays of time coordinate and 
		# varying bitcoin price. This is to implement the short term linear rgn
		contents = makeFileIntoArray(filename)
		now, then, idx = datetime.now(), datetime.now(), 0
		diff, xi, yi = now - then, [ ], [ ]
		xi += [0]
		yi += [float(getSpotRate())]
		while diff.days < 1:
			yrIdx, mIdx, dIdx, hIdx, minIdx, priceIdx = 4, 5, 8, 10, 13, 15
			year = int(contents[idx][0:yrIdx])
			month = int(contents[idx][mIdx:mIdx+2])
			day = int(contents[idx][dIdx:dIdx+2]) 
			hour = int(contents[idx][hIdx:hIdx+2])
			minute = int(contents[idx][minIdx:minIdx+2])
			price = float(contents[idx][priceIdx:])
			then = datetime(year, month, day, hour, minute)
			diff = now - then
			idx += 1
			xi += [-1*diff.seconds]
			yi += [price]
		# do not consider last element because that was beyond a day old
		return (xi[:-1], yi[:-1])

	def linearRegression(self, xi, yi):
		# returns the equation of the line that best approximates all sets of 
		# points (xi, yi), where xi = time coordinate, yi = bitcoin price
		matXi = [[0] for i in xrange(len(xi))]
		for i in xrange(len(xi)):
			matXi[i] = [xi[i]]
		X = Matrix(len(xi), 1, matXi)
		X = X.append(1)
		y = Vector(len(yi), yi)
		lstsqVector = leastSquares(X,y)
		# Performs a technique called least squares approximation in linear alg
		return lstsqVector.entries

	def plotLinRegChart(self, canvas):
		# plots a graph of bitcoin variation over the past one day
		# self.xi is going from most recent timestamp to oldest timestamp
		# we want to plot the chart in reverse order.
		# first translate all the entries of xi. translation will be done by
		# adding self.xi[-1]
		xi = self.translate() # translated
		# all entries are now non negative in decreasing order.
		# we can plot as (xi, yi) now.
		oldScreenX = self.originX
		oldScreenY = (self.originY - self.vertScalingFactor * 
			(self.yi[-1] - self.ymin))
		# traversing xi in reverse order now
		for index in xrange(-2, -len(xi)-1, -1):
			chartX, chartY = xi[index], self.yi[index] - self.ymin
			screenX = self.originX + chartX * self.horizScalingFactor
			screenY = self.originY - chartY * self.vertScalingFactor
			canvas.create_oval(screenX - 1, screenY - 1, screenX + 1, screenY+1)
			canvas.create_line(screenX, screenY, oldScreenX, oldScreenY)
			oldScreenX, oldScreenY = screenX, screenY
		self.drawLinRegScaledAxes(canvas)
		self.drawLinRegCurve(canvas)
		self.plotResistanceLine(canvas)
		self.plotSupportLine(canvas)

	def drawLinRegScaledAxes(self, canvas):
		marginY = 20
		canvas.create_line(self.originX, self.originY, 
			self.originX + self.horizPixelLimit, self.originY)
		canvas.create_line(self.originX, self.originY, 
			self.originX, self.originY - self.vertPixelLimit)
		canvas.create_text(self.originX, self.originY + marginY, 
			text = "One day back")
		canvas.create_text(self.originX - self.xi[-1] * self.horizScalingFactor,
			self.originY + marginY, text = self.format(date.today()))
		self.hashYAxis(canvas)

	def drawLinRegCurve(self, canvas):
		lineVector = self.linearRegression(self.xi, self.yi)
		slope, intercept = lineVector[0], lineVector[1]
		xi = self.translate()
		oldScreenX = self.originX
		oldScreenY = (self.originY - 
			(slope * self.xi[-1] + intercept - self.ymin) * 
			self.vertScalingFactor)
		screenX = self.originX + xi[0] * self.horizScalingFactor
		screenY = (self.originY - (intercept - self.ymin) * 
			self.vertScalingFactor)
		canvas.create_line(screenX, screenY, oldScreenX, oldScreenY, 
			fill = "blue", width = 4)

	def plotResistanceLine(self, canvas):
		self.resistanceLine = self.getResistanceLine()
		y = (self.originY - (self.resistanceLine - self.ymin) *
			self.vertScalingFactor)
		canvas.create_line(self.originX, y, 
						self.originX + self.horizPixelLimit, y,
						fill = rgbString(0, 100, 0), width = 4)

	def plotSupportLine(self, canvas):
		self.supportLine = self.getSupportLine()
		y = (self.originY - (self.supportLine - self.ymin) * 
			self.vertScalingFactor)
		canvas.create_line(self.originX, y, 
						self.originX + self.horizPixelLimit, y,
						fill = "red", width = 4)

	def hashYAxis(self, canvas):
		margin = 30
		for price in [self.ymin, self.ymax]:
			canvas.create_text(self.originX - margin, 
				self.originY - self.vertScalingFactor*(float(price)-self.ymin), 
				text = "$ "+str(float(price)))

	def format(self, date):
		months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", 
			"Oct", "Nov", "Dec"]
		month = months[date.month - 1]
		day = date.day
		return str(month) + " " + str(day)

	def translate(self):
		translatingFactor = -1 * self.xi[-1]
		xi = [0 for i in xrange(len(self.xi))]
		for i in xrange(len(self.xi)):
			xi[i] = self.xi[i] + translatingFactor
		return xi

	def determineRecentTrend(self):
		# returns a string determining increasing or decreasing trend
		path =  "tempDir" + os.sep + "bitcoinHistory2.txt"
		arr = self.linearRegression(self.xi, self.yi)
		self.slope, self.intercept = arr[0], arr[1]
		if self.slope < 0:
			return "decreasing"
		else:
			return "increasing"

	def displaySpotRateInSnow(self, canvas, spotRate):
		lineSpace = 100
		canvas.create_text(self.pageWidth, 0, anchor = NE, 
			text = "$ " + spotRate, font = "Helvetica 50 bold",
			fill = "snow")

class ChartPage(Page):
	def __init__(self, change):
		super(ChartPage, self).__init__(change)
		self.chart = True
		self.want1Year = True
		self.want6Months = False
		self.want3Months = False
		self.want1Month = False
		self.tooltip = False 
		self.tooltipX = None
		self.tooltipY = None
		self.tooltipText = None
		self.justStarted = False
		self.initializeAndMemoize()
		self.setButtonLocations()
		
	def initializeAndMemoize(self):
		self.lengthOfXAxisInPixels, self.lengthOfYAxisInPixels = 1000, 300
		self.chartWidth = self.lengthOfXAxisInPixels 
		self.chartHeight = self.lengthOfYAxisInPixels
		leftMargin, botMargin = 150, 150
		self.originX = leftMargin
		self.originY = self.pageHeight - botMargin
		filename = "tempDir" + os.sep + "bitcoinHistory2.txt"
		(self.days1Year, self.prices1Year) = self.getOneYearData(filename)
		(self.days6Months, self.prices6Months) = self.getNMonthsData(filename,6)
		(self.days3Months, self.prices3Months) = self.getNMonthsData(filename,3)
		(self.days1Month, self.prices1Month) = self.getNMonthsData(filename,1)
		self.days, self.prices = self.days1Year, self.prices1Year
		self.xmax, self.ymax = len(self.days), max(self.prices)
		self.horizScalingFactor = float(self.lengthOfXAxisInPixels)/self.xmax
		# pixel per day
		self.vertScalingFactor = float(self.lengthOfYAxisInPixels)/self.ymax
		# pixel per dollar

	def setButtonLocations(self):
		left, top, dist = 100, 50, 200
		cx, cy = left, top
		self.timeButY = cy # y coordinate common for all time buttons
		self.oneYrButX = cx
		cx += dist
		self.sixMthButX = cx
		cx += dist
		self.thrMthButX = cx
		cx += dist
		self.oneMthButX = cx

	def onMousePressed(self, event):
		x, y = event.x, event.y
		wby2, h = 50, 40
		if self.timeButY - h/2 < y < self.timeButY + h/2:
			if self.oneYrButX - wby2 < x < self.oneYrButX + wby2:
				self.mousePressedFor1Year()
			elif self.sixMthButX - wby2 < x < self.sixMthButX + wby2:
				self.mousePressedFor6Months()
			elif self.thrMthButX - wby2 < x < self.thrMthButX + wby2:
				self.mousePressedFor3Months()
			elif self.oneMthButX - wby2 < x < self.oneMthButX + wby2:
				self.mousePressedFor1Month()
		else:
			super(ChartPage, self).onMousePressed(event)

	def mousePressedFor1Year(self):
		self.tooltip = False
		self.want1Year = True
		self.want6Months = False 
		self.want3Months = False 
		self.want1Month = False

	def mousePressedFor6Months(self):
		self.tooltip = False
		self.want1Year = False
		self.want6Months = True 
		self.want3Months = False 
		self.want1Month = False

	def mousePressedFor3Months(self):
		self.tooltip = False
		self.want1Year = False
		self.want6Months = False
		self.want3Months = True
		self.want1Month = False

	def mousePressedFor1Month(self):
		self.tooltip = False
		self.want1Year = False
		self.want6Months = False
		self.want3Months = False
		self.want1Month = True

	def onMouseMotion(self, event):
		x, y, space = event.x, event.y, 30
		if self.inChart(x, y):
			index = int(self.getDaysIndexFromChartX(x))
			chartY = self.getChartYFromPricesIndex(index)
			self.tooltip = True
			self.mouseX, self.mouseY = x, chartY
			self.tooltipText = (self.display(self.days[index]) + "\n$" + 
				str(self.prices[index]))
			self.tooltipX, self.tooltipY = x, chartY - space

	def draw(self, canvas, spotRate):
		super(ChartPage, self).draw(canvas, spotRate)
		if self.chartIntermediate: self.drawLoadingScreen(canvas)
		elif self.data: self.drawLoadingScreen(canvas)
		else:
			self.displaySpotRateInCorner(canvas, spotRate)
			self.makeButton(canvas, self.oneYrButX, self.timeButY, 
				"Last one year")
			self.makeButton(canvas, self.sixMthButX, self.timeButY, 
				"Last 6 months")
			self.makeButton(canvas, self.thrMthButX, self.timeButY, 
				"Last 3 months")
			self.makeButton(canvas, self.oneMthButX, self.timeButY, 
				"Last 1 month")
			if self.want1Year: self.plotChart(canvas, 12)
			elif self.want6Months: self.plotChart(canvas, 6)
			elif self.want3Months: self.plotChart(canvas, 3)
			elif self.want1Month: self.plotChart(canvas, 1)
			if self.tooltip:
				self.displayTooltip(canvas)

	def makeButton(self, canvas, cx, cy, stringOfText):
		wby2, h = 50, 40
		canvas.create_rectangle(cx - wby2, cy - h/2, cx + wby2, cy + h/2,
								fill = rgbString(30, 104, 255), 
								outline = rgbString(30, 104, 255))
		canvas.create_text(cx, cy, text = stringOfText, fill = "snow")

	def displayTooltip(self, canvas):
		rx, ry = 25, 15
		canvas.create_oval(self.mouseX-3, self.mouseY-3, 
			self.mouseX+3, self.mouseY+3, fill = "blue")
		canvas.create_rectangle(self.tooltipX - rx, self.tooltipY - ry, 
			self.tooltipX + rx, self.tooltipY + ry, fill = "yellow")
		canvas.create_text(self.tooltipX, self.tooltipY, 
			text = self.tooltipText, font = "Mono 10 bold")

	def onKeyPressed(self, event):
		pass

class PersonalizedCharts(Page):
	def __init__(self, change):
		super(PersonalizedCharts, self).__init__(change)
		wby2, h, spacing = 50, 40, 100
		self.okX1 = self.pageWidth/2 - wby2
		self.okX2 = self.pageWidth/2 + wby2
		self.okY1 = self.pageHeight - spacing - h/2
		self.okY2 = self.pageHeight - spacing + h/2
		self.okPressed = False
		self.showInstructions = False
		self.tooltip = False 
		self.tooltipX = None
		self.tooltipY = None
		self.tooltipText = None

	def draw(self, canvas, spotRate):
		if self.chartIntermediate:
			self.drawLoadingScreen(canvas)
		elif self.data:
			self.drawLoadingScreen(canvas)
		else:
			super(PersonalizedCharts, self).draw(canvas, spotRate)
			if not self.showInstructions:
				if not self.okPressed:
					self.drawWhenOKNotPressed(canvas)
					self.displaySpotRateInCorner(canvas, spotRate)
				else:
					self.drawBanner(canvas)
					self.displaySpotRateInCorner(canvas, spotRate)
					self.plotChart(canvas, 1)
					self.plotResistanceLine(canvas)
					self.plotSupportLine(canvas)
					self.getPurchaseHistory()
					self.plotBuyPoints(canvas)
					self.plotSellPoints(canvas)
					w, h = 200, 50
					if self.tooltip:
						canvas.create_rectangle(self.tooltipX - w/2,
												self.tooltipY - h/2,
												self.tooltipX + w/2,
												self.tooltipY + h/2,
												fill = "yellow")
						canvas.create_text(self.tooltipX, self.tooltipY,
							text = self.tooltipText)
			else:
				self.drawBanner(canvas)
				self.displayInstructions(canvas)
				self.displaySpotRateInCorner(canvas, spotRate)

	def drawWhenOKNotPressed(self, canvas):
		self.drawBanner(canvas)
		wby2, h = 50, 40
		self.drawWhenInstructionsNotShown(canvas)
		canvas.create_rectangle(self.okX1, self.okY1, 
								self.okX2, self.okY2, 
								fill = rgbString(30, 104, 255))
		canvas.create_text(self.pageWidth/2, self.pageHeight - 100, 
							text = "OK!", fill = "snow")
		# because spacing = 100

	def getPurchaseHistory(self):
		path = "tempDir" + os.sep + "userData.txt"
		with open(path, "rt") as fin:
			self.purchaseHistory = fin.read()
		self.purchaseHistory = self.purchaseHistory.split("\n")
		self.balance = float(self.purchaseHistory[0])
		for i in xrange(1, len(self.purchaseHistory)):
			self.purchaseHistory[i] = self.purchaseHistory[i].split(",")
			newArray = (self.purchaseHistory[i][0].split("@") + 
						[self.purchaseHistory[i][1]])
			self.purchaseHistory[i-1] = newArray
			# self.purhaseHistory is a 2d list.
		self.purchaseHistory = self.purchaseHistory[:-1] 
		# to ignore last entry, which was copied to -2'th entry

	def plotBuyPoints(self, canvas):
		for i in xrange(len(self.purchaseHistory)):
			if self.purchaseHistory[i][0][0] == '+':
				priceBoughtAt = float(self.purchaseHistory[i][1])
				dateBoughtAt = self.purchaseHistory[i][2]
				recordedIndex = 0
				for j in xrange(len(self.days)):
					if str(self.days[j]) == dateBoughtAt:
						recordedIndex = j
						break
				canvas.create_oval(
					self.originX + recordedIndex * self.horizScalingFactor - 5,
					self.originY - priceBoughtAt * self.vertScalingFactor - 5,
					self.originX + recordedIndex * self.horizScalingFactor + 5,
					self.originY - priceBoughtAt * self.vertScalingFactor + 5,
					fill = "red"
					)

	def plotSellPoints(self, canvas):
		for i in xrange(len(self.purchaseHistory)):
			if self.purchaseHistory[i][0][0] == '-':
				priceSoldAt = float(self.purchaseHistory[i][1])
				dateSoldAt = self.purchaseHistory[i][2]
				recordedIndex = 0
				for j in xrange(len(self.days)):
					if str(self.days[j]) == dateSoldAt:
						recordedIndex = j
						break
				canvas.create_oval(
					self.originX + recordedIndex * self.horizScalingFactor - 5,
					self.originY - priceSoldAt * self.vertScalingFactor - 5,
					self.originX + recordedIndex * self.horizScalingFactor + 5,
					self.originY - priceSoldAt * self.vertScalingFactor + 5,
					fill = "green"
					)

	def plotResistanceLine(self, canvas):
		self.resistanceLine = self.getResistanceLine()
		y = self.originY - self.resistanceLine * self.vertScalingFactor
		canvas.create_line(self.originX, y, 
						self.originX + self.lengthOfXAxisInPixels, y,
						fill = "green", width = 4)

	def plotSupportLine(self, canvas):
		self.supportLine = self.getSupportLine()
		y = self.originY - self.supportLine * self.vertScalingFactor
		canvas.create_line(self.originX, y, 
						self.originX + self.lengthOfXAxisInPixels, y,
						fill = "red", width = 4)

	def drawWhenInstructionsNotShown(self, canvas):
		dist = 100
		wby2, h = 50, 40
		message = ("Press H to know how to enter your purchase history\n" + 
			"Click OK when you are done entering your data")
		canvas.create_text(self.pageWidth/2, self.pageHeight/2,
			text = message, font = "Helvetica 20 bold")
		canvas.create_rectangle(self.okX1, self.okY1, self.okX2, self.okY2, 
			fill = rgbString(30, 104, 255))
		canvas.create_text(self.okX1 + wby2, self.okY1 + h/2, 
			text = "OK!", fill = "snow")

	def displayInstructions(self, canvas):
		instructions = ("\n"+
			"Please enter your purchase history for the last one month\n" + 
			" in the text file, userData.txt, in tempDir, as follows:\n"+ 
			"Enter your balance (in BTC) as the first line of the file.\n" +
			"If you bought BTC 1.3481 at $500.12 per BTC on Nov 23, 2014"+ 
			",\n enter the details as follows:\n+1.3481@500.12,2014-11-23"+
			"\nIf you sold BTC 1.3481 at $500.12 per BTC on Nov 25, 2014," + 
			"\n enter the details as follows: \n-1.3481@500.12,2014-11-25" + 
			"\nPress H to go back")
		canvas.create_text(self.pageWidth/2, self.pageHeight/2,
			text = instructions, font = "Helvetica 20 bold")

	def onMousePressed(self, event):
		x, y = event.x, event.y
		if (not self.showInstructions and 
			((self.okX1 < x < self.okX2) and (self.okY1 < y < self.okY2))):
			self.okPressed = True
		else:
			super(PersonalizedCharts, self).onMousePressed(event)

	def onMouseMotion(self, event):
		if self.okPressed:
			x, y = event.x, event.y
			if self.inChart(x, y):
				index = int(self.getDaysIndexFromChartX(x))
				if self.onResistanceLine(x, y):
					self.mouseMotionOnResistanceLine(x, y)
				elif self.onSupportLine(x, y):
					self.mouseMotionOnSupportLine(x, y)
				else:
					self.tooltip = False

	def mouseMotionOnResistanceLine(self, x, y):
		space = 30
		self.tooltipX = x 
		self.tooltipY = (self.originY - 
			self.resistanceLine * self.vertScalingFactor - space)
		self.tooltip = True
		self.tooltipText = ("Resistance Line: " + str(self.resistanceLine))

	def mouseMotionOnSupportLine(self, x, y):
		space = 30
		self.tooltipX = x 
		self.tooltipY = (self.originY - 
			self.supportLine * self.vertScalingFactor - space)
		self.tooltip = True
		self.tooltipText = ("Support Line: " + str(self.supportLine))

	def onResistanceLine(self, x, y):
		return (abs(y - int(self.originY - 
			self.resistanceLine * self.vertScalingFactor)) < 4)

	def onSupportLine(self, x, y):
		return (abs(y - int(self.originY - 
			self.supportLine * self.vertScalingFactor)) < 4)

	def inChart(self, x, y):
		if (self.originX < x < self.originX + self.lengthOfXAxisInPixels and
			self.originY - self.lengthOfYAxisInPixels < y < self.originY):
			return True
		return False

	def onKeyPressed(self, event):
		if event.char == "h":
			self.showInstructions = not self.showInstructions

	def displaySpotRateInCorner(self, canvas, spotRate):
		lineSpace = 100
		canvas.create_text(self.pageWidth, 0, anchor = NE, 
			text = "$ " + spotRate, font = "Helvetica 50 bold",
			fill = "snow")

class Help(Page):
	def __init__(self, change):
		super(Help, self).__init__(change)
		self.wantAlgorithm = False

	def draw(self, canvas, spotRate):
		super(Help, self).draw(canvas, spotRate)
		self.drawBanner(canvas)
		self.displaySpotRateInCorner(canvas, spotRate)
		if self.wantAlgorithm:
			self.displayAlgorithmInfo(canvas)
		else:
			self.displayHelp(canvas)

	def displayHelp(self, canvas):
		space = 20
		filename = "tempDir" + os.sep + "about.txt"
		with open(filename, "rt") as fin:
			self.helpMessage = fin.read()
		canvas.create_text(self.pageWidth/2, self.pageHeight/2 + space, 
			text = self.helpMessage)

	def displayAlgorithmInfo(self, canvas):
		space = 50
		filename = "tempDir" + os.sep + "algoInfo.txt"
		with open(filename, "rt") as fin:
			self.algo = fin.read()
		canvas.create_text(self.pageWidth/2, self.pageHeight/2 + space,
			text = self.algo)

	def onMousePressed(self, event):
		super(Help, self).onMousePressed(event)

	def onMouseMotion(self, event):
		pass

	def onKeyPressed(self, event):
		if event.char == "a":
			self.wantAlgorithm = not self.wantAlgorithm
		elif event.char == "b":
			browser = webbrowser.get()
			browser.open_new_tab("http://en.wikipedia.org/wiki/Bitcoin")

	def displaySpotRateInCorner(self, canvas, spotRate):
		lineSpace = 100
		canvas.create_text(self.pageWidth, 0, anchor = NE, 
			text = "$ " + spotRate, font = "Helvetica 50 bold",
			fill = "snow")

# SHORT TERM LINEAR REGRESSION IMPLEMENTED BELOW

bitPredict = Application()
bitPredict.run()

def listsAlmostEqual(list1, list2):
	assert len(list1) == len(list2)
	for i in xrange(len(list1)):
		if almostEqual(list1[i], list2[i]): pass
		else: return False
	return True

def almostEqual(num1, num2, epsilon = 10 ** -6):
	return abs(num1 - num2) < epsilon

def testLeastSquares():
	print "Testing leastSquares...",
	A, b = Matrix(3, 2, [[3, 1], [1, 1], [1, 2]]), Vector(3, [1, 1, 1])
	assert listsAlmostEqual(leastSquares(A, b).entries, [1.0/5, 7.0/15])
	print "Passed!"

def testMatrixAndVectorClasses():
	print "Testing Matrix and Vector Classes..."
	A = Matrix(3, 3,
		[
		[1, 2, 3],
		[4, 5, 6],
		[7, 8, 9]])
	B = Matrix(3, 3,
		[
		[1, 1, 2],
		[2, 3, 4],
		[5, 5, 7]])
	I = Matrix(3, 3, [[1, 0, 0], [0, 1, 0], [0, 0, 1]])
	scalar = 0.5
	testMatrixMultiplication(A, B)
	testMatrixScalarDivision(A, scalar)
	testDeterminant(A, B)
	testInverse(A, B, I)
	
def testMatrixMultiplication(A, B):
	C = A * B
	print "Testing matrix-matrix multiplication...",
	assert C.entries == [[20, 22, 31], [44, 49, 70], [68, 76, 109]]
	print "Passed!"
	print "Testing matrix-vector multiplication...",
	v = Vector(3, [9, 8, 7])
	assert type(A * v) == Vector
	assert (A * v).entries == [46, 118, 190]
	print "Passed!"
	print "Testing matrix-scalar multiplication...",
	scalar = 0.5
	M = A * scalar
	assert type(M) == Matrix
	assert M.entries == [[0.5, 1.0, 1.5], [2.0, 2.5, 3.0], [3.5, 4.0, 4.5]]
	print "Passed!"
	
def testMatrixScalarDivision(A, scalar):
	print "Testing matrix-scalar division...",
	N = A / scalar
	assert type(N) == Matrix
	assert N.entries == [[2, 4, 6], [8, 10, 12], [14, 16, 18]]
	print "Passed!"

def testDeterminant(A, B):
	print "Testing determinant...",
	assert A.determinant() == 0
	assert B.determinant() == -3
	print "Passed!"
	
def testInverse(A, B, I):
	print "Testing inverse...",
	try:
		A.inverse()
	except:
		pass
	assert I.inverse().entries == I.entries
	assert type(B.inverse()) == Matrix
	assert (B.inverse().entries == [
		[-1.0/3, -1, 2.0/3],
		[-2, 1, 0],
		[5.0/3, 0, -1.0/3]
		])
	print "Passed!"

testLeastSquares()
testMatrixAndVectorClasses()