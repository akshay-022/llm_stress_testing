import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

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

        # Check if sample data already exists
        if EvaluateOrNot.query.first() is None:
            evaluate_or_not = EvaluateOrNot(is_evaluate=False, evaluation_id=1)
            db.session.add(evaluate_or_not)

        # Check if sample prompt already exists
        existing_prompt = Prompt.query.filter_by(agent_name="customer_support").first()
        if existing_prompt is None:
            prompt = """
            You are a helpful customer support assistant with tweet length response that responds based on the customer support documentation: {{EXAMPLE_CUSTOMER_SUPPORT_DOC}}. 
            Your response should be empathetic and assuring that the team is taking the matter very seriously. 
            Respond politely to the user's message: {{user_message}}."""
            
            sample_prompt = Prompt(
                prompt=prompt,
                agent_name="customer_support",
                model_name="GPT-3.5",
                process_id=1
            )
            db.session.add(sample_prompt)
            db.session.flush()  # This will assign an ID to sample_prompt

            # Check if sample test case already exists
            existing_test_case = TestCase.query.filter_by(input="How can I reset my password?").first()
            if existing_test_case is None:
                sample_test_case = TestCase(
                    input="How can I reset my password?",
                    output="To reset your password, please follow these steps:\n1. Go to our website's login page.\n2. Click on the 'Forgot Password' link.\n3. Enter your email address.\n4. Check your email for a password reset link.\n5. Click the link and follow the instructions to set a new password.",
                    is_correct=True,
                    reason="Provides clear step-by-step instructions for password reset",
                    agent_name="customer_support",
                    process_id=1,
                    prompt_id=sample_prompt.id
                )
                db.session.add(sample_test_case)

        # Commit the session to the database
        db.session.commit()

        print("Sample data added to the database (if it didn't exist already).")

class TestCase(db.Model):
    __tablename__ = 'test_cases'

    id = Column(Integer, primary_key=True)
    process_id = Column(Integer)
    input = Column(String)
    output = Column(String)
    is_correct = Column(Boolean)
    reason = Column(String)
    agent_name = Column(String)
    is_approved = Column(Boolean)
    ground_truth = Column(String)
    prompt_id = Column(Integer, ForeignKey('prompts.id'))  # New field for the relationship
    prompt = relationship("Prompt", back_populates="test_cases")  # Relationship to Prompt

    def __repr__(self):
        return f'<TestCase {self.id}, {self.input}, {self.output}, {self.is_correct}, {self.reason}>'

# This must have just one entry, where it says whether to evaluate or not
class EvaluateOrNot(db.Model):
    __tablename__ = 'evaluate_or_not'
    id = Column(Integer, primary_key=True)
    is_evaluate = Column(Boolean)
    evaluation_id = Column(Integer)

class Prompt(db.Model):
    __tablename__ = 'prompts'
    id = Column(Integer, primary_key=True)
    prompt = Column(String)
    agent_name = Column(String)
    model_name = Column(String)
    process_id = Column(Integer)
    test_cases = relationship("TestCase", back_populates="prompt")  # Relationship to TestCase

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
            'reason': test_case.reason,
            'ground_truth': test_case.ground_truth
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
    test_case.ground_truth = data['ground_truth']
    
    db.session.commit()
    
    return jsonify({
        'id': test_case.id,
        'input': test_case.input,
        'output': test_case.output,
        'is_correct': test_case.is_correct,
        'reason': test_case.reason,
        'ground_truth': test_case.ground_truth
    }), 200

@app.route("/prompts", methods=["GET"])
def get_prompts():
    prompts = Prompt.query.all()
    result = [
        {
            'id': prompt.id,
            'prompt': prompt.prompt,
            'prompt_name': prompt.agent_name,
            'model_name': prompt.model_name,
            'process_id': prompt.process_id
        }
        for prompt in prompts
    ]
    return jsonify(result)

@app.route("/prompts/<int:prompt_id>/testcases", methods=["GET"])
def get_testcases_by_prompt(prompt_id):
    test_cases = TestCase.query.filter_by(prompt_id=prompt_id).all()
    result = [
        {
            'id': test_case.id,
            'input': test_case.input,
            'output': test_case.output,
            'is_correct': test_case.is_correct,
            'reason': test_case.reason,
            'prompt_id': test_case.prompt_id,
            'ground_truth': test_case.ground_truth
        }
        for test_case in test_cases
    ]
    
    # Calculate the percentage of correct test cases
    total_cases = len(test_cases)
    correct_cases = sum(1 for test_case in test_cases if test_case.is_correct)
    percent_correct = (correct_cases / total_cases) * 100 if total_cases > 0 else 0
    
    # Add the percentage to the response
    response = {
        'test_cases': result,
        'percent_correct': round(percent_correct, 2)
    }
    
    return jsonify(response)

@app.route("/prompts/<int:prompt_id>", methods=["DELETE"])
def delete_prompt(prompt_id):
    prompt = Prompt.query.get_or_404(prompt_id)
    
    # Delete associated test cases
    TestCase.query.filter_by(prompt_id=prompt_id).delete()
    
    # Delete the prompt
    db.session.delete(prompt)
    db.session.commit()
    
    return jsonify({"message": f"Prompt with id {prompt_id} and its associated test cases have been deleted"}), 200




if __name__ == "__main__":
    add_sample_data()
    app.run(debug=True, port=9000)
