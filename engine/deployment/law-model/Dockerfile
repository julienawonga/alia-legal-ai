FROM vllm/vllm-openai:latest

RUN pip install hf_transfer
ENV HF_HUB_ENABLE_HF_TRANSFER=1
ENV VLLM_ENABLE_CUDA_COMPATIBILITY=1

ENTRYPOINT []
CMD ["sh", "-c", "vllm serve $MODEL_ID --host 0.0.0.0 --port ${PORT:-8080} --max-model-len 32768 --gpu-memory-utilization 0.85 --enforce-eager --trust-remote-code --api-key $VLLM_API_KEY --dtype bfloat16 --served-model-name $SERVED_MODEL_NAME"]