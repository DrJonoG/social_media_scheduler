from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import time
from typing import Optional, Tuple
import os

class GeminiAPI:
    def __init__(self, model="gemini-2.0-flash-exp", temperature: float = 0.7, top_k: int = 450, top_p: float = 0.7):
        # Load Gemini API key
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = model
        self.temperature = temperature
        self.top_k = top_k
        self.top_p = top_p
        self.last_error = None

    def get_model(self):
        return self.model

    def set_model(self, model):
        self.model = model

    def create_prompt(self, system_prompt: str, user_prompt: str) -> Tuple[str, str]:
        """
        Create a prompt in Gemini format
        
        Args:
            system_prompt: The system prompt
            user_prompt: The user prompt
            
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        return system_prompt, user_prompt

    def count_tokens(self, system_prompt: str, user_prompt: str) -> Optional[int]:
        """
        Estimate token count for Gemini API
        Note: This is a rough estimation since token counting may vary
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
        Send a prompt to the Gemini API

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

        try:
            start_time = time.time()
            
            # Configure the generation with temperature and other parameters
            generation_config = types.GenerateContentConfig(
                temperature=self.temperature,
                top_k=self.top_k,
                top_p=self.top_p,
                max_output_tokens=max_tokens,
                system_instruction=system_prompt
            )
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=generation_config
            )
            
            # Calculate elapsed time
            elapsed = time.time() - start_time
            elapsed_str = f"{elapsed:.1f}s"
            print(f"Elapsed: {elapsed_str}")

            return response.text

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
        Call a prompt with the Gemini API

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

    def generate_image(self, prompt, output_path, number_of_images=2, aspect_ratio="3:4"):
        """
        Generates an image using Google's Gemini API.

        Parameters:
        - prompt (str): The text prompt for image generation.
        - output_path (str): The file path to save the generated image.
        - number_of_images (int): The number of images to generate.
        - aspect_ratio (str): The aspect ratio of the image.
        """

        # See https://ai.google.dev/gemini-api/docs/image-generation

        if number_of_images > 4:
            number_of_images = 4
            print("==> Warning Number of images limited to 4.")

        if aspect_ratio not in ["1:1", "4:3", "3:4", "16:9", "9:16"]:
            print("==> Error Invalid aspect ratio. Please use '1:1', '4:3', '3:4', '16:9', or '9:16'.")
            return 

        print(f"==> Generating {number_of_images} images with aspect ratio {aspect_ratio}")
        response = self.client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images= number_of_images,
                aspect_ratio=aspect_ratio
            )
        )

        for i, generated_image in enumerate(response.generated_images):
            image = Image.open(BytesIO(generated_image.image.image_bytes))
            image.save(output_path.replace(".png", f"_{i}.png"))
            print(f"Image {i+1} saved to {output_path.replace('.png', f'_{i}.png')}")


