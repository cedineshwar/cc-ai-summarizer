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
    system_prompt = load_prompt('summarize_system_prompt.txt')
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


def chat_with_bulk_summaries(user_message: str, chat_history: list, summaries_context: str, model="gpt-4.1-nano-2025-04-14", temperature=0.7, max_tokens=500):
    """
    Chat with LLM about bulk summaries using chat prompts.
    
    Args:
        user_message: The user's question/message
        chat_history: List of previous messages in format [{"role": "user"/"assistant", "content": "..."}, ...]
        summaries_context: JSON string or formatted text of the summaries to analyze
        model: Model to use
        temperature: Temperature for response
        max_tokens: Max tokens in response
    
    Returns:
        Assistant response or None if error
    """
    # Load chat prompts
    system_prompt = load_prompt('chat_system_prompt.txt')
    user_prompt_template = load_prompt('chat_user_prompt.txt')
    guardrail_prompt = load_prompt('chat_guardrail_prompt.txt')
    
    if not system_prompt or not user_prompt_template or not guardrail_prompt:
        logger.error("Could not load required chat prompt files")
        return None
    
    # Replace placeholder in user prompt with actual summaries
    user_prompt = user_prompt_template.replace('{{PASTE ENTIRE SUMMARY HERE}}', summaries_context)
    
    # Prepare the full system prompt with guardrail
    full_system_prompt = f"{system_prompt}\n\n{guardrail_prompt}"
    
    # Prepare messages for API call - include chat history
    messages = chat_history.copy() if chat_history else []
    messages.append({"role": "user", "content": f"{user_prompt}\n\nUser Query: {user_message}"})
    
    try:
        logger.debug(f"Chat model: {model} | Temperature: {temperature} | Max tokens: {max_tokens}")
        logger.debug(f"Chat history messages: {len(messages)}")
        
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": full_system_prompt}
            ] + messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        assistant_message = response.choices[0].message.content.strip()
        logger.info(f"Successfully generated chat response ({len(assistant_message)} characters)")
        
        return assistant_message
    
    except Exception as e:
        logger.error(f"An error occurred during chat: {e}", exc_info=True)
        return None

