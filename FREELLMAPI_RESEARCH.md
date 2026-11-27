# FreeLLMAPI: isolated research setup

The existing optional `LocalLLMClient` speaks the OpenAI-compatible chat protocol used by [FreeLLMAPI](https://github.com/tashfeenahmed/freellmapi). No new dependency is needed. The router is a separately installed, single-user research service; it does not provide provider accounts or keys, guarantee free capacity, or validate a model. Follow its installation instructions, configure your own eligible provider and obtain a router unified key. Provider terms and limits apply.

**Privacy:** a locally running router may forward each request and its context to an external provider, even if the router itself runs on the same machine. HomzDoctor prompts can contain patient queries and retrieved record content. Use only fictional, non-identifying test data. Do not send real patient or sensitive records, and do not use this integration for clinical decisions. Keep the router private, protect credentials and consult the provider's data handling terms. Do not expose its single-user dashboard publicly.

For an isolated research copy running on the same host as the router, after reviewing these boundaries, configure the backend process environment (store the key as a secret, never in Git):

```env
LOCAL_LLM_BASE_URL=http://127.0.0.1:3001/v1
LOCAL_LLM_MODEL=auto
LOCAL_LLM_API_KEY=<router-unified-key>
```

Leave these variables empty to keep the default offline behavior. `127.0.0.1` means the same host or network namespace as the backend; it will not reach a router on your own computer from a remote cloud or serverless deployment. Do not expose a router to the internet to work around that. Configuring an endpoint does not validate a model, turn the deployed UI's AI features on, or establish that a provider accepts the key. Check the model's returned identity and service errors in the isolated environment; use fictional prompts only. Rate limits and outages are expected.

Run the protocol checks from `backend/`:

```sh
python -m unittest discover -s tests -p 'test_freellmapi_compat.py' -v
```

These tests use a simulated local server only. Passing them establishes compatibility with the mocked OpenAI-style HTTP contract; it does **not** prove a live FreeLLMAPI instance, provider, key, model, or clinical performance is working.
