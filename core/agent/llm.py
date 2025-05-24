from langchain_openai import ChatOpenAI


text_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0, max_tokens=2000)
text_to_img_llm = ChatOpenAI(model="gpt-image-1", temperature=0.0, max_tokens=2000)
