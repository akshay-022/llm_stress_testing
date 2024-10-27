import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import os
from dotenv import load_dotenv

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


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
gemini_pro = genai.GenerativeModel("gemini-1.5-pro-latest")

def construct_prompt_for_improvement(reasons: list[str], prompt: str):
    return f"""
        Your job is to improve the following prompt: {prompt}
        The following test cases failed with a reason: {reasons}
        Try your best to improve the prompt with concise and clear instructions so that the test cases pass the failed reasons.
        """

def execute_prompt_improvement(prompt: str, reasons: list[str]):
    improved_prompt = gemini_pro.generate_content(construct_prompt_for_improvement(reasons, prompt), safety_settings=SAFETY_SETTINGS)
    return improved_prompt.text
