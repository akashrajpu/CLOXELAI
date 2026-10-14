import ollama
import random

MODEL_NAME = 'qwen:0.5b'

def generate_daily_script(topic: str, duration: int) -> str:
    """
    Generates a new, unique video script for the given topic using local Ollama.
    """
    angles = [
        f"Give me 3 amazing facts about {topic}.",
        f"What is the history behind {topic}? Explain it simply.",
        f"What are the top 3 secrets no one tells you about {topic}?",
        f"Explain {topic} as if I am 5 years old.",
        f"Why is {topic} so popular right now?",
        f"What are the pros and cons of {topic}?",
        f"Tell a short, engaging story related to {topic}."
    ]
    
    selected_angle = random.choice(angles)
    
    word_count = int(duration * 2.5)
    
    system_prompt = (
        "You are an AI that ONLY outputs spoken video scripts. NO conversational filler, NO \"Here is your script:\", NO intro text. "
        f"Write an engaging video script about {word_count} words long. "
        "Do not include visual cues, camera directions, or any brackets. "
        "START DIRECTLY with the first word of the script."
    )
    
    try:
        response = ollama.chat(model=MODEL_NAME, messages=[
            {
                'role': 'system',
                'content': system_prompt
            },
            {
                'role': 'user',
                'content': selected_angle
            }
        ])
        
        script = response['message']['content'].strip()
        if not script:
            return f"Welcome to today's video about {topic}. Did you know that {topic} is absolutely amazing? Stay tuned for more!"
            
        return script
    except Exception as e:
        print(f"❌ Ollama Error: {e}")
        return f"Today, we are talking about {topic}. There is always something new to learn about {topic}. Subscribe for more!"

if __name__ == "__main__":
    print("Testing script generation...")
    print(generate_daily_script("Artificial Intelligence"))
