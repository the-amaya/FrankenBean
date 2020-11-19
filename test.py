import time
import random
import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String

#database setup

engine = db.create_engine('sqlite:///beanapi.db')
Session = sessionmaker(bind=engine)
session = Session()


class coilModel(declarative_base()):
	__tablename__ = 'coilModel'
	id = Column(Integer, primary_key=True)
	name = Column(String(100), nullable=False)
	state = Column(Integer, nullable=False)
	def __repr__(self):
		return f"coil(id = {id}, name = {name}, state = {state})"


def dbupdate(name, state):
	dbi = session.query(coilModel).filter_by(name=name).first()
	dbi.state = state
	try:
		session.commit()
	except:
		print('broken db connection')


states = [
	['pump', '0'],
	['w_solenoid', '0'],
	['heat', '0'],
	['vent', '0'],
	['air_pump', '0'],
	['fill_low', '0'],
	['fill_med', '0'],
	['fill_high', '0'],
	['overfill', '0'],
	['flow', '0'],
	['temperature', '0'],
	['active', '0']
]

c = 0
while c < 1000:
	dbupdate('temperature', c)
	time.sleep(1)
	c += 1

dbupdate('active', 0)