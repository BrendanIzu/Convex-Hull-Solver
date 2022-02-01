import math

from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
    from PyQt4.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT6':
    from PyQt6.QtCore import QLineF, QPointF, QObject
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import time

# S ome global color constants that might be useful
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25

def slope(point1, point2):
    return (point1.y() - point2.y()) / (point1.x() - point2.x())    # O(1)

class Hull:
    def __init__(self, points):
        self.points = points
        self.left = min(points, key=lambda p: p.x())	# O(1)
        self.right = max(points, key=lambda p: p.x())   # O(1)

    def getNextCW(self, point):     # O(1)
        index = self.points.index(point)
        if index == len(self.points)-1:
            return self.points[0]
        else:
            return self.points[index+1]

    def getNextCCW(self, point):    # O(1)
        index = self.points.index(point)
        if index == 0:
            return self.points[len(self.points)-1]
        else:
            return self.points[index - 1]

def createHull(points):     # O(1)
    n = len(points)
    if n <= 3:
        return createOrderedHull(points)
    return mergeHulls(createHull(points[0:math.floor(n/2)]), createHull(points[math.floor(n/2):n]))

def createOrderedHull(points):  # O(1)
    n = len(points)
    if n < 3:
        return Hull(points)
    if n == 3:
        if slope(points[0],points[1]) > slope(points[0], points[2]):
            return Hull(points)
        else:
            return Hull([points[0], points[2], points[1]])
    else:
        print("error, more than 3 points in create ordered hull method")

def mergeHulls(hull1, hull2):
    point1 = hull1.right
    point2 = hull2.left

    slopePrevious = slope(point1, point2)
    leave = 0
    topPoint1 = point1
    topPoint2 = point2

    # time complexity for finding topPoints
    # worst case: O(n + n) -> O(n)
    # best case: O(1 + 1) -> O(1)
    # average case : O(n)

    while not leave:
        leave = 1
        while slope(hull1.getNextCCW(topPoint1), topPoint2) < slopePrevious:
            topPoint1 = hull1.getNextCCW(topPoint1)
            slopePrevious = slope(topPoint1, topPoint2)
            leave = 0
        while slope(topPoint1, hull2.getNextCW(topPoint2)) > slopePrevious:
            topPoint2 = hull2.getNextCW(topPoint2)
            slopePrevious = slope(topPoint1, topPoint2)
            leave = 0

    # time complexity is the same as for finding bottomPoints

    bottomPoint1 = point1
    bottomPoint2 = point2
    slopePrevious = slope(point1, point2)
    leave = 0
    while not leave:
        leave = 1
        while slope(hull1.getNextCW(bottomPoint1), bottomPoint2) > slopePrevious:
            bottomPoint1 = hull1.getNextCW(bottomPoint1)
            slopePrevious = slope(bottomPoint1, bottomPoint2)
            leave = 0
        while slope(bottomPoint1, hull2.getNextCCW(bottomPoint2)) < slopePrevious:
            bottomPoint2 = hull2.getNextCCW(bottomPoint2)
            slopePrevious = slope(bottomPoint1, bottomPoint2)
            leave = 0

    q1 = []
    q2 = []
    q3 = []
    q4 = []

    # time complexity for adding final hull points
    # worst case: O(n + n) -> O(n)
    # best case: O(1 + 1) -> O(1)
    # average case: O(1)

    current = hull1.left
    while True:
        q1.append(current)
        if current == topPoint1:
            break
        else:
            current = hull1.getNextCW(current)

    current = topPoint2
    while True:
        q2.append(current)
        if current == hull2.right:
            break
        else:
            current = hull2.getNextCW(current)

    current = hull2.right
    while True:
        if current == bottomPoint2:
            break
        else:
            current = hull2.getNextCW(current)
            q3.append(current)

    current = bottomPoint1
    while True:
        if current == hull1.left:
            break
        else:
            q4.append(current)
            current = hull1.getNextCW(current)

    return Hull(q1+q2+q3+q4)

class ConvexHullSolver(QObject):

# Class constructor
    def __init__( self):
        super().__init__()
        self.pause = False

# Some helper methods that make calls to the GUI, allowing us to send updates
# to be displayed.

    def showTangent(self, line, color):
        self.view.addLines(line,color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseTangent(self, line):
        self.view.clearLines(line)

    def blinkTangent(self,line,color):
        self.showTangent(line,color)
        self.eraseTangent(line)

    def showHull(self, polygon, color):
        self.view.addLines(polygon,color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseHull(self,polygon):
        self.view.clearLines(polygon)

    def showText(self,text):
        self.view.displayStatusText(text)

# This is the method that gets called by the GUI and actually executes
# the finding of the hull

    def compute_hull( self, points, pause, view):
        self.pause = pause
        self.view = view
        assert( type(points) == list and type(points[0]) == QPointF )

        t1 = time.time()
        # time complexity for quicksort of points is O(nlogn)
        points.sort(key=lambda p: p.x())

        t2 = time.time()
        t3 = time.time()

        solvedHull = createHull(points)
        polygon = [QLineF(solvedHull.points[i],solvedHull.points[(i+1)%len(solvedHull.points)]) for i in range(len(solvedHull.points))]
        t4 = time.time()

        # when passing lines to the display, pass a list of QLineF objects.  Each QLineF
        # object can be created with two QPointF objects corresponding to the endpoints
        self.showHull(polygon,RED)
        self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))

