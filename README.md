# design_pitch
This repo leverages local SLMs to help create branding pitch documents that can be shared with stakeholders. 

## Run with Docker

Needs Docker and [Ollama](https://ollama.com) on the host, with a model pulled (a vision model for image critique).

```sh
# tests (no model needed)
docker build --target test -t pitchy-test . && docker run --rm pitchy-test

# app: web UI at http://localhost:8000
docker build -t pitchy .
docker run --rm -p 8000:8000 \
  -e PITCHY_MODEL=ollama_chat/<your-model> \
  -v "$PWD/output:/app/agents/pitchy/output" \
  pitchy
```

- Linux hosts also need `--add-host=host.docker.internal:host-gateway`, or set `-e OLLAMA_API_BASE=http://<host-ip>:11434`.
- Ollama must accept connections from the container (`OLLAMA_HOST=0.0.0.0` if it only listens on localhost).
- PDFs are written to `./output` on the host through the volume.
