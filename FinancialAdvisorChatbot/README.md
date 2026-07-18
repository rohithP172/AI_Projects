# 💰 Personal Finance Chatbot

A local privacy-friendly AI assistant that uses **LangChain**, **FAISS**, **Hugging Face Transformers**, and **Gradio** to answer user questions based on their **bank transaction CSV data**.

This chatbot uses **RAG (Retrieval-Augmented Generation)** powered by the **Phi-3-mini-4k-instruct** language model and MiniLM sentence embeddings for accurate and relevant financial responses.

---

## 🚀 Features

- ✅ Query your bank transactions using natural language
- ✅ Runs entirely **locally** (no cloud calls or APIs)
- ✅ Uses **FAISS** to retrieve relevant records
- ✅ Fast and efficient even on **CPU-only machines**
- ✅ Clean Gradio UI with example questions
- ✅ Safe: does **not hallucinate** or invent information

---

## 🧠 How It Works

1. **Embeds** your `bank_statement_1_year.csv` file using `MiniLM` embeddings.
2. **Indexes** the data using `FAISS` for fast similarity search.
3. **Retrieves** relevant transactions based on your question.
4. **Formats** the data into a prompt using a **custom template**.
5. **Feeds** the prompt into the **Phi-3-mini** model via Hugging Face's pipeline.
6. **Displays** the AI-generated answer in a chat interface.

---

## 📦 Dependencies

Clone Repo:

```bash
git clone https://github.com/RajeshMakala/MSAI_631/tree/main/Final_Project.git
```

Install all required packages:

```bash
pip install torch transformers langchain langchain-community langchain-huggingface pandas faiss-cpu gradio
```

> ✅ **Note**: Python 3.8–3.12 is recommended.

---

## 📂 File Structure

```
├── bank_statement_1_year.csv   # Your transactional data (must be present)
├── app.py                      # Main chatbot logic (your script)
├── README.md                   # You're here!
```

---

## 📊 CSV Format

Make sure your CSV follows this format:

```csv
Date,Description,Category,Amount
2024-07-01,Coffee Shop,Food & Drink,5.50
2024-07-02,Groceries,Food & Drink,75.20
...
```

---

## 🖥️ Running the App

```bash
python app.py
```

Then open your browser to the automatically launched Gradio interface.

---

## 🧪 Example Questions

Try asking:

- "What was my total spending on Food & Drink?"
- "Did I have any expenses on July 12th?"
- "What was my biggest expense this month?"
- "How much income did I receive in July?"

---

## 📌 Notes

- If it's your first time, the model and tokenizer will be downloaded (~500MB).
- Ensure your system has at least **4GB RAM** for smooth operation.
- Gradio will run locally and **won't share your data** externally.

---

## 🛡️ Privacy

All data is processed **locally** on your device. No data is sent to external servers or APIs. This is ideal for **personal finance privacy**.

---

## 🔧 Troubleshooting

- **Tokenizer/Model download error**? → Check internet connection and retry.
- **"Chatbot still initializing"**? → Wait for model and embeddings to load fully.
- **App crashes**? → Ensure your CSV is valid and dependencies are installed.

---

## 📜 License

This project is open-source under the MIT License. Use it, modify it, improve it — freely and responsibly.

---

## 🙌 Credits

- [LangChain](https://www.langchain.com/)
- [Hugging Face Transformers](https://huggingface.co)
- [Gradio](https://gradio.app/)
- [FAISS](https://github.com/facebookresearch/faiss)
