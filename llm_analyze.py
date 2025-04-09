from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
import torch

# NOT BEING USED ACCURACY IS REALLY BAD

MODEL = None
TOKENIZER = None
DEVICE = None

def load_model():
    global MODEL, TOKENIZER, DEVICE

    DEVICE = torch.device("cuda" if torch.cuda.is_available() else 
                          "mps" if torch.backends.mps.is_available() else 
                          "cpu")

    print(f"Using device: {DEVICE}")

    TOKENIZER = AutoTokenizer.from_pretrained("bigcode/starcoder2-3b")

    MODEL = AutoModelForCausalLM.from_pretrained(
        "bigcode/starcoder2-3b",
        low_cpu_mem_usage=True,  # Reduce memory usage
        torch_dtype=torch.float16 if DEVICE != torch.device('cpu') else torch.float32
    ).to(DEVICE)

def LLMAnalysis(html_content):
    global MODEL, TOKENIZER, DEVICE
    
    if MODEL is None or TOKENIZER is None or DEVICE is None:
        load_model()
    
    sample_content = html_content[:500]
    
    prompt = f"Answer strictly with 'No' or 'Yes': Does the following HTML content contain code?: <html> def main: \n print('hello world') </html>"
    
    inputs = TOKENIZER(prompt, return_tensors="pt", truncation=True, max_length=1024)
    input_ids = inputs["input_ids"].to(DEVICE)
    attention_mask = inputs["attention_mask"].to(DEVICE)
        
    with torch.no_grad():
        output_tensor = MODEL.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=10,
            do_sample=False
        )
        

    decoded_text = TOKENIZER.decode(output_tensor[0], skip_special_tokens=True)
    
    input_decoded = TOKENIZER.decode(inputs.input_ids[0], skip_special_tokens=True)


    if len(decoded_text) > len(input_decoded):
        response = decoded_text[len(input_decoded):].strip()
    else:
        response = "No response generated"

    print(f"Extracted response: {response}")

    has_code = any(word in response.lower() for word in ["yes", "true", "code"])
    
    return {
        "has_code": has_code,
        "model_response": response
    }

