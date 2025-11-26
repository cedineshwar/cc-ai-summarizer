from src.summarizer import summarize_call

def test_empty():
    assert summarize_call('') == ''

def test_basic():
    transcript = "Short sentence. This is a longer sentence that should rank higher. Small."
    summary = summarize_call(transcript, max_sentences=1)
    assert "This is a longer sentence" in summary
