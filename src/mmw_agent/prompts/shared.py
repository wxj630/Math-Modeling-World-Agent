def get_reflection_prompt(error_message: str, code: str) -> str:
    return f"""The code execution encountered an error:
{error_message}

Please analyze the error, identify the cause, and provide a corrected version of the code.
Consider:
1. Syntax errors
2. Missing imports
3. Incorrect variable names or types
4. File path issues
5. Any other potential issues
6. If a task repeatedly fails to complete, try breaking down the code, changing your approach, or simplifying the model. If you still can't do it, I'll \"chop\" you and cut your power.
7. Don't ask user what to do next, just do it by yourself.

Previous code:
{code}

Please provide an explanation of what went wrong and remember to call tools to retry.
"""


def get_completion_check_prompt(prompt: str, text_to_gpt: str) -> str:
    return f"""
Please analyze the current state and determine if the task is fully completed:

Original task: {prompt}

Latest execution results:
{text_to_gpt}

Consider:
1. Have all required data processing steps been completed?
2. Have all necessary files been saved?
3. Are there any remaining steps needed?
4. Is the output satisfactory and complete?
5. If a task repeatedly cannot complete, change approach to avoid endless loops.
6. Try to finish within fewer chat turns.
7. If complete, provide a short summary and don't call tools.
8. If not complete, rethink and call tools.
9. Don't ask user what to do next, do it by yourself.
10. Have a good visualization?
"""
