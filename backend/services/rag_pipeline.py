from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from backend.config import settings
from backend.services.embeddings import get_vector_store
import time

store = {}

def get_session_history(session_id: str) -> ChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# The User requested MASTER PROMPT:
master_prompt = """You are an intelligent AI assistant powered by Retrieval-Augmented Generation (RAG).

Your task is to answer user questions ONLY based on the provided context.

STRICT RULES:
1. Do not use your own knowledge.
2. If the answer is not in the context, say:
   "I could not find relevant information in the provided documents."
3. Be concise, clear, and factual.
4. Cite relevant parts of the context if possible.
5. Do not hallucinate or assume missing details.

CONTEXT:
{context}
"""

def get_answer(query: str, session_id: str):
    vs = get_vector_store()
    if not vs:
        return "Vector store not initialized. Please configure API keys.", []

    if not settings.GEMINI_API_KEY:
        return "Gemini API key is missing. Please configure your .env file.", []
        
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",  # 1500 RPD free tier vs 20 RPD for gemini-3-flash
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.0
    )

    # Use Maximum Marginal Relevance (MMR) to guarantee diversity instead of pure similarity
    # This prevents one resume (e.g. Java) from monopolizing the top chunks and hiding others.
    retriever = vs.as_retriever(
        search_type="mmr", 
        search_kwargs={"k": 8, "fetch_k": 30}
    )

    # Contextualize Question
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, formulate a standalone question "
        "which can be understood without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    # QA Chain
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", master_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = conversational_rag_chain.invoke(
                {"input": query},
                config={"configurable": {"session_id": session_id}}
            )
            break
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                time.sleep(10 * (attempt + 1))  # wait 10s, 20s before retrying
                continue
            raise e
    
    sources = []
    if "context" in response:
        for doc in response["context"]:
            source = doc.metadata.get("source", "Unknown Source")
            if source not in sources:
                sources.append(source)
                
    return response.get("answer", "No answer found"), sources
