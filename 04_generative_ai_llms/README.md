# 🔥 Zone 04 — The Engine Room

> **Mission:** *"Where transformers stop being a library and start being architecture."*
> Seven labs building a transformer from attention matrices up, then teaching it to follow instructions, judge its own answers, and finally build fields of knowledge.

**Specialization:** IBM Generative AI Engineering with LLMs
**Source:** [IBM_Generative_AI_Engineering_with_LLMs_Specialization](https://github.com/Sober-Migo/IBM_Generative_AI_Engineering_with_LLMs_Specialization)
**Status:** ✅ Zone cleared — 7/7 labs

---

## 🎯 Lab log

| Lab | Theme | Key experiments |
|-----|-------|-----------------|
| **C01 — Fuel & Ignition** | Architecture & data preparation | Tokenization from scratch · NLP data loaders · exploring GenAI libraries |
| **C03 — Metalwork** | Language modeling with transformers | **Boss: build a transformer from scratch.** Attention mechanism, positional encoding, GPT-like causal decoder, Baby BERT encoder |
| **C04 — Precision Tuning** | Fine-tuning transformers | HF model loading & inference · fine-tuning with PyTorch/HF · adapters · **LoRA** · **QLoRA** |
| **C05 — The Conscience (RLHF)** | Advanced fine-tuning | Instruction fine-tuning · reward modeling · **PPOTrainer** · DPO |
| **C06 — Retrieval & Agency** | RAG + LangChain agents | LangChain fundamentals · RAG w/ Hugging Face & PyTorch · weather agent · document QA |
| **C07 — Capstone Track** | Full RAG application | Document loaders → text-splitter → embeddings → vector store → retriever → grounded answers |

---

## ⚔️ Master boss — *"Keep the generation grounded"*

The hardest enemy here was not the model, but **its fluent hallucination**. A transformer that confidently invents citations is worse than useless. The turning point: building a pipeline that only allows answers *grounded in retrieved chunks*.

**The war ended here. And the peace treaty went live:**
→ 📄 [**RAG — PDF Q&A**](../05_applied_systems/#rag--pdf-question-answering) reimplements this capstone without Watsonx — Groq + local ONNX embeddings + Gradio — and is deployed at [HF Space Sober-Migo/RAG](https://huggingface.co/spaces/Sober-Migo/RAG).

---

## 🔓 Unlocks

Transformer internals · tokenization · GPT/BERT architectures · LoRA & QLoRA fine-tuning · RLHF (reward modeling, PPO, DPO) · LangChain · RAG pipelines · AI agents

**→ Unlocks [Zone 05 — Open Skies](../05_applied_systems/) — where the campaign becomes product.**