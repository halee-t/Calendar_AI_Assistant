import openai
import os


# YOUR API KEY HERE DELETE BEFORE PUSHING CODE
openai.api_key = 'x'

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,  # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


prompt = f"""
Hi, what's 10+10?
"""
response = get_completion(prompt)
print(response)