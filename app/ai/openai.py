import requests
import base64
import time
from typing import Optional, Tuple

class OpenAIAPI:
    def __init__(self, api_key, model: str = "gpt-4", temperature: float = 0.7, top_p: float = 0.7):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.last_error = None
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def get_model(self):
        return self.model

    def set_model(self, model: str):
        self.model = model

    def create_prompt(self, system_prompt: str, user_prompt: str) -> Tuple[str, list]:
        """
        Create a prompt in OpenAI format
        
        Args:
            system_prompt: The system prompt
            user_prompt: The user prompt
            
        Returns:
            Tuple of (system_prompt, messages) where messages is the OpenAI format
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return system_prompt, messages

    def count_tokens(self, system_prompt: str, user_prompt: str) -> Optional[int]:
        """
        Estimate token count for OpenAI API
        Note: This is a rough estimation since OpenAI doesn't provide a direct count API
        """
        try:
            # Rough estimation: ~4 characters per token
            total_text = system_prompt + user_prompt
            estimated_tokens = len(total_text) // 4
            return estimated_tokens
        except Exception as e:
            print(f"Error estimating tokens: {e}")
            return None

    def send_prompt(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        max_tokens: int
    ) -> Optional[str]:
        """
        Send a prompt to the OpenAI API

        Args:
            system_prompt: The system prompt
            user_prompt: The user prompt
            max_tokens: The maximum number of tokens to use

        Returns:
            The result of the prompt
        """ 
        # Only request verification if the tokens are high
        tokens = self.count_tokens(system_prompt, user_prompt)
        print(f"Sending prompt with model: {self.model}. Tokens: ~{tokens}")

        system_prompt, messages = self.create_prompt(system_prompt, user_prompt)

        try:
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "stream": True
            }

            start_time = time.time()
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=self.headers,
                json=data,
                stream=True
            )

            if response.status_code != 200:
                print(f"API request failed: {response.status_code} {response.text}")
                return None

            content = []
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        line = line[6:]  # Remove 'data: ' prefix
                        if line.strip() == '[DONE]':
                            break
                        try:
                            import json
                            chunk = json.loads(line)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    content.append(delta['content'])
                                    # Calculate time taken
                                    elapsed = time.time() - start_time
                                    elapsed_str = f"{elapsed:.1f}s"
                                    print(f"Elapsed: {elapsed_str}", end="\r", flush=True)
                        except json.JSONDecodeError:
                            continue

            # Print final elapsed time
            elapsed = time.time() - start_time
            elapsed_str = f"{elapsed:.1f}s"
            print(f"Elapsed: {elapsed_str}")

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
        max_tokens: int = 100000
    ):
        """
        Call a prompt with the OpenAI API

        Args:
            system_prompt: The system prompt
            user_prompt: The user prompt
            max_tokens: The maximum number of tokens to use

        Returns:
            The result of the prompt
        """

        result = self.send_prompt(system_prompt, user_prompt, max_tokens)
        if not result:
            print("Error: No result from prompt")
            return None  # Return None instead of nothing

        return result

    def estimate_image_cost(self, data):
        """
        Estimate the cost of image generation based on model, size, quality, and quantity.
        """

        model = data.get("model", "gpt-image-1")
        size = data.get("size", "1024x1024")
        n = data.get("n", 1)
        quality = data.get("quality", "standard").lower()  # Default to 'standard' if not specified

        # Pricing for gpt-image-1
        gpt_image_1_prices = {
            "low": {
                "1024x1024": 0.011,
                "1024x1536": 0.016,
                "1536x1024": 0.016,
            },
            "medium": {
                "1024x1024": 0.042,
                "1024x1536": 0.063,
                "1536x1024": 0.063,
            },
            "high": {
                "1024x1024": 0.167,
                "1024x1536": 0.250,
                "1536x1024": 0.250,
            }
        }

        # Pricing for DALL·E 2
        dall_e_2_prices = {
            "256x256": 0.016,
            "512x512": 0.018,
            "1024x1024": 0.020,
        }

        # Pricing for DALL·E 3
        dall_e_3_prices = {
            "standard": {
                "1024x1024": 0.040,
                "1024x1792": 0.080,
                "1792x1024": 0.080,
            },
            "hd": {
                "1024x1024": 0.080,
                "1024x1792": 0.120,
                "1792x1024": 0.120,
            }
        }

        if model == "gpt-image-1":
            cost_per_image = gpt_image_1_prices.get(quality, {}).get(size)
        elif model == "dall-e-2":
            cost_per_image = dall_e_2_prices.get(size)
        elif model == "dall-e-3":
            cost_per_image = dall_e_3_prices.get(quality, {}).get(size)
        else:
            raise ValueError(f"Unsupported model '{model}'.")

        if cost_per_image is None:
            raise ValueError(f"Unsupported size '{size}' for model '{model}' with quality '{quality}'.")

        total_cost = cost_per_image * n
        return round(total_cost, 4)

    def generate_image(self, prompt, model, output_path, quality, size):
        ''' 
        Notes:
        The size of the generated images must be one of:
        - 1024x1024, 1536x1024 (landscape), 1024x1536 (portrait), or auto (default value) for gpt-image-1, 
        - 256x256, 512x512, or 1024x1024 for dall-e-2, 
        - 1024x1024, 1792x1024, or 1024x1792 for dall-e-3
        '''

        # Validate model and size
        if model not in ["gpt-image-1", "dall-e-2", "dall-e-3"]:
            raise ValueError(f"Unsupported model '{model}'.")

        if size not in ["1024x1024", "1536x1024", "1024x1536", "256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"]:
            raise ValueError(f"Unsupported size '{size}'.")

        data = {
            "model": model,
            "prompt": prompt,
            "n": 1,
            "quality": quality,
            "size": size,
            "response_format": "b64_json"
        }

        estimated_cost = self.estimate_image_cost(data)
        print(f"Estimated cost: {estimated_cost}")
       
        response = requests.post("https://api.openai.com/v1/images/generations", headers=self.headers, json=data)
        response_json = response.json()

        if response.status_code == 200 and 'data' in response_json:
            try:
                b64_image = response_json['data'][0]['b64_json']
                image_data = base64.b64decode(b64_image)
                with open(output_path, "wb") as f:
                    f.write(image_data)
                print("Image saved successfully.")
            except (KeyError, IndexError, base64.binascii.Error) as e:
                print("Failed to decode and save image:", e)
        else:
            print("Request failed:", response.status_code, response.text)

