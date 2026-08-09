# Changes for Claude

## Problem Context
The pipeline was failing at the LLM stage when attempting to run the search grounding ablation. The failure was caused by the `_get_search_grounded_findings` function in `scripts/remediation/llm_reasoner.py`.

The author attempted to bypass a `429 RESOURCE_EXHAUSTED` billing error on the `google_search` tool by using the internal `client.interactions.create()` SDK surface, which was observed working in AI Studio's web UI. However, this undocumented endpoint has strict Pydantic validation schemas. When the SDK unpacked `model`, `input`, and `tools` into a generic JSON body, Pydantic threw a fatal `ValidationError` and the call crashed. 

When this crashed, the pipeline fell back to the empty fallback string and proceeded to the structured LLM call. The structured call likely also crashed due to RPM (Requests Per Minute) rate-limiting when running scenarios in parallel, ultimately resulting in a `sys.exit(1)` and failing the entire pipeline.

## Solution Implemented
1. **SDK Usage Correction:** Replaced the broken `client.interactions.create()` workaround with the officially supported `client.models.generate_content()` method from the `google-genai` SDK.
2. **Proper Configuration:** Imported `google.genai.types` to correctly configure the `google_search` tool via the `GenerateContentConfig` object, matching the SDK's documented requirements.
3. **Model String Format:** Passed `model_name` directly instead of prepending `models/`, as the new SDK handles the `models/` routing prefix internally.

## Note on Billing and 429 Errors
If the `google_search` tool still throws a 429 "check your plan and billing details" error across all fallback models, this confirms that Google strictly requires a paid-tier API key (billing enabled) to use the Search Grounding tool via the public API. If so, the script will catch the 429s, log warnings, use the empty fallback string, and successfully proceed to the structured LLM call without crashing the pipeline.
