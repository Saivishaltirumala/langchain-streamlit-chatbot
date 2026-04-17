# Deploying the Streamlit QA Chatbot to Hugging Face Spaces (via GitHub Actions)

This guide documents the exact steps taken to successfully deploy our Streamlit application to a Hugging Face Space using Docker and automated via GitHub Actions.

## 1. Prepare Hugging Face Space Configuration (`README.md`)

When a Hugging Face Space starts, it looks for a `README.md` file at the root of the repository. This file must contain specific YAML "frontmatter" to tell Hugging Face what the Space should use. 

Ensure your `README.md` has the following block exactly at the top of the file:

```yaml
---
title: Langchain Streamlit Chatbot
emoji: 💬
colorFrom: blue
colorTo: indigo
sdk: docker
app_file: app.py
pinned: false
---
```

## 2. Prepare the Dockerfile

Because we used the `docker` SDK in our configuration, Hugging Face will build a Docker container to host our code. Streamlit defaults to port `8501`, **but Hugging Face Spaces default to expecting traffic on port `7860`**. 

We created a custom `Dockerfile` that ensures Streamlit binds to the `0.0.0.0` address on port `7860`:

```dockerfile
# Use the official Python image
FROM python:3.13.5-slim

# Set the working directory
WORKDIR /app

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install python packages
COPY requirements.txt ./
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

# Copy the application code
COPY app.py ./

# Expose the Hugging Face standard port
EXPOSE 7860

# Add a healthcheck to let Hugging Face know when the app has started
HEALTHCHECK CMD curl --fail http://localhost:7860/_stcore/health

# Run the Streamlit app on port 7860, binding to all network interfaces
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
```

## 3. Automate Deployments with GitHub Actions

Instead of pushing directly to Hugging Face manually, we configured GitHub Actions to automatically sync the Hugging Face Space whenever new code is pushed to our GitHub repository. 

Create a file at `.github/workflows/sync-to-hub.yml`:

```yaml
name: Sync to Hugging Face Hub

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  sync-to-hub:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0 
          lfs: true 

      - name: Push to Hugging Face Space
        env:
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
        run: |
          # The force push overrides any state present on the Space
          git push --force https://<YOUR_HF_USERNAME>:$HF_TOKEN@huggingface.co/spaces/<YOUR_HF_USERNAME>/<YOUR_SPACE_NAME> main
```
> **Note:** Make sure to replace `<YOUR_HF_USERNAME>` and `<YOUR_SPACE_NAME>` with your actual Hugging Face profile values.

## 4. Set GitHub Secrets

To allow the GitHub Action to authenticate and push to Hugging Face:
1. Go to your Hugging Face account **Settings** > **Access Tokens**.
2. Generate a token with `write` permissions.
3. In your GitHub Repository, navigate to **Settings** > **Secrets and variables** > **Actions**.
4. Create a **New repository secret** named `HF_TOKEN` and paste your Hugging Face token.

## 5. Configure Your Application Secrets on Hugging Face

Because this chatbot uses LLMs, you must configure the hidden API keys directly on Hugging Face.

1. Navigate to your Hugging Face Space settings.
2. Scroll to the **Variables and secrets** section.
3. Click **New secret** to add your hidden credentials defined in your `.env` file. For this project:
   - `GROQ_API_KEY`: `<your_groq_key>`
   - `LANGCHAIN_API_KEY`: `<your_langchain_key>`

> **Note:** You can also define public configuration variables as "Variables" instead of "Secrets" (for example, `LANGCHAIN_TRACING_V2` set to `true`).

## 6. Push and Deploy!

With the `README.md`, `Dockerfile`, and `.github/workflows/sync-to-hub.yml` committed to the repository, push the changes to GitHub. The GitHub action will automatically intercept that push, mirror it securely into your Hugging Face Space, and the Docker container will build and serve your app.
