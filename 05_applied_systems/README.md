# 🛬 Zone 05 — Open Skies

> **Mission:** *"Turn the lab into a product someone can touch."*
> Five systems where the training is behind you and the goal is simple: something real, deployed, demoable. No notebooks in this chapter — only projects that run.

**Source:** standalone production-style repos + in-repo builds
**Status:** ✈ 5/5 systems deployed

---

## 🏔️ Hideout 01 — RAG: PDF Question Answering

> *"Let this document speak."*
> Point it at a PDF, ask it anything, and get an answer grounded in the text — with citations. Built on the [Zone 04](../04_generative_ai_llms/) capstone track, rebuilt with free-tier primitives so it runs anywhere.

| | |
|--|--|
| **Repo** | [github.com/Sober-Migo/RAG](https://github.com/Sober-Migo/RAG) |
| **Live demo** | [huggingface.co/spaces/Sober-Migo/RAG](https://huggingface.co/spaces/Sober-Migo/RAG) |
| **Stack** | LangChain · Chroma · ONNX MiniLM · Groq · Gradio |
| **Pipeline** | PDF → chunk → embed → retrieve → grounded generation |
| **Origin** | IBM GenAI C06–C07, reimplemented for free-tier deployment |

## 🏔️ Hideout 02 — PACE: Egyptian Psychiatric Speech Analytics

> *"Listen to what is said, and what is not."*
> A multimodal pipeline for Egyptian Arabic clinical-style sessions: transcribe speech, model the conversation, surface analytics. The most ambitious system in the campaign — multi-model, multi-GPU.

| | |
|--|--|
| **Repo** | [PACE-Egyptian_Psychiatric_Speech_Analytics](https://github.com/Sober-Migo/PACE-Egyptian_Psychiatric_Speech_Analytics) |
| **Stack** | FastAPI · Whisper · Wav2Vec2 · CAMeLBERT · Qwen · multi-GPU · Docker-oriented |
| **Focus** | Multimodal speech analytics for Egyptian Arabic clinical-style sessions |

## 🏔️ Hideout 03 — HelloML: Handwritten Digit OCR

> *"The classic grudge match: pixels vs. predictions."*
> Where the campaign began its applied arc: an end-to-end classical ML system on DIDA handwritten digits. Pipeline discipline, hyperparameter search, joblib serialization — basics done right.

| | |
|--|--|
| **Repo** | [HelloML](https://github.com/Sober-Migo/HelloML) |
| **Stack** | sklearn Pipeline · GridSearchCV · MLP / logistic / linear · joblib |
| **Focus** | End-to-end classical ML system on DIDA digits |

## 🏔️ Hideout 04 — Enterprise SQL Assistant

> *"Type it like a human, run it like a query — without breaking the vault."*
> Natural language in, read-only SQL out, against a real company database. Powered by a **Hermes Agent custom skill** (schema inspection + safety validation + summarization), wrapped in a standalone Gradio interface, packaged for Hugging Face Spaces.

| | |
|--|--|
| **Source** | [`06_hermes_sql_assistant/`](./06_hermes_sql_assistant/) |
| **Stack** | Hermes Agent skill · SQLite · Gradio · Docker |
| **Safety rule** | SELECT-only — no writes can ever reach the database |

## 🏔️ Hideout 05 — Fasten Your Seat Belts AI Portal

> *"The front door of the whole campaign."*
> A single Gradio hub that ties the systems together: SQL Q&A and sentiment analytics behind one interface, with CPU-friendly deployments wired up for Render, Railway, and Fly.io. This is where a recruiter lands first.

| | |
|--|--|
| **Source** | [`07_fasten_your_seat_belts_ai_portal/`](./07_fasten_your_seat_belts_ai_portal/) |
| **Live demo** | [huggingface.co/spaces/Sober-Migo/fasten-your-seat-belts-ai](https://huggingface.co/spaces/Sober-Migo/fasten-your-seat-belts-ai) |
| **Stack** | Gradio · SQLite · LangChain · Chroma · DistilBERT · Docker |
| **Deploy configs** | Render · Railway · Fly.io (all included in the project folder) |

> ⚠️ The sentiment model is CPU-based, downloads its weights on first use, and needs ≥2 GB RAM. Check provider pricing before deploying multiple services.

---

These five are the primary **portfolio showcase** — [Zone 01](../01_machine_learning/) through [Zone 04](../04_generative_ai_llms/) document the journey behind them.