from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean

db = SQLAlchemy()

class TestCase(db.Model):
    __tablename__ = 'test_cases'

    id = Column(Integer, primary_key=True)
    input = Column(String, nullable=False)
    output = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    reason = Column(String)

    def __repr__(self):
        return f'<TestCase {self.id}>'
