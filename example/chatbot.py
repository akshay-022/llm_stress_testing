import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

import os

from dotenv import load_dotenv

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
    return f"""
You are a helpful customer support assistant with tweet length response that responds based on the customer support documentation: {EXAMPLE_CUSTOMER_SUPPORT_DOC}. 
Your response should be empathetic and assuring that the team is taking the matter very seriously. 
Respond politely to the user's message: {user_message}."""


def answer_user_question(user_message: str) -> str:
    prompt = construct_customer_support_prompt(user_message)
    response = dumbest_gemini_model.generate_content(prompt, safety_settings=SAFETY_SETTINGS)
    return response.text

if __name__ == "__main__":
    print(answer_user_question("How can I get in contact with MarkLogic?")) # EVAL: Make sure it is less than 50 characters
