from langchain_openai import ChatOpenAI


def generate_prompt_name(model: ChatOpenAI, prompt: str):
    """Generate marketing prompt that needs to be feed to generating banner image"""
    return model.invoke(prompt)
