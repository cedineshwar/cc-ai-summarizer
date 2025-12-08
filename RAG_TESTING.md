# RAG Implementation Testing Guide

## Test Checklist

Use this guide to verify all RAG functionality works correctly.

---

## 1. Setup & Initialization Tests

### Test 1.1: Vector Store Creation
**Objective:** Verify vector store is created on first RAG access

**Steps:**
1. Go to View Summaries page
2. Click RAG-Based Chat tab
3. Wait for initialization (should see "Initializing RAG Chatbot and vector store...")
4. Watch for success message: "✅ RAG Chatbot initialized successfully!"

**Expected Result:**
- ✅ Vector store is created in `/output_data/vector_store/`
- ✅ Success message appears
- ✅ Vector store files exist on disk
- ✅ Subsequent tab switches don't reinitialize

**Failure Indicators:**
- ❌ Error message appears
- ❌ No vector store files created
- ❌ Timeout during initialization

---

### Test 1.2: API Key Validation
**Objective:** Verify API key requirement is enforced

**Steps:**
1. Clear API key in main app (set to empty or invalid)
2. Go to View Summaries
3. Click RAG-Based Chat tab
4. Observe the message

**Expected Result:**
- ✅ Warning message: "Please enter your OpenAI API key in the main app page first!"
- ✅ No attempt to initialize without valid key
- ✅ Chat input is disabled

**Failure Indicators:**
- ❌ Initialization attempts without key
- ❌ No warning message
- ❌ Confusing error messages

---

## 2. Vector Store Tests

### Test 2.1: Document Preparation
**Objective:** Verify summaries are properly converted to documents

**Steps:**
1. Check logs for vector store creation
2. Look for: "Prepared X documents for vector store"
3. Verify all 5 summaries appear in logs

**Expected Output in Logs:**
```
Loaded 5 summaries from output_data/bulk_summaries.json
Prepared 5 documents for vector store
Creating FAISS vector store with 5 documents...
Vector store saved to output_data/vector_store
Vector store loaded successfully
```

**Expected Result:**
- ✅ All 5 summaries loaded
- ✅ All 5 documents prepared
- ✅ No data loss during conversion
- ✅ Metadata preserved

---

### Test 2.2: Persistence
**Objective:** Verify vector store is saved and reused

**Steps:**
1. First RAG chat access - vector store created
2. Switch to Standard Chat tab
3. Switch back to RAG Chat tab
4. Check logs for load vs create message

**Expected Result:**
- ✅ First access: "Creating FAISS vector store..."
- ✅ Second access: "Loading existing vector store from..."
- ✅ No re-creation on tab switch
- ✅ Instant load on second access

**Performance:**
- ⏱️ First creation: 5-10 seconds
- ⏱️ Subsequent loads: <1 second

---

### Test 2.3: Vector Store Reload
**Objective:** Verify reload functionality picks up new summaries

**Steps:**
1. Click "🔄 Reload Vector Store" button
2. Watch for spinner
3. Wait for completion

**Expected Result:**
- ✅ Spinner appears during reload
- ✅ Vector store is force-recreated
- ✅ Success message appears
- ✅ Subsequent queries use updated index

**Logs Should Show:**
```
Reloading vector store...
Creating FAISS vector store with N documents...
```

---

## 3. Similarity Search Tests

### Test 3.1: Basic Query
**Objective:** Verify vector similarity search works

**Steps:**
1. Type question: "Which agents have the highest scores?"
2. Send query
3. Check RAG response

**Expected Result:**
- ✅ Response received within 2-4 seconds
- ✅ Response mentions specific agent names
- ✅ Includes actual agent scores from summaries
- ✅ References specific call IDs

**Example Response Should Include:**
```
Sarah Mitchell (AG-2847): 95/100
Marcus Johnson (AG-2951): 85/100
...
```

---

### Test 3.2: Semantic Search Accuracy
**Objective:** Verify semantic search understands meaning

**Steps:**
1. Ask: "What customer emotions appear in calls?"
2. Ask: "How do customers feel?"
3. Both should retrieve similar, relevant summaries

**Expected Result:**
- ✅ Both questions return similar documents
- ✅ Emotions and sentiments mentioned in response
- ✅ Specific emotions cited from summaries
- ✅ Response is contextually correct

---

### Test 3.3: Complex Question Handling
**Objective:** Verify RAG handles multi-faceted questions

**Steps:**
1. Ask: "Analyze customer sentiment patterns"
2. Observe response structure

**Expected Result:**
- ✅ Response organizes sentiment by emotional categories
- ✅ References multiple calls
- ✅ Provides frequency/pattern analysis
- ✅ Highlights trends

---

## 4. Chat History Tests

### Test 4.1: Message Display
**Objective:** Verify chat messages display correctly

**Steps:**
1. Ask a question
2. Observe message in chat container
3. Ask follow-up question
4. Observe both messages visible

**Expected Result:**
- ✅ User message appears in blue/left
- ✅ Assistant message appears in different style
- ✅ Both messages stay in history
- ✅ Chat container scrolls if needed
- ✅ Auto-scroll shows latest messages

---

### Test 4.2: History Persistence Across Tab Switches
**Objective:** Verify chat history persists when switching tabs

**Steps:**
1. In RAG Chat: Ask a question, get response
2. Switch to Standard Chat tab
3. Switch back to RAG Chat tab
4. Observe history

**Expected Result:**
- ✅ RAG chat history still visible
- ✅ Standard chat history independent
- ✅ No history loss
- ✅ Correct history shown in each tab

---

### Test 4.3: Clear History
**Objective:** Verify clear history button works

**Steps:**
1. Have some chat messages
2. Click "Clear RAG Chat History"
3. Observe chat container

**Expected Result:**
- ✅ Success message appears
- ✅ Chat history completely empty
- ✅ Can start fresh conversation

---

## 5. Context & LLM Tests

### Test 5.1: Citation Accuracy
**Objective:** Verify LLM correctly cites call data

**Steps:**
1. Ask: "Which agents got perfect 5-star ratings?"
2. Check response for call ID and agent name

**Expected Result:**
- ✅ Response mentions Sarah Mitchell (AG-2847)
- ✅ References call CC-2025-001847
- ✅ Cites actual 5-star rating
- ✅ Information matches bulk_summaries.json

---

### Test 5.2: Multi-turn Conversation
**Objective:** Verify context is maintained across questions

**Steps:**
1. Q1: "Which agents have high scores?"
2. Q2: "Tell me about the top performer"
3. Q3: "How did they handle difficult customers?"

**Expected Result:**
- ✅ Q2 references agent from Q1
- ✅ Q3 builds on previous context
- ✅ LLM remembers earlier questions
- ✅ Responses are contextually connected

---

### Test 5.3: System Prompt Integration
**Objective:** Verify system prompt is loaded and used

**Steps:**
1. Check response style and instructions
2. Verify response follows prompt guidelines

**Expected Behavior:**
- ✅ Uses specific agent names in citations
- ✅ Provides quantitative analysis when asked
- ✅ Highlights patterns and trends
- ✅ Organized and clear format
- ✅ References actual metrics

---

## 6. Predefined Questions Tests

### Test 6.1: Button Functionality
**Objective:** Verify predefined question buttons work

**Steps:**
1. Click "Which agents have the highest scores?"
2. Click "What are common customer issues?"
3. Click "Summarize unresolved issues"
4. Try each of 6 predefined buttons

**Expected Result:**
- ✅ Each button triggers a query
- ✅ Questions are accurate/relevant
- ✅ Responses appear in chat
- ✅ Buttons are easy to read
- ✅ Icons display correctly

---

### Test 6.2: Questions Relevance
**Objective:** Verify predefined questions produce good results

**Click Each Button:**
- "Which agents have the highest scores?" → Lists agents by score ✅
- "What are common customer issues?" → Lists issue categories ✅
- "Summarize unresolved issues" → Lists unresolved calls ✅
- "What agent got the best ratings?" → Lists by rating ✅
- "Analyze customer sentiment patterns" → Breaks down emotions ✅
- "Which department needs improvement?" → Department analysis ✅

---

## 7. UI/UX Tests

### Test 7.1: Tab Switching
**Objective:** Verify tabs switch cleanly without errors

**Steps:**
1. Click on "Standard Chat" tab
2. Click on "RAG-Based Chat" tab
3. Repeat several times
4. Verify no console errors

**Expected Result:**
- ✅ Tabs switch instantly
- ✅ No errors in browser console
- ✅ Chat content changes appropriately
- ✅ History persists per tab
- ✅ Session state maintained

---

### Test 7.2: Chat Container Scrolling
**Objective:** Verify auto-scroll works in 400px container

**Steps:**
1. Ask multiple questions (5+ messages)
2. Each response should be visible
3. Latest message should be visible after new response

**Expected Result:**
- ✅ Container stays 400px height
- ✅ Scrollbar appears with many messages
- ✅ Auto-scroll shows latest message
- ✅ Can manually scroll to see older messages
- ✅ No layout breaking

---

### Test 7.3: Button Layout
**Objective:** Verify buttons layout properly on different screen sizes

**Steps:**
1. View on desktop (wide screen)
2. View on tablet
3. View on mobile (narrow screen)
4. Resize browser window

**Expected Result:**
- ✅ Buttons stack appropriately
- ✅ Text readable in all sizes
- ✅ No button overlap
- ✅ "Reload Vector Store" button accessible
- ✅ "Clear Chat History" button accessible

---

## 8. Error Handling Tests

### Test 8.1: Network Error Handling
**Objective:** Verify graceful error handling

**Steps:**
1. Simulate network error (disconnect internet)
2. Try to ask a question in RAG chat
3. Observe error handling

**Expected Result:**
- ✅ User-friendly error message
- ✅ No app crash
- ✅ Can retry when connection restored
- ✅ Error logged appropriately

---

### Test 8.2: Invalid Question Handling
**Objective:** Verify system handles edge cases

**Steps:**
1. Ask: "" (empty question)
2. Ask: "????????" (special characters)
3. Ask: Very long question (500+ characters)
4. Ask: Non-English text (if supported)

**Expected Result:**
- ✅ Empty questions don't send
- ✅ Special characters handled gracefully
- ✅ Long questions processed correctly
- ✅ Clear behavior in all cases

---

### Test 8.3: Model Fallback
**Objective:** Verify default system prompt works if file missing

**Steps:**
1. Temporarily rename `prompt_store/chat_system_prompt.txt`
2. Access RAG chat
3. Ask a question
4. Verify response uses default prompt

**Expected Result:**
- ✅ Default prompt loads automatically
- ✅ Response quality remains good
- ✅ No errors in logs
- ✅ Rename file back after test

---

## 9. Performance Tests

### Test 9.1: Response Time Measurement
**Objective:** Verify acceptable response times

**Steps:**
1. Time first RAG query: 5-10 seconds (includes LLM)
2. Time second RAG query: 2-3 seconds
3. Time predefined button: 2-3 seconds
4. Time vector store reload: 5-10 seconds

**Expected Times:**
- ⏱️ Vector store creation: 5-10 seconds (one-time)
- ⏱️ Subsequent queries: 2-3 seconds
- ⏱️ Vector retrieval alone: <50ms
- ⏱️ Reload: 5-10 seconds

---

### Test 9.2: Memory Usage
**Objective:** Verify no memory leaks

**Steps:**
1. Open browser DevTools (F12)
2. Go to Memory tab
3. Ask 10+ questions in RAG chat
4. Observe memory usage

**Expected Result:**
- ✅ Memory usage stable
- ✅ No continuous growth
- ✅ Garbage collection working
- ✅ No memory leaks detected

---

## 10. Integration Tests

### Test 10.1: Both Chat Modes Work
**Objective:** Verify both chat modes functional simultaneously

**Steps:**
1. Use Standard Chat - ask for chart (e.g., "show agent performance")
2. Switch to RAG Chat - ask analytical question
3. Switch back to Standard Chat - predefined button
4. Switch to RAG - another question

**Expected Result:**
- ✅ Standard Chat generates charts
- ✅ RAG Chat provides semantic search
- ✅ Both modes work correctly
- ✅ No interference between modes
- ✅ Independent history per tab

---

### Test 10.2: Data Consistency
**Objective:** Verify both modes use same summaries

**Steps:**
1. Note an agent name and score from Standard Chat
2. Ask RAG Chat about that agent
3. Verify same score is mentioned

**Expected Result:**
- ✅ Scores match between modes
- ✅ Agent names consistent
- ✅ No data discrepancies
- ✅ Same source for both modes

---

## 11. Documentation Tests

### Test 11.1: Code Documentation
**Objective:** Verify code is well-documented

**Checks:**
- ✅ All classes have docstrings
- ✅ All methods have docstrings
- ✅ Parameters documented
- ✅ Return values documented
- ✅ Examples provided

---

### Test 11.2: User Documentation
**Objective:** Verify user guides are complete

**Checks:**
- ✅ RAG_QUICK_START.md is clear
- ✅ RAG_IMPLEMENTATION.md is detailed
- ✅ Examples provided
- ✅ Troubleshooting included
- ✅ Screenshots/diagrams helpful

---

## Final Validation Checklist

- [ ] All 11 test categories passed
- [ ] No critical errors in logs
- [ ] No warning messages for users
- [ ] Both chat modes fully functional
- [ ] Performance acceptable (2-3 sec queries)
- [ ] UI clean and intuitive
- [ ] Documentation complete
- [ ] Code quality high
- [ ] Tests reproducible
- [ ] Ready for production

---

## Testing Commands (for developers)

### Check vector store files
```bash
ls -lah /Users/dineshwar.elanchezhian/Documents/Dev/Python/IK/Projects/capstone/cc-ai-summarizer/output_data/vector_store/
```

### Check logs for errors
```bash
tail -f /Users/dineshwar.elanchezhian/Documents/Dev/Python/IK/Projects/capstone/cc-ai-summarizer/logs/log_*.txt
```

### Test vector store programmatically
```python
from src.vector_store import VectorStoreManager

manager = VectorStoreManager()
manager.create_vector_store(api_key="your-key")
results = manager.similarity_search("which agents have high scores?", k=5)
print(results)
```

### Test RAG chatbot programmatically
```python
from src.rag_chat import RAGChatbot

chatbot = RAGChatbot(api_key="your-key")
chatbot.initialize()
response = chatbot.get_rag_response("Which agents have the highest scores?")
print(response)
```

---

## Test Report Template

Use this to document your test run:

```
RAG Implementation Test Report
Date: _______________
Tester: _______________
Environment: Python 3.14, Streamlit 1.50.0

Category 1 - Setup & Initialization: PASS / FAIL
Category 2 - Vector Store: PASS / FAIL
Category 3 - Similarity Search: PASS / FAIL
Category 4 - Chat History: PASS / FAIL
Category 5 - Context & LLM: PASS / FAIL
Category 6 - Predefined Questions: PASS / FAIL
Category 7 - UI/UX: PASS / FAIL
Category 8 - Error Handling: PASS / FAIL
Category 9 - Performance: PASS / FAIL
Category 10 - Integration: PASS / FAIL
Category 11 - Documentation: PASS / FAIL

Overall Result: PASS / FAIL

Issues Found:
1. [Description]
2. [Description]

Notes:
[Any additional observations]
```

---

**Happy testing! 🧪**

