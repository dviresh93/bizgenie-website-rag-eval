from string import Template
from typing import Optional

class PromptManager:
    """
    Centralized manager for system and user prompts.
    Ensures consistent persona and formatting across the application.
    """

    # 1. SYSTEM PROMPT (The Persona)
    SYSTEM_PROMPT_TEMPLATE = Template("""You are an expert, professional, and friendly customer support representative for the business found at ${target_url}.
Your primary goal is to provide accurate and helpful answers to user questions, speaking *as if you are a representative of this organization*.

Instructions:
1. Refer to the business as 'we' or 'our company' where appropriate.
2. Answer questions primarily based on the retrieved information about *this specific business*.
3. Maintain a polite, professional, and conversational tone. Avoid using bullet points or numbered lists unless explicitly requested by the user or if the information is inherently list-like (e.g., a pricing plan).
4. If asked about general topics that could apply to many companies, assume the user is asking in the context of *our company* (the one at ${target_url}).
5. If the retrieved information does not contain the answer, state that 'we do not have that information available' or 'I cannot provide details on that at the moment' rather than making up an answer.
""")

    # 2. USER PROMPT (The Task)
    # Injects the context (search results) and the specific question
    USER_PROMPT_TEMPLATE = Template("""Based on the following retrieved information, please answer the user's question.

RETRIEVED INFORMATION:
${context}

USER QUESTION:
${question}

Please provide a clear, accurate answer following the persona defined in the system instructions. Cite specific sources when possible.""")

    @staticmethod
    def get_system_prompt(target_url: str) -> str:
        """
        Generate the system prompt defining the AI's persona.
        """
        if not target_url:
            return "You are a helpful AI assistant."
            
        return PromptManager.SYSTEM_PROMPT_TEMPLATE.substitute(target_url=target_url)

    @staticmethod
    def get_user_prompt(question: str, context: str) -> str:
        """
        Generate the user prompt combining context and question.
        """
        return PromptManager.USER_PROMPT_TEMPLATE.substitute(
            question=question,
            context=context
        )
