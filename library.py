from backend.app import db, TestCase, EvaluateOrNot, Prompt


# Create a sample element in EvaluateOrNot that has is_evaluate = False
def create_sample_evaluate_or_not():
    sample_entry = EvaluateOrNot(is_evaluate=False)
    db.session.add(sample_entry)
    db.session.commit()

class LLMLogger:
    def __init__(self, app):
        self.process_id = 0
        self.app = app
        self.is_evaluate, self.evaluation_id = self.get_evaluate()
        self.do_db_actions = True

    def get_evaluate(self):
        with self.app.app_context():
            evaluate = EvaluateOrNot.query.first()
            return evaluate.is_evaluate, evaluate.id

    def start_process_here(self):
        with self.app.app_context():
            last_entry = TestCase.query.order_by(TestCase.process_id.desc()).first()
            if last_entry:
                self.process_id = last_entry.process_id + 1
            else:
                self.process_id = 1

    def query_llm(self, prompt: str, input: str = None, output: str = None) -> tuple:
        from langchain.llms import OpenAI
        from langchain.prompts import PromptTemplate
        from langchain.chains import LLMChain
        from langchain.output_parsers import PydanticOutputParser
        from pydantic import BaseModel, Field

        class QueryResponse(BaseModel):
            is_correct: bool = Field(description="Whether the answer is yes or no to the question")
            reason: str = Field(description="The reason for the answer, especially if it's no")

        llm = OpenAI(temperature=0)
        output_parser = PydanticOutputParser(pydantic_object=QueryResponse)

        template = """
        Question: {prompt}
        
        Input: {input}
        Output: {output}
        
        Please answer the question and provide a reason if the answer is no.
        
        {format_instructions}
        """

        prompt_template = PromptTemplate(
            input_variables=["prompt", "input", "output"],
            template=template,
            partial_variables={"format_instructions": output_parser.get_format_instructions()}
        )

        chain = LLMChain(llm=llm, prompt=prompt_template)

        result = chain.run(prompt=prompt, input=input, output=output)
        parsed_result = output_parser.parse(result)

        return parsed_result.is_correct, parsed_result.reason if not parsed_result.is_correct else None

    def save_input(self, inputs: str, agent_name: str, prompt: str):
        
        if not self.do_db_actions:
            return None
        with self.app.app_context():
            prompt_id = self.save_prompt_to_table(prompt = prompt, agent_name = agent_name, model_name = "gemini-1.5-flash")
            new_entry = TestCase(process_id=self.process_id, input=inputs, agent_name=agent_name, prompt_id = prompt_id)
            db.session.add(new_entry)
            db.session.commit()
            return None

    def save_output(self, content: str, is_correct: bool, agent_name: str, reason_failure: str = None):
        if not self.do_db_actions:
            return None
        with self.app.app_context():
            entry = TestCase.query.filter_by(process_id=self.process_id, agent_name=agent_name).first()
            
            if entry:
                entry.output = content
                entry.is_correct = is_correct
                
                if not is_correct:
                    print("Input:")
                    print(entry.input)
                    print("\nOutput:")
                    print(content)
                    reason = reason_failure if reason_failure else "Did not provide a reason"#input("\nWhy is this output incorrect? ")
                    entry.reason = reason
                    print(f"Execution paused. Reason for incorrectness: {reason}")
                db.session.commit()
            else:
                print(f"No input found for run number {self.process_id} and agent_name {agent_name}")

    # This auto-assigns if a query is correct or not based on the LLM's judgement.
    def save_output_using_llm(self, content: str, is_correct_query: str, agent_name: str):
        if not self.do_db_actions:
            return None
        with self.app.app_context():
            entry = TestCase.query.filter_by(process_id=self.process_id, agent_name=agent_name).first()
            
            if entry:
                entry.output = content
                
                # Use the is_correct_query to determine correctness
                # This assumes you have a method to query an LLM
                is_correct = self.query_llm(is_correct_query, entry.input, content)
                entry.is_correct = is_correct
                
                if not is_correct:
                    print("Input:")
                    print(entry.input)
                    print("\nOutput:")
                    print(content)
                    reason = self.query_llm(f"Why is this output incorrect?\nInput: {entry.input}\nOutput: {content}")
                    entry.reason = reason
                    print(f"Execution paused. Reason for incorrectness: {reason}")
                
                db.session.commit()
            else:
                print(f"No input found for run number {self.process_id} and agent_name {agent_name}")

    def save_prompt_to_table(self, prompt, agent_name, model_name = None):
        if not self.do_db_actions:
            return None
        # if exact same agent name and prompt already exists, return the id
        with self.app.app_context():
            existing_prompt = Prompt.query.filter_by(agent_name=agent_name, prompt = prompt.strip()).first()
            if existing_prompt:
                return existing_prompt.id

        # If agent_name exists in db already, find its model name
        with self.app.app_context():
            existing_entry = Prompt.query.filter_by(agent_name=agent_name).first()
            if existing_entry:
                model_name = existing_entry.model_name
            existing_entry_complete = Prompt.query.filter_by(agent_name=agent_name, model_name=model_name, process_id=self.process_id, prompt = prompt.strip()).first()
            if not existing_entry_complete:
                new_entry = Prompt(prompt=prompt, agent_name=agent_name, model_name=model_name, process_id=self.process_id)
                db.session.add(new_entry)
                db.session.commit()
            return new_entry.id

    # This is for when you want to generate new outputs for the current prompt in code and all inputs to the same agent_name previously.
    def generate_new_prompt_outputs(self, running_function, prompt_id: int):
        if not self.do_db_actions:
            return None
        from langchain.chains.llm import LLMChain
        from langchain_openai.chat_models import ChatOpenAI
        from langchain.prompts import PromptTemplate
        from langchain.chains import LLMChain
        import json

        with self.app.app_context():
            entries = TestCase.query.order_by(TestCase.process_id, TestCase.id).all()
            # Get distinct inputs
            distinct_inputs = set(entry.input for entry in entries if entry.input)
            
            for distinct_input in distinct_inputs:
                # Find the first entry with this input
                entry = next(e for e in entries if e.input == distinct_input)
                
                # Simulate input
                print(f"Processing distinct input for system {entry.agent_name}")
                # Here you would typically call the function that processes this input
                self.do_db_actions = False
                new_output = running_function(inputs=distinct_input)
                self.do_db_actions = True
                new_entry = TestCase(process_id=self.process_id, input=distinct_input, output=new_output, agent_name=entry.agent_name, prompt_id=prompt_id, ground_truth=entry.ground_truth if entry.ground_truth else None)
                db.session.add(new_entry)
            db.session.commit()
            db.session.close()

    # Applies the evaluation metric to the latest prompt outputs.
    def evaluate_latest_prompt_outputs(self, how_to_evaluate: str, who_to_evaluate: str, prompt_id: int):
        if not self.do_db_actions:
            return None
        from langchain.chains.llm import LLMChain
        from langchain_openai.chat_models import ChatOpenAI
        from langchain.prompts import PromptTemplate
        from langchain.chains import LLMChain

        with self.app.app_context():
            entries = TestCase.query.order_by(TestCase.process_id, TestCase.id).all()
            # Filter entries based on who_to_evaluate
            entries = [entry for entry in entries if entry.agent_name == who_to_evaluate and entry.prompt_id == prompt_id]
            if not how_to_evaluate:
                llm = ChatOpenAI(temperature=0)
                prompt_template = PromptTemplate(
                    input_variables=["original_output", "new_output"],
                    template="Compare these two outputs and determine if they are semantically equivalent:\n\nOriginal: {original_output}\n\nNew: {new_output}\n\nAre they equivalent? Answer with 'Yes' or 'No' and provide a brief explanation."
                )
                chain = LLMChain(llm=llm, prompt=prompt_template)
            else : 
                llm = ChatOpenAI(temperature=0)
                prompt_template = PromptTemplate(
                    input_variables=["original_output", "new_output"],
                    template= how_to_evaluate + "\n\nHere are the original and new outputs:\n\nOriginal: {original_output}\n\nNew: {new_output} Answer the question with 'Yes' or 'No' and provide a brief explanation."
                )
                chain = LLMChain(llm=llm, prompt=prompt_template)
            try:
                for entry in entries:
                    # There should either be ground truth or a how_to_evaluate prompt
                    if entry.input and (how_to_evaluate or entry.ground_truth):
                        new_output = entry.output
                        # Compare output
                        result = chain.run(original_output=entry.ground_truth, new_output=new_output)
                        is_equivalent = result.strip().lower().startswith('yes')
                        
                        print(f"Process ID: {entry.process_id}, System: {entry.agent_name}")
                        print(f"Original output: {entry.output}")
                        print(f"New output: {new_output}")
                        print(f"Equivalent: {is_equivalent}")
                        print(f"LLM explanation: {result}")
                        print("---")

                        # Update the database entry
                        entry.is_correct = is_equivalent
                        if not is_equivalent:
                            entry.reason = result
                        entry.how_to_evaluate = how_to_evaluate
                        if not how_to_evaluate:
                            entry.how_to_evaluate = "Compare the ground truth, new outputs for semantic equivalence."
                        db.session.commit()

            finally:
                db.session.close()
    
    def evaluate_complete_unit_test(self, running_function, prompt, who_to_evaluate: str, how_to_evaluate: str = None):
        if not self.do_db_actions:
            return None
        from prompt_config import Config
        Config[who_to_evaluate] = prompt
        prompt_id = self.save_prompt_to_table(prompt, who_to_evaluate, "gemini-1.5-flash")
        self.generate_new_prompt_outputs(running_function = running_function, prompt_id = prompt_id)
        self.evaluate_latest_prompt_outputs(how_to_evaluate = how_to_evaluate, who_to_evaluate = who_to_evaluate, prompt_id = prompt_id)
        return self.get_reliability_score(who_to_evaluate, prompt_id)

    def get_reliability_score(self, agent_name: str, prompt_id: int):
        with self.app.app_context():
            entries = TestCase.query.filter_by(agent_name=agent_name, prompt_id=prompt_id).all()
            correct_entries = [entry for entry in entries if entry.is_correct and 'equivalence' in entry.how_to_evaluate.lower()]
            return 100 * len(correct_entries) / len(entries)

    def get_best_prompts(self, agent_name: str):
        from langchain.llms import OpenAI
        from langchain.prompts import PromptTemplate
        from langchain.chains import LLMChain
        import json

        with self.app.app_context():
            entries = TestCase.query.filter_by(agent_name=agent_name).all()

            correct_entries = []
            incorrect_entries = []

            for entry in entries:
                if entry.is_correct:
                    correct_entries.append({
                        'input': entry.input,
                        'output': entry.output,
                        'prompts': json.loads(entry.prompts)
                    })
                else:
                    incorrect_entries.append({
                        'input': entry.input,
                        'output': entry.output,
                        'prompts': json.loads(entry.prompts)
                    })

            llm = OpenAI(temperature=0.7)
            prompt_template = PromptTemplate(
                input_variables=["correct_entries", "incorrect_entries"],
                template="Given the following correct and incorrect input-output pairs with their associated prompts, generate an optimal prompt for each variable:\n\nCorrect entries: {correct_entries}\n\nIncorrect entries: {incorrect_entries}\n\nGenerate optimal prompts:"
            )
            chain = LLMChain(llm=llm, prompt=prompt_template)

            result = chain.run(correct_entries=str(correct_entries), incorrect_entries=str(incorrect_entries))
            
            # And then maybe after this iteratively generate new prompts, see which ones it fails at the most, and especially focus on getting those right.
            return result
    
    def fill_template(self, template: str, **kwargs) -> str:
        # Function to replace placeholders with actual values
        def fill_template(template, **kwargs):
            return template.format(**{k: '{' + k + '}' for k in kwargs.keys()}).format(**kwargs)
        # Fill the template with actual values
        prompt_to_return = fill_template(template, **kwargs)
        return prompt_to_return


    def generate_remaining_input_outputs(self, agent_name: str, number_of_items_to_generate: int = 5, prompt_to_aid_generation: str = None):
        from openai import OpenAI
        import json
        import os
        from dotenv import load_dotenv

        # Load environment variables and set OpenAI API key
        load_dotenv()
        api_key=os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key)

        with self.app.app_context():
            correct_entries = TestCase.query.filter_by(agent_name=agent_name, is_correct=True).all()

            if not correct_entries:
                return []

            correct_pairs = [{"input": entry.input, "output": entry.output} for entry in correct_entries]

            prompt = f"""
            Given the following correct input-output pairs:
            {json.dumps(correct_pairs, indent=2)}

            Generate {number_of_items_to_generate} new input-output pairs that are similar in style and complexity, but different in content. 
            Ensure that the new pairs maintain the same pattern or logic as the given examples.
            Format your response as a Python list of dictionaries, each containing 'input' and 'output' keys.
            """

            if prompt_to_aid_generation:
                prompt = "Keep the below guidelines in mind when generating the new input-output pairs:\n" + prompt_to_aid_generation + "\n\n" + prompt

            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that generates input-output pairs."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.0
                )
                
                result = response.choices[0].message.content
            
                #Trim result to only the part within '''json'''
                #result = result.split('```json')[1].split('```')[0]

                new_pairs = json.loads(result)

                # Append all the new pairs to the database
                for pair in new_pairs:
                    # Get the highest prior prompt_id for the agent_name
                    highest_prompt = db.session.query(TestCase).filter_by(agent_name=agent_name).order_by(TestCase.prompt_id.desc()).first()
                    prompt_id = highest_prompt.prompt_id if highest_prompt else None
                    # No prompts key here means that these are llm generated samples, not based on a certain prompt.
                    new_entry = TestCase(process_id=self.process_id, input=pair['input'], output=pair['output'], agent_name=agent_name, prompt_id = prompt_id)
                    db.session.add(new_entry)
                db.session.commit()

                return new_pairs
            except json.JSONDecodeError:
                print("Error: Unable to parse the generated output as JSON.")
                return []

# Usage example
def main():
    logger = LLMLogger()
    logger.start_process_here()

    # Simulating multiple runs
    for run in range(1, 4):
        agent_name = f"system_{run}"
        input_text = f"Sample input for run {run}"
        output_text = f"Output for run {run}"
        prompts = {"system": "You are a helpful assistant", "user": "Process this input"}
        
        # Simulating query_llm
        result = logger.query_llm(prompts["user"], input=input_text)
        
        # Simulating correct and incorrect outputs
        is_correct = run % 2 == 0
        reason = "Correct output" if is_correct else "Incorrect output"
        
        # Save the test data
        logger.save_test_data(input_text, output_text, prompts, is_correct, reason, agent_name)

    # Generate optimal prompts
    optimal_prompts = logger.generate_optimal_prompts(agent_name)
    print("Optimal prompts:", optimal_prompts)

    # Generate remaining input-outputs
    new_pairs = logger.generate_remaining_input_outputs(agent_name)
    print("New input-output pairs:", new_pairs)

    # Test the evaluate_or_not functionality
    create_sample_evaluate_or_not()
    is_evaluate, evaluation_id = logger.get_evaluate()
    print(f"Is evaluate: {is_evaluate}, Evaluation ID: {evaluation_id}")

if __name__ == "__main__":
    main()
