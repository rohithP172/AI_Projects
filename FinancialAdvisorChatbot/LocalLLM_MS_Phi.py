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

# --- Configuration ---
MODEL_NAME = "microsoft/Phi-3-mini-4k-instruct"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

def get_device():
    """Detects if a CUDA-compatible GPU is available; otherwise, returns CPU."""
    min_memory_required = 16 * 1024  # 16GB in MB

    if torch.cuda.is_available():
        # Ensure CUDA compatibility (avoid Metal GPUs on Apple devices)
        device = "cuda"
        total_memory = torch.cuda.get_device_properties(device).total_memory // (1024 * 1024)  # Convert to MB
        available_memory = total_memory - torch.cuda.memory_reserved(device)

        print(f"GPU detected: {torch.cuda.get_device_name(device)}")
        print(f"Total GPU Memory: {total_memory} MB")
        print(f"Available GPU Memory: {available_memory} MB")

        if available_memory >= min_memory_required:
            return device
        else:
            print("Insufficient GPU memory, switching to CPU.")

    # If CUDA is not available, check for MPS (Apple Metal) and fallback to CPU
    if torch.backends.mps.is_available():
        print("Apple MPS GPU detected, but CUDA is required. Using CPU.")
    
    print("No suitable CUDA-compatible GPU found, using CPU.")
    return "cpu"

# Usage
device = get_device() # Hugging Face Spaces default is CPU
print(f"Using device: {device}")

# --- Transactional Data File ---
TRANSACTION_DATA_FILE = "bank_statement_1_year.csv" # Define the CSV file name

# Global variables for the FAISS vector store and Langchain QA chain
faiss_db = None
llm_pipeline = None # Changed from qa_chain to llm_pipeline
llm_tokenizer = None

# --- Custom Prompt Template ---
# This prompt guides the LLM to use the provided context effectively
CUSTOM_PROMPT_TEMPLATE = """You are a helpful financial assistant. Your task is to answer user questions about their bank transactions.
Use ONLY the following retrieved bank transaction information to answer the question.
If the answer cannot be found in the provided transaction information, clearly state that you cannot find the answer in the given data.
Do not make up any information. Do not Mention the source of the information or Transaction ID.

Retrieved Transaction Information:
{context}

User Question: {question}

Financial Assistant Answer:"""


# --- Model Loading ---
def load_llm_and_tokenizer():
    """Loads the Phi-3 LLM and its tokenizer."""
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
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True,
        )
        model.to(device)
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Please ensure you have an an active internet connection for the first run to download the model weights.")
        print(f"Also, check your system's RAM. Phi-3-mini-4k-instruct typically needs around 4-8GB RAM. Device: {device}")
        raise

    llm_pipeline_instance = pipeline( # Renamed to avoid confusion with global
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=1024,
        do_sample=True,
        temperature=0.7,
        top_k=50,
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
        raise FileNotFoundError(f"Error: The file '{file_path}' was not found in the current directory.")

    try:
        loader = CSVLoader(file_path=file_path)
        documents = loader.load()

        # Initialize embeddings model using the Langchain class
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
    Generates a text response using the RAG approach, leveraging the FAISS database and Phi-3 pipeline.
    """
    global faiss_db
    global llm_pipeline
    global llm_tokenizer

    if faiss_db is None or llm_pipeline is None or llm_tokenizer is None:
        return "Chatbot is still initializing. Please wait a moment."

    print(f"\nUser message received: '{message}'")

    try:
        # 1. Retrieve relevant documents from FAISS
        # We'll retrieve more documents to give the LLM ample context
        retrieved_docs = faiss_db.as_retriever(search_kwargs={"k": 15}).invoke(message) # Increased k to 15

        # 2. Format the retrieved documents into a single context string
        context_str = "\n".join([doc.page_content for doc in retrieved_docs])

        # 3. Format the custom prompt with the retrieved context and user's question
        # The CUSTOM_PROMPT_TEMPLATE will now be used to structure the *actual* query for the LLM
        formatted_prompt_for_llm = CUSTOM_PROMPT_TEMPLATE.format(
            context=context_str,
            question=message
        )

        # 4. Apply the model's chat template to the entire formatted prompt
        # This is crucial for Phi-3 to correctly understand the instruction format
        messages_for_phi3 = [
            {"role": "user", "content": formatted_prompt_for_llm},
        ]
        final_input_for_phi3 = llm_tokenizer.apply_chat_template(
            messages_for_phi3,
            tokenize=False,
            add_generation_prompt=True # Ensures the model knows it's supposed to generate a response
        )

        # 5. Generate the response using the LLM pipeline
        output = llm_pipeline(final_input_for_phi3)

        # Extract the generated text, which is typically the 'generated_text' from the first item
        # and then remove the input prompt part.
        generated_text = output[0]['generated_text']

        # The model might repeat the input prompt, so we need to remove it
        if generated_text.startswith(final_input_for_phi3):
            response = generated_text[len(final_input_for_phi3):].strip()
        else:
            response = generated_text.strip() # Fallback if it doesn't start exactly

        # Clean up any remaining special tokens
        response = response.replace("<|end|>", "").strip()
        response = response.replace("<|endoftext|>", "").strip()
        response = response.replace("<|assistant|>", "").strip() # Remove assistant token if present

        return response

    except Exception as e:
        print(f"Error during RAG generation: {e}")
        return "Sorry, I encountered an error while processing your request. Please try again."

# --- Main Application Logic ---
print("\n--- Personal Finance Helper Chatbot (Gradio UI) ---")
print("Initializing components for the first time. This may take a few minutes...")

try:
    # 1. Load LLM and Tokenizer
    llm_pipeline, llm_tokenizer = load_llm_and_tokenizer()
    # No need for HuggingFacePipeline wrapper if we're calling pipeline directly
    # llm = HuggingFacePipeline(pipeline=llm_pipeline)

    # 2. Load and build FAISS database from the specified CSV file
    faiss_db = load_faiss_database_from_file(TRANSACTION_DATA_FILE)

    # 3. We are no longer using Langchain's RetrievalQA chain directly
    # qa_chain = RetrievalQA.from_chain_type(...)
    print("All components initialized successfully. Starting Gradio UI...")

except Exception as e:
    print(f"Fatal error during initialization: {e}")
    print("The application cannot start. Please ensure the CSV file exists and dependencies are installed.")
    exit()

# --- Gradio UI Setup ---
demo = gr.ChatInterface(
    fn=chatbot_response,
    chatbot=gr.Chatbot(height=500, type='messages'),
    textbox=gr.Textbox(placeholder="Ask me about your finances...", container=False, scale=7),
    title="💰 Personal Finance Chatbot",
    description=(
        f"Ask me questions about your transactional data "
        "All data and processing stay on your device for privacy."
    ),
    theme="huggingface",
    examples=[
        "What was my total spending on Food & Drink?",
        "Tell me about my income in July.",
        "Did I have any expenses on July 12th?",
        "What was my biggest expense this month?",
    ],
)

# Launch the Gradio app
demo.launch(share=False, inbrowser=True)