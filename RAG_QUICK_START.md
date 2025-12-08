# RAG Chat Quick Start Guide

## What is RAG Chat?

RAG (Retrieval-Augmented Generation) Chat uses **vector search** to find the most relevant call summaries for your questions, then uses AI to generate intelligent answers based on those summaries.

**In simple terms:** Instead of searching all summaries manually, RAG instantly finds the 5 most relevant calls and answers your question based on them.

---

## How to Use RAG Chat

### Step 1: Navigate to View Summaries

1. Open the Call Center AI Summarizer app
2. Click on **"View Summaries"** in the left sidebar
3. Scroll down to **"Chat with Summaries"** section

### Step 2: Switch to RAG Chat Tab

You'll see two tabs:

- **Tab 1:** 📊 Standard Chat (with Charts)
- **Tab 2:** 🤖 RAG-Based Chat (Vector Search) ← Click this

### Step 3: Ask Your Question

Type any question in the chat box:

- "Which agents have the highest scores?"
- "What are the most common customer issues?"
- "Analyze customer sentiment patterns"
- "Which agent got the best ratings?"
- "Summarize the unresolved issues"
- "How long are typical calls?"

### Step 4: Get Instant Answers

RAG will:
1. Search through all call summaries
2. Find the 5 most relevant calls
3. Analyze them with AI
4. Provide a detailed answer with specific call references

---

## Sample Questions to Try

### Agent Performance
- "Which agents have the highest scores?"
- "What agent got the best ratings?"
- "Who is the top performing agent?"

### Issue Analysis
- "What are common customer issues?"
- "Summarize unresolved issues"
- "What issue categories do we have?"

### Sentiment & Emotions
- "Analyze customer sentiment patterns"
- "What customer emotions are most common?"
- "Which calls had frustrated customers?"

### Call Duration
- "How long are the calls typically?"
- "Which agent handles calls fastest?"
- "Analyze call duration patterns"

### Resolution
- "What's our resolution rate?"
- "How many issues were resolved?"
- "Which calls were unresolved?"

---

## Key Features

### 🔍 Intelligent Search
- Finds relevant calls using AI understanding
- Not just keyword matching
- Understands context and meaning

### 📊 Specific Citations
- Answers reference specific call IDs
- Mentions agent and customer names
- Includes actual metrics and scores

### 💬 Chat History
- Maintains conversation history
- Understands follow-up questions
- Builds on previous context

### 🔄 Reload Vector Store
- Click the **"🔄 Reload Vector Store"** button after adding new summaries
- Updates the search index with new call data

---

## Comparing Chat Modes

| Feature | Standard Chat | RAG Chat |
|---------|---------------|----------|
| Chart Generation | ✅ Yes | ❌ No |
| Predefined Questions | ✅ Yes | ✅ Yes |
| Quick Answers | ✅ Yes | ✅ Yes |
| Vector Search | ❌ No | ✅ Yes |
| Complex Analysis | ⚠️ Limited | ✅ Excellent |
| Semantic Understanding | ⚠️ Basic | ✅ Advanced |
| Full Context | ❌ All summaries | ✅ Top 5 relevant |

**Use Standard Chat for:** Charts and quick summaries
**Use RAG Chat for:** Intelligent analysis and complex questions

---

## How RAG Works (Technical Overview)

### The Process

```
Your Question
    ↓
Vector Search Engine (FAISS)
    ↓
Finds 5 Most Relevant Summaries
    ↓
Feeds to AI (GPT-4)
    ↓
AI Analyzes and Answers
    ↓
Response with Specific Citations
```

### What Makes It Special

1. **Semantic Understanding:** Understands meaning, not just keywords
2. **Relevance:** Returns most relevant calls for your specific question
3. **Efficiency:** Processes hundreds of summaries in milliseconds
4. **Accuracy:** Bases answers on actual call data, not generalization

---

## Tips & Tricks

### ✅ Best Practices

1. **Ask specific questions:** "Which agent got the best ratings?" works better than "Tell me about agents"
2. **Use proper grammar:** "Customer sentiment patterns" finds better results than "how are customers"
3. **Ask follow-up questions:** RAG remembers context from previous questions
4. **Reload after updates:** Click "Reload Vector Store" when new calls are added

### ❌ Avoid These

1. **Very generic questions:** "Tell me everything" - be more specific
2. **Single words:** "Agents" - ask full questions instead
3. **Forgetting to reload:** New summaries won't appear until you reload
4. **Mixing request types:** "Show me a chart and analyze..." - stick to one per question

---

## Troubleshooting

### Issue: "Initializing RAG Chatbot" takes long

**Why:** Creating vector index from summaries (only happens once)
**Solution:** This is normal. Subsequent questions will be instant. ✅

### Issue: Empty response from RAG

**Why:** API key not set
**Solution:** 
1. Go to main app page (app.py)
2. Enter your OpenAI API key in the sidebar
3. Return to View Summaries
4. Try again

### Issue: "Please enter your OpenAI API key"

**Solution:** Same as above - set API key in main app sidebar

### Issue: New summaries not showing up

**Why:** Vector store cache is stale
**Solution:** Click **"🔄 Reload Vector Store"** button to refresh

### Issue: Getting wrong results for a question

**Why:** Question phrasing might not match call content well
**Solution:** Try rephrasing the question differently

---

## Understanding Vector Search

### What is it?

Vector search converts text into numbers (vectors) and finds similar vectors.

**Simple analogy:**
- Traditional search: Looking for exact keyword matches
- Vector search: Understanding meaning and finding conceptually similar content

### Why it's better for calls:

- Understands that "unresolved" is similar to "not resolved" 
- Finds "agent performance" when you ask about "scores"
- Connects "WiFi down" with "connectivity issue"
- Understands context and relationships between concepts

---

## Performance & Costs

### Speed

- **First RAG access:** 10-15 seconds (one-time vector store creation)
- **Each RAG query:** 2-3 seconds average
- **Vector retrieval:** <50ms (very fast)

### Cost

- **Per RAG query:** ~$0.001-0.003
- **Per day (20 queries):** ~$0.02-0.06
- **Much cheaper than chat without retrieval**

### Limits

- **Maximum summaries:** 10,000+ (scales well)
- **Response length:** 600 tokens (configurable)
- **Concurrent users:** Depends on OpenAI API limits

---

## Advanced Usage

### Setting Expectations

RAG works best with:
- ✅ Analytical questions
- ✅ Pattern finding queries
- ✅ Comparative analysis
- ✅ Data summarization

RAG is not ideal for:
- ❌ Chart generation (use Standard Chat)
- ❌ Real-time data (uses historical summaries)
- ❌ Creative writing (it's analytical, not creative)

### Chaining Questions

RAG maintains conversation context:

```
Q1: "Which agents have the highest scores?"
→ RAG finds relevant calls, answers

Q2: "Tell me more about the top agent"
→ RAG uses context from Q1, provides deeper analysis

Q3: "How did they handle difficult calls?"
→ RAG still remembers agent from Q1, analyzes their approach
```

### Asking for Specific Metrics

When you ask for specific data:

```
Q: "What's the average agent score?"
→ RAG retrieves calls, calculates average from retrieved data

Q: "Which agents scored above 85?"
→ RAG analyzes top 5 relevant calls, identifies high scorers
```

---

## Next Steps

1. **Try Sample Questions:** Use the predefined buttons to see RAG in action
2. **Ask Your Own:** Experiment with different question styles
3. **Reload Vector Store:** After adding new call summaries
4. **Compare Modes:** Use Standard Chat for charts, RAG Chat for analysis
5. **Provide Feedback:** Let us know what questions work best!

---

## FAQ

**Q: Does RAG replace Standard Chat?**
A: No! Both are useful. Use Standard Chat for charts, RAG Chat for analysis.

**Q: Can I see which calls RAG used?**
A: Yes! RAG mentions specific call IDs and agent names in responses.

**Q: Is my data secure?**
A: Summaries are sent to OpenAI for analysis. Check OpenAI's privacy policy.

**Q: How often should I reload the vector store?**
A: After adding new summaries. No need to reload otherwise.

**Q: Can RAG access real-time data?**
A: No, only summaries in your `bulk_summaries.json` file.

**Q: What if I have 1000+ summaries?**
A: RAG scales well! Performance stays under 5 seconds per query.

---

## More Information

For technical details, see: **RAG_IMPLEMENTATION.md**

For troubleshooting: Check the logs in `/logs/` folder

For architecture: See function diagrams in README.md

---

**Happy analyzing! 🚀**

