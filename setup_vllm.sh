# mistralai/Mistral-Nemo-Instruct-FP8-2407
# Qwen/Qwen2.5-14B-Instruct

########################## vLLM 실행 ######################################################
# 터미널 초기화시 실행
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:${LD_LIBRARY_PATH:-}"
unset LD_PRELOAD
python -m vllm.entrypoints.openai.api_server \
  --host 127.0.0.1 \
  --port 8000 \
  --model mistralai/Mistral-Nemo-Instruct-FP8-2407 \
  --max-model-len 28672 \
  --gpu-memory-utilization 0.90 \
  --swap-space 32