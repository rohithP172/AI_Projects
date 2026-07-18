import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFacePipeline
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import CSVLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import pandas as pd
import io
import os
import gradio as gr

# Add this line to suppress tokenizers parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false" 

# --- Configuration ---
MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

def get_device():
    """Detects if a CUDA-compatible GPU is available; otherwise, returns CPU."""
    min_memory_required = 16 * 1024  # 16GB in MB

    if torch.cuda.is_available():
        # Ensure CUDA compatibility (avoid Metal GPUs on Apple devices)
        device = "cuda"
        total_memory = torch.cuda.get_device_properties(device).total_memory // (1024 * 1024)  # Convert to MB
        
        print(f"GPU detected: {torch.cuda.get_device_name(device)}")
        print(f"Total GPU Memory: {total_memory} MB")

        if total_memory >= min_memory_required:
            return device
        else:
            print("Insufficient GPU memory, switching to CPU.")

    if torch.backends.mps.is_available():
        print("Apple MPS GPU detected, but CUDA is required. Using CPU.")
    
    print("No suitable CUDA-compatible GPU found, using CPU.")
    return "cpu"

# Usage
device = get_device()
print(f"Using device: {device}")

# --- Transactional Data File ---
TRANSACTION_DATA_FILE = "bank_statement_1_year.csv"

# Global variables for the FAISS vector store and Langchain QA chain
faiss_db = None
llm_pipeline = None
llm_tokenizer = None

# --- Custom Prompt Template ---
CUSTOM_PROMPT_TEMPLATE = """You are a helpful financial assistant. Your task is to answer user questions about their bank transactions.
Use ONLY the following retrieved bank transaction information to answer the question.
If the answer cannot be found in the provided transaction information, clearly state that you cannot find the answer in the given data.
Do NOT make up any information.
Do NOT mention the source of the information or Transaction ID.
Be concise and to the point. Do NOT explain your reasoning or internal thought process.

Retrieved Transaction Information:
{context}

User Question: {question}

Financial Assistant Answer:"""


# --- Model Loading ---
def load_llm_and_tokenizer():
    """Loads the specified LLM and its tokenizer."""
    print(f"Loading tokenizer for {MODEL_NAME}...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        print("Tokenizer loaded successfully.")
    except Exception as e:
        print(f"Error loading tokenizer: {e}")
        print("Please ensure you have an active internet connection for the first run to download the tokenizer.")
        raise

    print(f"Loading model for {MODEL_NAME} on {device}...")
    try:
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.bfloat16 if device == "cuda" else torch.float32,
            low_cpu_mem_usage=True,
        )
        model.to(device)
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Please ensure you have an active internet connection for the first run to download the model weights.")
        print(f"Also, check your system's RAM. {MODEL_NAME} typically needs around 1-2GB RAM. Device: {device}")
        raise

    llm_pipeline_instance = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=256, # Keep this reasonably high for detailed answers if needed
        do_sample=True,
        temperature=0.7,
        top_k=10,
        eos_token_id=tokenizer.eos_token_id,
        device=device
    )
    return llm_pipeline_instance, tokenizer

def load_faiss_database_from_file(file_path: str):
    """
    Loads transactional data from a CSV file, processes it,
    creates embeddings, and builds a FAISS vector store.
    """
    print(f"Loading and processing transactional data from {file_path} for FAISS...")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: The file '{file_path}' was not found at the specified path.")

    try:
        loader = CSVLoader(file_path=file_path)
        documents = loader.load()

        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        print(f"Embedding model '{EMBEDDING_MODEL_NAME}' loaded.")

        db = FAISS.from_documents(documents, embeddings)
        print("FAISS vector database built successfully.")
        return db
    except Exception as e:
        print(f"Error building FAISS database from file: {e}")
        print("Please ensure 'pandas', 'langchain', 'faiss-cpu', 'sentence-transformers', and 'langchain-huggingface' are installed.")
        print("Also, check the format of your CSV file.")
        raise

# --- Chatbot Response Function for Gradio ---
def chatbot_response(message, history):
    """
    Generates a text response using the RAG approach, leveraging the FAISS database and LLM pipeline.
    
    Args:
        message (str): The user's current message.
        history (list): The list of previous message pairs (user, bot).
                        Gradio's ChatInterface passes this.
    Returns:
        tuple: (updated_history, bot_response_text)
    """
    global faiss_db
    global llm_pipeline
    global llm_tokenizer

    if faiss_db is None or llm_pipeline is None or llm_tokenizer is None:
        return history + [[message, "Chatbot is still initializing. Please wait a moment."]]

    print(f"\nUser message received: '{message}'")

    try:
        # 1. Retrieve relevant documents from FAISS
        retrieved_docs = faiss_db.as_retriever(search_kwargs={"k": 15}).invoke(message)

        # 2. Format the retrieved documents into a single context string
        context_str = "\n".join([doc.page_content for doc in retrieved_docs])

        # 3. Format the custom prompt with the retrieved context and user's question
        formatted_prompt_for_llm = CUSTOM_PROMPT_TEMPLATE.format(
            context=context_str,
            question=message
        )

        # 4. Apply the model's chat template to the entire formatted prompt
        messages_for_llm = [
            {"role": "user", "content": formatted_prompt_for_llm},
        ]
        final_input_for_llm = llm_tokenizer.apply_chat_template(
            messages_for_llm,
            tokenize=False,
            add_generation_prompt=True
        )

        # 5. Generate the response using the LLM pipeline
        output = llm_pipeline(final_input_for_llm)

        generated_text = output[0]['generated_text']

        # The model might repeat the input prompt, so we need to remove it
        if generated_text.startswith(final_input_for_llm):
            response = generated_text[len(final_input_for_llm):].strip()
        else:
            response = generated_text.strip()

        # Clean up any remaining special tokens
        response = response.replace("</s>", "").strip()
        response = response.replace("<|end_of_text|>", "").strip() 
        response = response.replace("<|end|>", "").strip()
        response = response.replace("<|endoftext|>", "").strip()
        response = response.replace("<|assistant|>", "").strip()

        return response

    except Exception as e:
        print(f"Error during RAG generation: {e}")
        history.append([message, "Sorry, I encountered an error while processing your request. Please try again."])
        return history

# --- Main Application Logic ---
print("\n--- Personal Finance Helper Chatbot (Gradio UI) ---")
print("Initializing components for the first time. This may take a few minutes...")

try:
    llm_pipeline, llm_tokenizer = load_llm_and_tokenizer()
    faiss_db = load_faiss_database_from_file(TRANSACTION_DATA_FILE)
    
    print("All components initialized successfully. Starting Gradio UI...")

except Exception as e:
    print(f"Fatal error during initialization: {e}")
    print("The application cannot start. Please ensure the CSV file exists and dependencies are installed.")
    exit()

# --- Gradio UI Setup ---
demo = gr.ChatInterface(
    fn=chatbot_response,
    type="messages",
    textbox=gr.Textbox(placeholder="Ask me about your finances...", container=False, scale=7),
    title="💰 Personal Finance Chatbot",
    description=(
        f"Ask me questions about your transactional data. "
        "All data and processing stay on your device for privacy."
    ),
    examples=[
        "What was my total spending on Food & Drink?",
        "Tell me about my income in July.",
        "Did I have any expenses on July 12th?",
        "What was my biggest expense this month?",
    ],
    analytics_enabled=False 
)

# Launch the Gradio app
demo.launch(share=False, inbrowser=True)