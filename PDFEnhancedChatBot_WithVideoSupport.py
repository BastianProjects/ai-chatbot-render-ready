
import streamlit as st
import os
import shutil
from PDFhandling import load_pdf, upload_pdf, pdfs_directory
from langchain.document_loaders import SeleniumURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document

# -- Settings --
CHROMA_DB_DIR = "chroma_db"
os.makedirs(CHROMA_DB_DIR, exist_ok=True)

# -- Init Models --
embeddings = OpenAIEmbeddings()
llm = ChatOpenAI(model="gpt-3.5-turbo")

# -- Chat Template --
template = """You are a helpful assistant. Use the following context to answer the question.
Chat History:
{history}

Context:
{context}

Question: {question}
Answer:"""

@st.cache_resource
def get_vector_store():
    return Chroma(collection_name="everything", embedding_function=embeddings, persist_directory=CHROMA_DB_DIR)

def split_text(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_documents(docs)

def index_docs(docs, label):
    store = get_vector_store()
    wrapped = [Document(page_content=doc.page_content, metadata={"source": label}) for doc in docs]
    store.add_documents(wrapped)
    store.persist()

def retrieve_docs(query):
    store = get_vector_store()
    return store.similarity_search(query, k=6)

def answer_question(question, context):
    history = "\n".join(f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.chat_history[-6:])
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm
    return chain.invoke({"question": question, "context": context, "history": history})

# -- Streamlit UI --
st.title("🧠 AI Chatbot for PDFs and URLs")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if st.sidebar.button("🧹 Clear DB"):
    get_vector_store.clear()
    shutil.rmtree(CHROMA_DB_DIR)
    st.sidebar.success("Vector DB cleared.")

if st.sidebar.button("🗑 Clear Chat"):
    st.session_state.chat_history = []

url = st.text_input("Enter a URL to index")
if url:
    loader = SeleniumURLLoader(urls=[url])
    docs = loader.load()
    chunks = split_text(docs)
    index_docs(chunks, url)
    st.success("URL indexed.")

uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)
if uploaded_files:
    for pdf in uploaded_files:
        upload_pdf(pdf)
        text = load_pdf(os.path.join(pdfs_directory, pdf.name))
        chunks = split_text([Document(page_content=text)])
        index_docs(chunks, pdf.name)
        st.success(f"{pdf.name} indexed.")

question = st.chat_input("Ask a question...")
if question:
    st.chat_message("user").write(question)
    results = retrieve_docs(question)
    context = "\n\n".join(doc.page_content for doc in results)
    answer = answer_question(question, context)
    st.chat_message("assistant").write(answer)
    st.session_state.chat_history.append({"role": "user", "content": question})
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
