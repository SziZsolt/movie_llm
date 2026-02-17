from Retrieval import Retrieval
from transformers import AutoModelForCausalLM, AutoTokenizer

class MovieModel():
    def __init__(self, retrieval: Retrieval, model_name: str):
        self.__retrieval = retrieval
        self._model_name = model_name
        self.__tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.__model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")

    def generate_answer(self, input: str, max_new_tokens: int = 300) -> dict:
        try:
            context = self.__retrieval.process_input(input)
        except Exception as e:
            context = f"Error during retrieval: {str(e)}"
        try:
            prompt = f"""
                You are a helpful movie assistant.
                Use the provided data to answer naturally.

                Context:
                {context}

                User question:
                {input}
            """
            inputs = self.__tokenizer(prompt, return_tensors="pt").to(self.__model.device)
            outputs = self.__model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
            )
            generated_text = self.__tokenizer.decode(outputs[0], skip_special_tokens=True)
            return generated_text
        except Exception as e:
            return f"Error during answer generation: {str(e)}"



    