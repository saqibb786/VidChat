from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
import os 

def get_llm():
    return ChatMistralAI(model="mistral-small-latest", mistral_api_key=os.getenv("MISTRAL_API_KEY"), temperature=0.2)

def build_chain(system_prompt: str):
    llm = get_llm()
    return (
        RunnablePassthrough() 
        | RunnableLambda(lambda x: {"text": x}) 
        | ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{text}"),
        ]) 
        | llm 
        | StrOutputParser()
    )

def extract_action_items(transcript: str) -> str:
    chain = build_chain(
        "You are an expert content analyst. Analyze the transcript and extract all actionable items, "
        "practical takeaways, or next steps. If this is an informal talk or video, extract the key practical "
        "advice or recommended actions mentioned. Format as a clean numbered list."
    )
    return chain.invoke(transcript)

def extract_key_decisions(transcript: str) -> str:
    chain = build_chain(
        "You are an expert content analyst. Analyze the transcript and extract all key decisions, core conclusions, "
        "or central takeaways established in the video. Format as a clean numbered list."
    )
    return chain.invoke(transcript)

def extract_questions(transcript: str) -> str:
    chain = build_chain(
        "Analyze the transcript and extract any open questions, unresolved topics, or key themes requiring "
        "further reflection or discussion. Format as a clean numbered list."
    )
    return chain.invoke(transcript)