import anthropic
import time
from typing import Optional, Tuple

class AnthropicAPI:
    def __init__(self, model: str = None, temperature: float = 0.7, top_k: int = 450, top_p: float = 0.7):
        self.client = anthropic.Anthropic()
        self.model = model
        self.temperature = temperature
        self.top_k = top_k
        self.top_p = top_p
        self.last_error = None

    def get_model(self):
        return self.model

    def set_model(self, model: str):
        self.model = model

    def create_prompt(self, system_prompt: str, user_prompt: str) -> Tuple[str, list]:
        system_prompt = system_prompt
        user_message = [{"role": "user",
            "content": [{"type": "text", "text": user_prompt}]
        }]

        return system_prompt, user_message

    def count_tokens(self, system_prompt: str, user_prompt: str) -> Optional[int]:
        system_prompt, messages = self.create_prompt(system_prompt, user_prompt)
        try:
            response = self.client.messages.count_tokens(
                messages=messages,
                model=self.model,
                system=system_prompt
            )
            return response.input_tokens
        except Exception as e:
            print(f"Error counting tokens: {e}")
            return None
        

    def send_prompt(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        max_tokens: int,
        thinking_mode: bool = False
    ) -> Optional[str]:
        """
        Send a prompt to the Anthropic API

        Args:
            system_prompt: The system prompt
            user_prompt: The user prompt
            model: The model to use
            max_tokens: The maximum number of tokens to use

        Returns:
            The result of the prompt
        """ 
        # Only request verification if the tokens are high
        tokens = self.count_tokens(system_prompt, user_prompt)
        if thinking_mode == True:
            print(f"Sending prompt with model: {self.model}, Thinking mode. Tokens: ~{tokens}. ")
        else:
            print(f"Sending prompt with model: {self.model}. Tokens: ~{tokens}")

        system_prompt, messages = self.create_prompt(system_prompt, user_prompt)

        try:
            content = []
            
            # Set parameters based on thinking mode
            if thinking_mode:
                temperature = 1
                top_p = 0.95
                thinking_config = {
                    "type": "enabled",
                    "budget_tokens": 10000
                }
            else:
                temperature = self.temperature
                top_p = self.top_p
                thinking_config = None
            
            stream_params = {
                "model": self.model,
                "max_tokens": max_tokens,
                "system": system_prompt,
                "temperature": temperature,
                "top_p": top_p,
                "messages": messages
            }
            
            if thinking_config:
                stream_params["thinking"] = thinking_config
            
            elapsed_str = ""
            with self.client.messages.stream(**stream_params) as stream:
                start_time = time.time()
                for text in stream.text_stream:
                    content.append(text)
                    # Calculate time taken
                    elapsed = time.time() - start_time
                    elapsed_str = f"{elapsed:.1f}s"
                    print(f"Elapsed: {elapsed_str}", end="\r", flush=True)
                # Print final elapsed time
                print(f"Elapsed: {elapsed_str}")

            final_message = stream.get_final_message()

            # Join all content first and save it
            full_content = ''.join(content)

            return full_content
        except Exception as e:
            self.last_error = e  # Store the original error
            print(f"Error processing prompt: {e}")
            return None


    def call_prompt(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 64000,
        thinking_mode: bool = False
    ):
        """
        Call a prompt with the Anthropic API

        Args:
            processor: The AnthropicAPI instance
            system_prompt: The system prompt
            user_prompt: The user prompt
            max_tokens: The maximum number of tokens to use

        Returns:
            The result of the prompt
        """

        result = self.send_prompt(system_prompt, user_prompt, max_tokens, thinking_mode)
        if not result:
            print("Error: No result from prompt")
            return None  # Return None instead of nothing


        return result


