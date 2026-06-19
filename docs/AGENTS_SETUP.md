# HomzDoctor AI Agents — Setup & API Keys

This project ships **two Hugging Face–powered agents**:

| Agent | File | What it does | Model type |
|-------|------|--------------|------------|
| **LVLM Diagnostic** | `backend/agents/lvlm_agent.py` | Reads X-ray / CT / MRI images and lab PDFs, runs **diagnose → recheck → finalise**, always flags result for doctor review | Large Vision-Language Model (LVLM) |
| **LLM Pharmacy** | `backend/agents/pharmacy_agent.py` | Searches nearby pharmacies (ranked by distance) and drives the prescription **ordering** procedure | Text LLM |

> ⚠️ **Safety:** Both agents are *decision support only*. The LVLM result always returns `doctor_review_required: true`; the pharmacy agent refuses to order unless the prescription is **doctor-approved** and **patient-confirmed**.

---

## 1. The only key you NEED: a Hugging Face token

Both agents call the Hugging Face Inference API, which needs one token.

**Where to get it**
1. Create / log in to an account at <https://huggingface.co>.
2. Go to **Settings → Access Tokens**: <https://huggingface.co/settings/tokens>
3. Click **New token**, give it a name (e.g. `homzdoctor`), role **Read** is enough.
4. Copy the token (looks like `hf_xxxxxxxxxxxxxxxxxxxx`).

**Where to put it**
Edit `backend/.env` (copy from `backend/.env.example` if you haven't yet):

```env
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx
HF_MODEL=Qwen/Qwen3-4B-Instruct
HF_VLM_MODEL=Qwen/Qwen2.5-VL-7B-Instruct
HF_VLM_PROVIDER=
HF_TIMEOUT=120
```

> The token is read by `services/hf_llm_service.py` (text) and `services/hf_vision_service.py` (vision). `backend/.env` is git-ignored — **never commit your token.**

**Billing note:** HF serverless inference has a small free monthly credit; heavy/vision usage needs a **PRO** account or a paid inference provider. See <https://huggingface.co/docs/inference-providers>.

---

## 2. Choosing the models

### Text model (`HF_MODEL`) — pharmacy + patient chat
Default `Qwen/Qwen3-4B-Instruct` works out of the box. Any instruct chat model on HF inference works (e.g. `meta-llama/Llama-3.1-8B-Instruct`).

### Vision model (`HF_VLM_MODEL`) — imaging/lab diagnosis
Default `Qwen/Qwen2.5-VL-7B-Instruct` (general open VLM, no special access).

For a **medical-tuned** model, use MedGemma (matches the README vision):
1. Open <https://huggingface.co/google/medgemma-4b-it> and click **Agree / request access** (it's gated).
2. Once granted, set `HF_VLM_MODEL=google/medgemma-4b-it` in `.env`.
3. Make sure your `HF_TOKEN` belongs to the approved account.

If a model isn't served by the default provider, set `HF_VLM_PROVIDER` (e.g. `nebius`, `together`, `hf-inference`).

---

## 3. Optional key: Google Maps / Places (live pharmacy search)

Without this key the pharmacy agent ranks the pharmacies **already in your database** by real distance — fully functional for the demo. Add the key only if you want **live** nearby-pharmacy lookup from Google.

**Where to get it**
1. Go to <https://console.cloud.google.com/> and create / pick a project.
2. **APIs & Services → Library → enable "Places API"** (and "Maps JavaScript API" if you map on the frontend).
3. **APIs & Services → Credentials → Create credentials → API key.**
4. Restrict the key (recommended): by API = Places, and by IP/referrer.

**Where to put it**
```env
GOOGLE_MAPS_API_KEY=AIzaSy...your_key...
```
Read by `backend/agents/pharmacy_agent.py`. Billing must be enabled on the Google project (Places has a monthly free tier).

---

## 4. Install dependencies

```bash
cd backend
pip install -r requirements.txt   # adds pillow + pymupdf for image/PDF reading
```

`pymupdf` reads lab-report PDFs; `pillow` normalises images. If they're missing the agent still runs but PDF support is disabled.

---

## 5. Try it

Start the backend (`uvicorn main:app --reload`) and log in to get a JWT, then:

**Diagnose an image / lab PDF** (`POST /api/v1/ai/diagnose`, multipart):
```bash
curl -X POST http://localhost:8000/api/v1/ai/diagnose \
  -H "Authorization: Bearer <JWT>" \
  -F "file=@chest_xray.jpg" \
  -F "modality=xray"
```
Returns `draft_diagnosis`, `recheck`, `final_diagnosis`, `confidence`, and `doctor_review_required: true`.

**Search nearby pharmacies** (`GET /api/v1/pharmacies/search?lat=..&lon=..&radius_km=5`).

**Order a prescription** (`POST /api/v1/pharmacies/{pharmacy_id}/order`):
```json
{ "prescription_id": 1, "patient_confirmed": true }
```
First call it with `patient_confirmed: false` to get an `order_preview`, then confirm.

---

## Summary: what goes in `.env`

| Variable | Required? | From where |
|----------|-----------|------------|
| `HF_TOKEN` | ✅ yes | huggingface.co/settings/tokens |
| `HF_MODEL` | optional (has default) | any HF text model id |
| `HF_VLM_MODEL` | optional (has default) | any HF vision model id (MedGemma = gated) |
| `HF_VLM_PROVIDER` | optional | HF inference provider name |
| `GOOGLE_MAPS_API_KEY` | optional | console.cloud.google.com (Places API) |
