import openai
import os
from src.logger import logger

def load_prompt(prompt_file):
    """Load prompt text from a file in the prompt_store folder."""
    prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompt_store', prompt_file)
    try:
        with open(prompt_path, 'r') as f:
            content = f.read().strip()
            logger.debug(f"Loaded prompt file: {prompt_file}")
            return content
    except FileNotFoundError:
        logger.error(f"Prompt file not found: {prompt_path}")
        return None

def summarize_call(transcript, model="gpt-4.1-nano-2025-04-14", max_sentences=3, temperature=0.7, max_tokens=150):
    # Load prompts from files
    system_prompt = load_prompt('system_prompt.txt')
    user_prompt_template = load_prompt('summarize_user_prompt.txt')
    guardrail_prompt = load_prompt('summarize_guardrail_prompt.txt')
    
    if not system_prompt or not user_prompt_template or not guardrail_prompt:
        logger.error("Could not load required prompt files")
        return None
    
    # Replace placeholder with actual transcript
    user_prompt = user_prompt_template.replace('{{PASTE TRANSCRIPT HERE}}', transcript)

    user_prompt = user_prompt.replace('{{max_summary_length}}', str(max_sentences))

    logger.debug(f"User prompt after replacing the strings:  {user_prompt}")

    # Combine guardrail prompt with system prompt for additional context
    full_system_prompt = f"{system_prompt}\n\n{guardrail_prompt}"
    
    try:
        # DEBUG logging
        logger.debug(f"Model used: {model} | Temperature: {temperature} | Max tokens: {max_tokens} | Max sentences: {max_sentences}")
        logger.debug(f"Transcript length: {len(transcript)} characters")
       
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": full_system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )

        summary = response.choices[0].message.content.strip()
        logger.info(f"Successfully generated summary ({len(summary)} characters)")
        
        return summary
    
    except Exception as e:
        logger.error(f"An error occurred during summarization: {e}", exc_info=True)
        return None
