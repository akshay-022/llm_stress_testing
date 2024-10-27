import os
from flask import Flask, jsonify, request
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

        if not EvaluateOrNot.query.first():
            evaluate_or_not = EvaluateOrNot(is_evaluate=False, evaluation_id=1)
            db.session.add(evaluate_or_not)
        if not TestCase.query.first():
            test_cases = [
                TestCase(input='input1', output='output1', is_correct=True, reason='Correct output', system_name='customer_support', prompts='{"prompt": "prompt1"}', process_id=1),
                TestCase(input='input2', output='output2', is_correct=False, reason='Incorrect output', system_name='customer_support', prompts='{"prompt": "prompt2"}', process_id=2),
                # Add more test cases as needed
            ]
            db.session.add_all(test_cases)
        # Commit the session to the database
        db.session.commit()

        print("Sample data added to the database.")

class TestCase(db.Model):
    __tablename__ = 'test_cases'

    id = Column(Integer, primary_key=True)
    process_id = Column(Integer)
    input = Column(String)
    output = Column(String)
    prompts = Column(String)    #Will be a dumped json dictionary with the prompts used
    is_correct = Column(Boolean)
    reason = Column(String)
    system_name = Column(String)
    is_approved = Column(Boolean)
    ground_truth = Column(String)

    def __repr__(self):
        return f'<TestCase {self.id}, {self.input}, {self.output}, {self.is_correct}, {self.reason}>'

# This must have just one entry, where it says whether to evaluate or not
class EvaluateOrNot(db.Model):
    __tablename__ = 'evaluate_or_not'
    id = Column(Integer, primary_key=True)
    is_evaluate = Column(Boolean)
    evaluation_id = Column(Integer)

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

@app.route("/testcase/<int:id>", methods=["DELETE"])
def delete_test_case(id):
    test_case = TestCase.query.get_or_404(id)
    db.session.delete(test_case)
    db.session.commit()
    return jsonify({"message": f"Test case {id} deleted successfully"}), 200

@app.route("/testcase", methods=["POST"])
def update_test_case():
    data = request.json
    print(data)
    test_case = TestCase.query.get_or_404(data['id'])
    
    test_case.input = data['input']
    test_case.output = data['output']
    test_case.is_correct = data['is_correct']
    test_case.reason = data['reason']
    
    db.session.commit()
    
    return jsonify({
        'id': test_case.id,
        'input': test_case.input,
        'output': test_case.output,
        'is_correct': test_case.is_correct,
        'reason': test_case.reason
    }), 200



if __name__ == "__main__":
    add_sample_data()
    app.run(debug=True, port=9000)
