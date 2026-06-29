"""Fetch model catalog from HuggingFace API. No API key needed for listing."""
import json
import urllib.parse
import urllib.request

from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel

HF_API_BASE = "https://huggingface.co/api/models"

def fetch_gguf_models(trace: TraceEmitter, search: str = "", limit: int = 50) -> list[dict]:
    """Fetch GGUF models from the HuggingFace API and return them sorted by download count."""
    params = {
        "filter": "gguf",
        "sort": "downloads",
        "direction": "-1",
        "limit": str(limit),
    }
    if search:
        params["search"] = search

    url = f"{HF_API_BASE}?{urllib.parse.urlencode(params)}"
    trace.emit(component="hf_catalog", level=TraceLevel.INFO,
               message=f"Fetching GGUF models from HuggingFace: {url}")

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SovereignAI/0.1"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        models = []
        for m in data:
            model_id = m.get("id", "")
            publisher = model_id.split("/")[0] if "/" in model_id else "unknown"
            models.append({
                "id": model_id,
                "publisher": publisher,
                "name": model_id.split("/")[-1] if "/" in model_id else model_id,
                "downloads": m.get("downloads", 0),
                "likes": m.get("likes", 0),
                "tags": m.get("tags", []),
                "last_modified": m.get("lastModified", ""),
                "pipeline_tag": m.get("pipeline_tag", ""),
            })

        trace.emit(component="hf_catalog", level=TraceLevel.INFO,
                   message=f"Fetched {len(models)} GGUF models from HuggingFace")
        return models
    except Exception as exc:
        trace.emit(component="hf_catalog", level=TraceLevel.ERROR,
                   message=f"Failed to fetch HuggingFace catalog: {exc}")
        return []

def get_model_files(trace: TraceEmitter, model_id: str) -> list[dict]:
    """Get available GGUF files for a specific model (for quantization selection)."""
    url = f"https://huggingface.co/api/models/{model_id}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SovereignAI/0.1"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        siblings = data.get("siblings", [])
        gguf_files = []
        for s in siblings:
            fname = s.get("rfilename", "")
            if fname.endswith(".gguf"):
                # Parse quantization from filename (e.g., "model-Q4_K_M.gguf")
                quant = "unknown"
                quant_list = [
                    "Q4_K_M",
                    "Q4_K_S",
                    "Q5_K_M",
                    "Q5_K_S",
                    "Q6_K",
                    "Q8_0",
                    "Q3_K_M",
                    "Q3_K_S",
                    "Q2_K",
                    "F16",
                    "F32",
                ]
                for q in quant_list:
                    if q.lower() in fname.lower():
                        quant = q
                        break
                gguf_files.append({
                    "filename": fname,
                    "quantization": quant,
                    "download_url": f"https://huggingface.co/{model_id}/resolve/main/{fname}",
                })

        return gguf_files
    except Exception as exc:
        trace.emit(component="hf_catalog", level=TraceLevel.ERROR,
                   message=f"Failed to get files for {model_id}: {exc}")
        return []
