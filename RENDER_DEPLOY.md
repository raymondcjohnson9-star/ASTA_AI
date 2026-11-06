# Deploy ASTA_AI backend on Render

This guide prepares the Python API for a test deployment. Creating this file does not create a Render service or start a deployment.

## What the service runs

- Runtime: Python
- Start command: `python brain/api_server.py`
- Health check: `/health`
- The API reads Render's `PORT` environment variable and binds to `0.0.0.0`.
- The Render Blueprint creates a random `ASTA_API_TOKEN` and has automatic deploys turned off.

## Deploy when ready

1. Sign in to Render and choose **New → Blueprint**.
2. Connect the GitHub repository `raymondcjohnson9-star/ASTA_AI`.
3. Select the repository's `main` branch and review the `render.yaml` settings.
4. Create the Blueprint/service when you are ready. The service will then build and deploy.
5. In the Render service dashboard, open its environment settings and securely view/copy the generated `ASTA_API_TOKEN`. Never add it to GitHub or share it in chat.
6. Copy the service's HTTPS URL and enter that URL and the token in ASTA's Android connection settings.

## AI model configuration

The deployment does not include or train a large language model. Without a configured provider, ASTA uses its existing local features. If you later choose a hosted model provider, add its provider name, base URL, model name, and API key as private Render environment variables. Provider API usage may cost money. Do not put API keys in repository files.

## Important limitations

- Render's free web services sleep after 15 minutes without inbound traffic and can take about a minute to wake.
- Free service files are ephemeral. ASTA's current JSON memory file may be lost after a restart, sleep, or redeploy. Do not rely on this deployment for permanent memory until persistent storage is implemented.
- This is an early single-instance prototype, not a production multi-user service. Do not send sensitive personal information.
- The API uses a bearer token. Keep it private and rotate it if exposed.
- Automatic Render deploys are disabled in the Blueprint. GitHub Actions workflows remain separate and manual-only.
