import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import os
from dotenv import load_dotenv

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from library import LLMLogger
from backend.app import app


from prompt_config import Config
logger = LLMLogger(app)
all_prompt = {

    "customer_support": "You are a helpful customer support assistant with tweet length response that responds based on the customer support documentation: {EXAMPLE_CUSTOMER_SUPPORT_DOC}. Your response should be empathetic and assuring that the team is taking the matter very seriously. Respond politely to the user's message: {{user_message}}."
}

EXAMPLE_CUSTOMER_SUPPORT_DOC = """
HOW TO CONTACT US
Once registered as a support contact, you can contact MarkLogic Technical Support via:
• Web Support portal at https://help.marklogic.com;
• Email
• For Data Hub Service issues, send email to cloud-support@marklogic.com;
• For all other issues, send email to support@marklogic.com.
• Phone – 1-855-882-8323
To enhance the process of reporting, tracking and resolving issues, we recommend that all support
requests be submitted via the web portal or via email.
Support requests for urgent issues (as defined in Understanding Case Priority and Response Time
Targets) can be submitted at any time via our support portal or via email to urgent@marklogic.com.
"""

SAFETY_SETTINGS =  {
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

dumbest_gemini_model = genai.GenerativeModel("gemini-1.5-flash-8b")
gemini_flash = genai.GenerativeModel("gemini-1.5-flash")



def construct_customer_support_prompt(user_message: str) -> str:
    # Save prompt to logger here
    agent_name = "customer_support"
    prompt_to_return = logger.fill_template(Config[agent_name],
                                            user_message=user_message,
                                            EXAMPLE_CUSTOMER_SUPPORT_DOC=EXAMPLE_CUSTOMER_SUPPORT_DOC)
    return prompt_to_return


def answer_user_question(inputs: str) -> str:
    prompt = construct_customer_support_prompt(inputs)
    logger.save_input(inputs = inputs, agent_name = "customer_support", prompt = Config["customer_support"])
    response = dumbest_gemini_model.generate_content(prompt, safety_settings=SAFETY_SETTINGS)
    logger.save_output(response.text, True, "customer_support")
    return response.text

if __name__ == "__main__":
    logger.start_process_here()

    print(answer_user_question("How can I get in contact with MarkLogic?")) # EVAL: Make sure it is less than 50 characters
    #print(answer_user_question("Who do I contact if I have some problems with my account?"))
    logger.generate_remaining_input_outputs(agent_name="customer_support", number_of_items_to_generate=5, prompt_to_aid_generation="Ensure you only stay within the bounds of the customer support documentation.")
    
    
    prompt = """
        You are a very rude customer support assistant with tweet length response that responds based on the customer support documentation: {{EXAMPLE_CUSTOMER_SUPPORT_DOC}}. 
        Your response should be empathetic and assuring that the team is taking the matter very seriously. 
        Respond politely to the user's message: {{user_message}}."""
    reliability_score = logger.evaluate_complete_unit_test(answer_user_question, prompt = prompt, who_to_evaluate="customer_support", how_to_evaluate="Is the output polite?")
    print(reliability_score)