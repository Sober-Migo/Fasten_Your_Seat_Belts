# Fasten Your Seat Belts AI Portal

A Gradio portal that brings together the SQL assistant, PDF RAG Q&A, and an English sentiment classifier using `distilbert/distilbert-base-uncased-finetuned-sst-2-english`. The model is Apache-2.0, fine-tuned on SST-2, and is not trained on your own data.

## Run locally

Install Python 3.11, then install CPU PyTorch and the remaining dependencies:

```bash
pip install --index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple torch==2.3.1+cpu
pip install -r requirements.txt
python app.py
```

The sentiment model weights are downloaded from the public Hugging Face Hub on the first prediction. The service needs outbound internet access and at least 2 GB RAM. `GROQ_API_KEY` is optional and is only used for generated RAG answers; without it, the RAG tab returns relevant passages.

## Deploy

This folder contains deployment configurations for Render, Railway, and Fly.io. Each service downloads the model on first use. CPU inference may be slow. Deploying all three creates separate services and may incur separate bills.

- **Render:** create a Blueprint from the repository and select `05_applied_systems/07_fasten_your_seat_belts_ai_portal/render.yaml` as the Blueprint file. It sets this folder as the service root and uses the paid Standard plan.
- **Railway:** create a service from the repository and set its root directory to `05_applied_systems/07_fasten_your_seat_belts_ai_portal`; `railway.json` selects the Dockerfile and configures health checks.
- **Fly.io:** change the placeholder `app` name in `fly.toml` to a globally unique name, then run `fly launch --no-deploy` and `fly deploy` from this folder.

In the Hugging Face Space, classifier calls use the ZeroGPU-compatible wrapper and may consume ZeroGPU quota. External Docker deployments run the model on CPU without that wrapper.
