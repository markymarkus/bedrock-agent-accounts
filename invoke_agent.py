import logging
import boto3
from datetime import datetime
from botocore.exceptions import ClientError
import random

agent_id = "AGENT_ID_HERE"
agent_alias_id = "TSTALIASID"
session_id = ''.join(random.choices('0123456789', k=12))

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.ERROR)

agent_client = boto3.client('bedrock-agent-runtime')

def check_nested_structure(data):
    return data.get('trace', {}).get('trace', {}).get('orchestrationTrace', {}).get('modelInvocationOutput', {}).get('metadata', {}).get('usage', None) is not None

def invoke_agent_with_prompt(prompt):
    current_date = datetime.now().strftime("%Y-%m-%d")

    try:
        response = agent_client.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText=prompt,
            enableTrace=True,
            sessionState={
                "promptSessionAttributes": {
                 "CURRENT_DATE": current_date
                }
            },
        )

        completion = ""
        input_tokens = 0
        output_tokens = 0

        for event in response.get("completion", []):
            chunk = event.get("chunk", {})

            completion += chunk.get("bytes", b"").decode()

            if check_nested_structure(event):
                usage = event['trace']['trace']['orchestrationTrace']['modelInvocationOutput']['metadata']['usage']
                input_tokens += usage.get('inputTokens', 0)
                output_tokens += usage.get('outputTokens', 0)

        print(completion)
        print(f"input: {input_tokens}, output: {output_tokens}") # this is matching with cloudwatch metrics, so probably correct

    except ClientError as e:
        logger.error(f"Couldn't invoke agent. {e}")
        raise

def main():
    while True:
        prompt = input("Prompt (or 'exit') > ")
        if prompt.lower() == 'exit':
            print("Exiting...")
            break
        invoke_agent_with_prompt(prompt)

if __name__ == "__main__":
    main()
