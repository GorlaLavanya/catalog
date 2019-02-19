from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fdatabase_setup import Institute, Base, Course, User
engine = create_engine('sqlite:///courses.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
session.query(User).delete()
user1 = User(name="Lavanyareddy", email="kameshreddy341@gmail.com")
session.add(user1)
session.commit()
institute1 = Institute(user_id=1, id="6253", name="srinivasa")
session.add(institute1)
session.commit()
course1 = Course(user_id=1, id="10", name="machinelearning",
                 department="computer science and engineering",
                 duration="12", instructor="praveenkumar",
                 institute=institute1)
session.add(course1)
session.commit()
course2 = Course(user_id=1, id="11", name="datamining",
                 department="computer science and engineering",
                 duration="8", instructor="suman",
                 institute=institute1)
session.add(course2)
session.commit()
course3 = Course(user_id=1, id="12", name="python",
                 department="computer science and engineering",
                 duration="12", instructor="badulla",
                 institute=institute1)
session.add(course3)
session.commit()
course4 = Course(user_id=1, id="13", name="operating system",
                 department="computer science and engineering",
                 duration="12", instructor="galvin",
                 institute=institute1)
session.add(course4)
session.commit()
institute2 = Institute(user_id=1, id="6543", name="talentedge")
session.add(institute2)
session.commit()
course1 = Course(user_id=1, id "21", name="logic design",
                 department="electronics and communication engineering",
                 duration="12", instructor="raviteja",
                 institute=institute2)
session.add(course1)
session.commit()
course2 = Course(user_id=1, id="23", name="english",
                 department="Humanities and social science",
                 duration="10", instructor="vinatha",
                 institute=institute2)
session.add(course2)
session.commit()
course3 = Course(user_id=1, id="25", name="aptitude",
                 department="Mathematics", duration="12",
                 instructor="hari", institute=institute2)
session.add(course3)
session.commit()
print("items are added")
