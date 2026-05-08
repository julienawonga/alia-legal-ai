# ⚖️  Alia: Democratizing Ivorian Labor Law through Voice and Gemma 4
### Bridging the Legal Gap for Millions of Dioula/Bambara Speakers in Ivory Coast

[![Gemma Impact Challenge](https://img.shields.io/badge/Gemma_Impact_Challenge-Submission-blue.svg)](https://www.kaggle.com/competitions/gemma-impact-challenge)
[![Track: Digital Equity](https://img.shields.io/badge/Track-Digital_Equity_%26_Inclusivity-orange.svg)]()
[![Model: Gemma 4](https://img.shields.io/badge/Model-Gemma_4_E4B--it_Fine--Tuned-green.svg)]()

> **"Every challenge has a perfect match, and the clock is ticking. Real innovation happens when we build for the places that need it most. Coming off the heels of May Day (International Workers' Day), the gap between labor rights and labor reality has never been more apparent."**

**Alia** is a pioneering bilingual legal assistant designed to democratize access to labor law in Ivory Coast. By combining the power of a fine-tuned **Gemma 4** model with a modular, voice-first pipeline, Alia provides millions of Bambara/Dioula speakers with direct, accurate, and actionable legal guidance in their native tongue.

---

## 📖 The Context & The "Wow" Factor

While the world recently celebrated International Workers' Day, for 90% of the Ivorian labor force, rights remain a luxury of the elite. In Ivory Coast, the **informal sector accounts for approximately 90% of the total labor force**. These workers—street vendors, agricultural laborers, small-scale mechanics—are theoretically protected by the Ivorian *Code du Travail*, but in reality, they operate completely outside of legal safety nets.

When an informal worker faces an unfair dismissal or hazardous working conditions, the barriers to justice are insurmountable:
1. **The Linguistic Divide**: The law is written in formal, complex French. While general literacy is improving, legal literacy in French remains a massive barrier for millions who communicate primarily in local languages like Bambara/Dioula.
2. **The Cost of Justice**: Seeking advice from a human lawyer is financially impossible for informal workers.

**Alia breaks this barrier.** It strips away the requirements for literacy, French fluency, and legal fees. A user simply speaks their legal problem in Bambara. Alia processes the audio, consults a highly specialized Gemma 4 "Legal Brain", and speaks the legal advice back to them in their native tongue.

This is true **Digital Equity**—putting the power of the law directly into the hands of the workers who build the country, closing the justice gap for 90% of the workforce.

---

## 🧠 How We Implemented Gemma 4 (The "Source of Truth")

To build a model capable of understanding and citing complex Ivorian law without hallucinating, we could not rely on standard Retrieval-Augmented Generation (RAG) alone. We needed a model that natively "spoke" the law.

We chose **`unsloth/gemma-4-E4B-it`** as our base model. Its parameter efficiency makes it ideal for cost-effective deployment (a critical requirement for public-service/NGO tools), while its frontier intelligence handles complex legal reasoning.

### 1. Curating the Ivorian Legal Dataset
We digitized and structured the entire corpus of the Ivorian Labor Code and Social Security laws into **2,357 discrete JSON files**. Each file represents a specific article (e.g., `art_100_loi_n_99_477_du_02_aout_1999_portant_modification_du_code_de_prevoyance_sociale.json`), containing metadata such as the legal field, chapter, status (e.g., "EN VIGUEUR"), and the exact textual content.

### 2. Synthetic Conversational Generation
Using a custom Python pipeline, we transformed these 2,357 static JSON files into a rich, multi-turn conversational dataset. For every single article, our script automatically generated diverse User/Assistant interactions.

Here is an excerpt of how we engineered the training data:

```python
def generate_examples(entry):
    titre = entry.get("text_juridique_name", "")
    article_num = entry.get("article_num", "")
    contenu = extract_article_content(entry.get("text", ""))

    system_prompt = (
        "Tu es un assistant juridique spécialisé en droit ivoirien. "
        "Tu connais les lois, décrets et règlements de la République de Côte d'Ivoire. "
        "Réponds avec précision en citant les textes applicables."
    )

    examples = [
        {"conversations": [
            {"role": "system",    "content": system_prompt},
            {"role": "user",      "content": f"Que dit l'article {article_num} de la {titre} ?"},
            {"role": "assistant", "content": f"L'article {article_num} de la {titre} prévoit :\n\n{contenu}"}
        ]},
        # Additional conversational turns for broad domain questions and definitions...
    ]
    return examples
```

### 3. Supervised Fine-Tuning (SFT) & Grounding
By training `unsloth/gemma-4-E4B-it` on this conversational dataset using LoRA adapters, the model learned the specific cadence, structure, and exact citations of Ivorian law. The resulting weights (`julienawonga/gemma-4-ivorian-labor-law-merged`) ensure that when Alia answers a question, it grounds its response by explicitly citing the relevant article, refusing out-of-domain prompts and eliminating generic "US-centric" legal hallucinations.

---

## 🏗️ Technical Architecture

Alia utilizes a multi-model, cost-optimized pipeline orchestrated by LangGraph to handle the complexities of voice and memory:

<p align="center">
  <img src="./assets/Alia.png" alt="Technical Architecture" width="300">
</p>
---

## 📂 Repository Structure

- `app.py`: The main Streamlit bilingual UI (French/Bambara) and entry point.
- `pipeline/orchestrator.py`: The LangGraph state machine managing the multi-model flow.
- `services/legal_llm.py`: Integration with the fine-tuned Gemma 4 API.
- `services/translation.py`: Gemini integrations for the cross-lingual bridge (Bambara ↔ French).
- `Dockerfile`: Production-ready, stateless container configuration for Google Cloud Run.
- `config.yaml`: Secure authentication and session management.

---

## 🚀 Local Setup & Deployment

### Prerequisites
- Python 3.12+
- `uv` (recommended) or `pip`

### 1. Installation
```bash
git clone https://github.com/YOUR_USERNAME/alia-legal-assistant.git
cd alia-legal-assistant
uv venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
uv pip install -r requirements.txt
```

### 2. Environment Variables
Copy the example environment file and fill in your API keys:
```bash
cp .env.example .env
```

### 3. Run Locally
```bash
uv run streamlit run app.py
```
The application will be available at `http://localhost:8501`.

### 4. Deploy to Google Cloud Run
The application is fully Dockerized and ready for serverless deployment:
```bash
gcloud run deploy alia-app \
    --source . \
    --region us-east4 \
    --allow-unauthenticated \
    --set-secrets="GEMINI_API_KEY=GEMINI_API_KEY:latest,LLM_API_KEY=LLM_API_KEY:latest,SPEECH_API_KEY=SPEECH_API_KEY:latest"
```
We deployed our fine-tuned **Gemma 4-E4B** on Cloud Run with **NVIDIA L4 GPUs**, leveraging **scale-to-zero** to ensure a production-ready yet cost-efficient architecture. This setup allows Alia to be highly responsive when needed while incurring zero costs during idle periods.

---

## 👥 Collaborators
- [Add Collaborator Name] - [Role/Contribution]
- **Julien Awon'ga** - Data Scientist

## 📦 Artefacts & Submission Links
- **Video Pitch**: [YouTube Link]
- **Gemma 4 Weights**: [[HuggingFace](https://huggingface.co/julienawonga/gemma-4-ivorian-labor-law-merged/)]
- **Public Repository**: [GitHub Link](https://github.com/julienawonga/alia-legal-ai)

*Built with ❤️ for the Gemma Impact Challenge.*
