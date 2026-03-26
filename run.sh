# run the agent for the first time
mmw-agent run \
  --problem-file example/MCM-2017-C/Problem.md \
  --data-dir example/MCM-2017-C \
  --output-dir outputs \
  --jupyter-host 0.0.0.0 \
  --jupyter-port 8888 \
  --no-token

# after the agent is stopped, you can resume it with the following command
mmw-agent resume \
  --task-id 20260325-165532-a339abdc \
  --output-dir outputs

# ai_tutor mode example
mmw-agent run \
  --mode ai_tutor \
  --problem-file example/ai_tutor/distributions.md \
  --data-dir example/ai_tutor \
  --output-dir outputs \
  --jupyter-host 0.0.0.0 \
  --jupyter-port 8888 \
  --no-token
