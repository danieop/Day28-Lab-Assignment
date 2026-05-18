# Kaggle Kernel For Lab 28

This folder is ready for `kaggle kernels push -p kaggle-lab28` after authentication.

Required Kaggle setup:

1. Enable Internet for the notebook.
2. Enable GPU accelerator.
3. Add Kaggle secret `NGROK_AUTHTOKEN` with your ngrok authtoken.
4. Replace `REPLACE_WITH_KAGGLE_USERNAME` in `kernel-metadata.json`.

After the notebook runs, copy the printed `VLLM_NGROK_URL` and `EMBED_NGROK_URL` into local `.env`.
