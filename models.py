from inventoryApp import db  # type: ignore
from typing import Optional
from datetime import date

class Grocery(db.Model):  # type: ignore
	__tablename__ = 'grocery_items'

	id = db.Column(db.Integer, primary_key=True)  # type: ignore
	description = db.Column(db.String(60), nullable=False)  # type: ignore
	last_sold = db.Column(db.Date)  # type: ignore
	shelf_life = db.Column(db.String(5), nullable=False)  # type: ignore
	department = db.Column(db.String(40))  # type: ignore
	price = db.Column(db.String(20), nullable=False)  # type: ignore
	unit = db.Column(db.String(10), nullable=False)  # type: ignore
	x_for = db.Column(db.Integer, nullable=False)  # type: ignore
	cost = db.Column(db.String(20), nullable=False)  # type: ignore

	def __init__(self, id: int, description: str, last_sold: Optional[date], shelf_life: str,
				 department: Optional[str], price: str, unit: str, x_for: int, cost: str):
		self.id = int(id)
		self.description = description
		self.last_sold = last_sold
		self.shelf_life = shelf_life
		self.department = department
		self.price = price
		self.unit = unit
		self.x_for = int(x_for)
		self.cost = cost

	def __iter__(self):
		"""Make the model iterable for JSON serialization"""
		yield 'id', self.id
		yield 'description', self.description
		yield 'last_sold', str(self.last_sold) if self.last_sold else None
		yield 'shelf_life', self.shelf_life
		yield 'department', self.department
		yield 'price', self.price
		yield 'unit', self.unit
		yield 'x_for', self.x_for
		yield 'cost', self.cost