import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean

basedir = os.path.abspath(os.path.dirname(__file__))
print(basedir)

db = SQLAlchemy()


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
CORS(app)
with app.app_context():
    db.create_all()

def add_sample_data():
    with app.app_context():
        # Create the database tables if they don't exist
        db.create_all()

        # Sample test cases
        test_cases = [
            TestCase(input='input1', output='output1', is_correct=True, reason='Correct output'),
            TestCase(input='input2', output='output2', is_correct=False, reason='Incorrect output'),
            # Add more test cases as needed
        ]

        # Add test cases to the session
        db.session.add_all(test_cases)
        # Commit the session to the database
        db.session.commit()

        print("Sample data added to the database.")

class TestCase(db.Model):
    __tablename__ = 'test_cases'

    id = Column(Integer, primary_key=True)
    input = Column(String, nullable=False)
    output = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    reason = Column(String)

    def __repr__(self):
        return f'<TestCase {self.id}, {self.input}, {self.output}, {self.is_correct}, {self.reason}>'


@app.route("/")
def index():
    return "Hello, World!"


@app.route("/input-output", methods=["GET"])
def get_test_cases():
    test_cases = TestCase.query.all()
    result = [
        {
            'id': test_case.id,
            'input': test_case.input,
            'output': test_case.output,
            'is_correct': test_case.is_correct,
            'reason': test_case.reason
        }
        for test_case in test_cases
    ]
    return jsonify(result)

if __name__ == "__main__":
    add_sample_data()
    app.run(debug=True, port=9000)
