from langchain.agents import AgentExecutor
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.llms import LlamaCpp, HuggingFaceEndpoint
from datetime import datetime
from langchain_community.vectorstores import Chroma
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings

repo_id = "mistralai/Mistral-7B-Instruct-v0.2"
llama_model_path = "C:/Users/agadi/Documents/A/My Llama 2/llama.cpp/models/llama-2-7b-chat/ggml-model-f16.gguf"
mistral_model_path = "C:/Users/agadi/Documents/A/My Llama 2/llama.cpp/models/llama-2-7b-chat/mistral-7b-instruct-v0.2.Q6_K.gguf"

# DB_FAISS_PATH = 'vectorstore/db_faiss'
#wvprevue/e5-mistral-7b-instruct
#db = FAISS.load_local(DB_FAISS_PATH, embeddings)

embeddings = HuggingFaceEmbeddings( model_name="thenlper/gte-large",
    encode_kwargs={"normalize_embeddings": True}
    )

class MyEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        emb = embeddings.embed_query(input.page_content)
        return emb

client = chromadb.HttpClient(host='localhost', port=8000)
db = Chroma(collection_name="umkc", client=client, embedding_function=embeddings)
faq_db = client.get_or_create_collection(name="umkc_faq")
faq_check_db = Chroma(collection_name="umkc_faq", client=client, embedding_function=embeddings)

n_gpu_layers = 1  
n_batch = 512  

llm = LlamaCpp(
    model_path=mistral_model_path,
    n_gpu_layers=n_gpu_layers,
    n_batch=n_batch,
    n_ctx=2048,
    f16_kv=True,  
    verbose=False,
)


def add_to_faq(faq_data):
    
    embedding = embeddings.embed_query(faq_data["question"])
    faq_db.add(
        documents=[faq_data["question"]],
        metadatas=[faq_data],
        embeddings= embedding,
        ids=[str(faq_db.count()+1)]
    )


def ask_llm(question):
    template = """
    Use the following context (delimited by <ctx></ctx>) to answer. Do not answer anything outside of the context and answer only to the asked question. Your responses should be concise, informative, and focused solely on addressing the questions asked. If you do not find the answer, tell that you could not find any relevant information. Do not add anything unnecessary.
    ------
    <ctx>
    {context}
    </ctx>
    ------
    {question}
    Answer:
    """
    prompt = PromptTemplate(
        input_variables=[ "context", "question"],
        template=template,
    )

    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)# Run chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type='stuff',
        retriever= db.as_retriever(search_kwargs={'k': 1}),
        verbose=False,
        chain_type_kwargs={
            "verbose": False,
            "prompt": prompt
        }
    )
    result = qa_chain({"query": question})
    answer = result["result"]

    faq_data = {
        "question": question,
        "answer": answer
    }

    add_to_faq(faq_data)
    
    return answer

def check_faq(question):
    docs = faq_check_db.similarity_search_with_score(question)
    if len(docs) == 0:
        return ask_llm(question)
    print("Similarity Score : ",docs[0][1])
    return docs[0][0].metadata['answer'] if docs[0][1] <= 0.1 else ask_llm(question)


def send_query(question):
    start_time = datetime.now()
    answer = check_faq(question)
    end_time = datetime.now()
    print(f"Question: {question}")
    print(f"Answer: {answer}")
    elapsed_time = end_time - start_time
    elapsed_seconds = elapsed_time.total_seconds()
    print(f"Time taken: {elapsed_seconds} seconds")
    return answer