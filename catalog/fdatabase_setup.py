import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(300))


class Institute(Base):
    __tablename__ = 'institute'
    id = Column(Integer, primary_key=True)
    name = Column(String(300), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            }


class Course(Base):
    __tablename__ = 'course'
    id = Column(Integer, primary_key=True)
    name = Column(String(90), nullable=False)
    instructor = Column(String(20))
    department = Column(String(100))
    duration = Column(Integer)
    institute_id = Column(Integer, ForeignKey('institute.id'))
    institute = relationship(Institute)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return{
            'name': self.name,
            'instructor': self.instructor,
            'department': self.department,
            'duration': self.duration,
            'id': self.id,
            }


engine = create_engine('sqlite:///courses.db')
Base.metadata.create_all(engine)
