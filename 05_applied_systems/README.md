# 05 — Applied / capstone systems

Standalone repos and deployable demos that turn course skills into applied systems.

## RAG — PDF Question Answering

| | |
|--|--|
| **Repo** | [github.com/Sober-Migo/RAG](https://github.com/Sober-Migo/RAG) |
| **Demo** | [huggingface.co/spaces/Sober-Migo/RAG](https://huggingface.co/spaces/Sober-Migo/RAG) |
| **Stack** | LangChain · Chroma · ONNX MiniLM · Groq · Gradio |
| **Origin** | IBM GenAI specialization C06–C07, reimplemented for free-tier deploy |

Pipeline: PDF → chunk → embed → retrieve → grounded generation (Markdown UI).

## PACE — Egyptian Psychiatric Speech Analytics

| | |
|--|--|
| **Repo** | [PACE-Egyptian_Psychiatric_Speech_Analytics](https://github.com/Sober-Migo/PACE-Egyptian_Psychiatric_Speech_Analytics) |
| **Stack** | FastAPI · Whisper · Wav2Vec2 · CAMeLBERT · Qwen · multi-GPU · Docker-oriented |
| **Focus** | Multimodal speech analytics for Egyptian Arabic clinical-style sessions |

## HelloML — Handwritten Digit OCR

| | |
|--|--|
| **Repo** | [HelloML](https://github.com/Sober-Migo/HelloML) |
| **Stack** | sklearn Pipeline · GridSearchCV · MLP / logistic / linear · joblib |
| **Focus** | End-to-end classical ML system on DIDA digits |

## Fasten Your Seat Belts AI Portal

| | |
|--|--|
| **Source** | [Portal files](./07_fasten_your_seat_belts_ai_portal/) · [Live Hugging Face Space](https://huggingface.co/spaces/Sober-Migo/fasten-your-seat-belts-ai) |
| **Stack** | Gradio · SQLite · LangChain · Chroma · DistilBERT · Docker |
| **Deploy** | Render · Railway · Fly.io configurations are included in the project folder |

The sentiment model is CPU-based, downloads its weights on first use, and requires at least 2 GB RAM. Check provider pricing before deploying multiple services.

---

These are the primary **portfolio showcase** items; course folders (01–04) document the training path behind them.
