import gradio as gr
from peft import PeftModel

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TextIteratorStreamer,
    pipeline,
)
from threading import Thread

# The huggingface model id for Microsoft's phi-2 model
base_model_id = "microsoft/phi-2"

# Download and load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(
    base_model_id,
    add_bos_token=True,
    trust_remote_code=True,
    use_fast=False
)
tokenizer.pad_token = tokenizer.eos_token

base_model = AutoModelForCausalLM.from_pretrained(
    base_model_id,
    device_map="auto",
    trust_remote_code=True,
    load_in_8bit=True,
    torch_dtype=torch.float16,
)
model = PeftModel.from_pretrained(base_model, "./training/checkpoint-100")

# Text generation pipeline
phi2 = pipeline(
    "text-generation",
    tokenizer=tokenizer,
    model=model,
    pad_token_id=tokenizer.eos_token_id,
    eos_token_id=tokenizer.eos_token_id,
    device_map="cpu",
)

# Function that accepts a prompt and generates text using the phi2 pipeline
def generate(message, chat_history):
    max_new_tokens = 64
    instruction = "You answers questions from 'User' about Washington and Lee University."
    final_prompt = f"Instruction: {instruction}\n"

    for sent, received in chat_history:
        final_prompt += "User: " + sent + "\n"
        final_prompt += "Assistant: " + received + "\n"

    final_prompt += "User: " + message + "\n"
    final_prompt += "Output:"

    if (
        len(tokenizer.tokenize(final_prompt))
        >= tokenizer.model_max_length - max_new_tokens
    ):
        final_prompt = "Instruction: Say 'Input exceeded context size, please clear the chat history and retry!' Output:"

    # Streamer
    streamer = TextIteratorStreamer(
        tokenizer=tokenizer, skip_prompt=True, skip_special_tokens=True, timeout=300.0
    )
    thread = Thread(
        target=phi2,
        kwargs={
            "text_inputs": final_prompt,
            "max_new_tokens": max_new_tokens,
            "streamer": streamer,
        },
    )
    thread.start()

    generated_text = ""
    for word in streamer:
        generated_text += word
        response = generated_text.strip()

        if "User:" in response:
            response = response.split("User:")[0].strip()

        if "Assistant:" in response:
            response = response.split("Assistant:")[1].strip()

        yield response


# Chat interface with gradio
with gr.Blocks() as demo:
    gr.Markdown(
        """
        # W&L Chatbot Using Phi-2 and QLoRA
        This chatbot was created using Microsoft's 2.7 billion parameter [Phi-2](https://huggingface.co/microsoft/phi-2) Transformer model. It has been tuned with QLoRA to answer questions about Washington and Lee University.
        
        Created by Malachi Eberly, Bennett Ehret, Micah Tongen, Barrett Bourgeois, and Armando Mendez
        """
    )

    chatbot = gr.ChatInterface(
        fn=generate,
        stop_btn=None,
        examples=[["What is Washington and Lee University?"], ["What majors are offered at W&L?"], ["What courses should a First-Year take?"], ["How many students attend W&L?"], ["What athletic teams are available?"]]
    )

demo.queue().launch()
