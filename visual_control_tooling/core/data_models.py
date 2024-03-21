# -*- coding: utf-8 -*

from visual_control_tooling.core.enums import Orientation

"""
Here we put dumb data structures, POJOs if you will
"""

class Resolution:

	def __init__(self, width: int, height: int):
		self.width = width
		self.height = height

	def toString(self):
		return f"Resolution, width : {self.width}, height {self.height}"


class Point:

	def __init__(self, x: int, y: int):
		self.x = x
		self.y = y

	def toString(self):
		return f"Point : x={self.x}, y={self.y}"

	def to_tuple(self):
		return int(self.x), int(self.y)


class Area:

	def __init__(self, topleft_xy: Point, resolution: Resolution):
		self.topleft_xy = topleft_xy
		self.resolution = resolution

	def toString(self):
		return f"Area, {self.topleft_xy}, {self.resolution}"


class Rectangle:

	def __init__(self, top_left_xy: Point, bottom_right_xy:Point):
		self.top_left_xy = top_left_xy
		self.bottom_right_xy = bottom_right_xy

	def toString(self):
		tl_str = f"topLeft_yx = ({self.top_left_xy.x}, {self.top_left_xy.y})"
		br_str = f"bottomRight_xy = ({self.bottom_right_xy.x}, {self.bottom_right_xy.y})"
		return f"Rectangle : {tl_str}, {br_str}"

class ScreenAreaParams:
	"""
	this class represents the window you want to control, that I call the screen_area
	"""

	def __init__(self, absolute_topleft_point: Point, absolute_bottomright_point: Point, width: int, height: int, orientation: Orientation):
		self.absolute_topleft_point: Point = absolute_topleft_point
		self.absolute_bottomright_point: Point = absolute_bottomright_point
		self.height: int = height
		self.width: int = width
		self.orientation: Orientation = orientation

	def update(self, absolute_topleft_point: Point, absolute_bottomright_point: Point, width: int, height: int, orientation: str) -> None:
		self.absolute_topleft_point = absolute_topleft_point
		self.absolute_bottomright_point = absolute_bottomright_point
		self.height = height
		self.width = width
		self.orientation = orientation

	def toString(self) -> str:
		return "absolute topleft : ({},{}), absolute_bottomright : ({},{}), widthxheight : {}x{}, orientation : {}".format(
			self.absolute_topleft_point.x, self.absolute_topleft_point.y, self.absolute_bottomright_point.x,
			self.absolute_bottomright_point.y, self.width, self.height, self.orientation)
