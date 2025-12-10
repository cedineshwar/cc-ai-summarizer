# Chart Generation Features

This document describes all the chart and graph generation features available in the View All Summaries chat interface.

## 🎯 Supported Chart Types

### 1. **Agent Performance Bar Chart**
- **Triggered by keywords:** "agent performance", "agent scores", "performance scores", "agent skill"
- **What it shows:** Average performance scores for each agent (0-100 scale)
- **Color coding:**
  - 🟢 Green: Excellent (80+)
  - 🟡 Orange: Good (60-79)
  - 🔴 Red: Needs improvement (<60)
- **Use case:** Compare agent performance across your team

**Example queries:**
- "Show me agent performance chart"
- "What are the agent scores?"
- "Agent performance comparison"

---

### 2. **Agent Score Distribution Pie Chart**
- **Triggered by keywords:** "score distribution", "performance distribution", "score breakdown"
- **What it shows:** Distribution of agents by performance category
- **Categories:**
  - Excellent (85+)
  - Very Good (75-84)
  - Good (60-74)
  - Needs Improvement (<60)
- **Use case:** Get an overview of team performance levels

**Example queries:**
- "Show score distribution"
- "What's the performance breakdown?"
- "How many agents are in each tier?"

---

### 3. **Call Duration Chart**
- **Triggered by keywords:** "call duration", "conversation length", "duration", "time spent"
- **What it shows:** Average call duration for each agent (in minutes)
- **Color:** Gradient visualization (viridis color scale)
- **Use case:** Identify which agents handle longer or shorter calls

**Example queries:**
- "Show call duration by agent"
- "Average conversation length"
- "How long are calls taking?"

---

### 4. **Agent vs Conversation Count**
- **Triggered by keywords:** "agent count", "conversation count", "calls per agent", "agent vs conversation"
- **What it shows:** Number of calls/conversations handled by each agent
- **Color:** Multi-color bars for visual distinction
- **Use case:** See workload distribution and agent productivity

**Example queries:**
- "How many calls per agent?"
- "Conversation count by agent"
- "Who's handling the most calls?"

---

### 5. **Customer Sentiment Distribution**
- **Triggered by keywords:** "sentiment", "customer tone", "emotion", "customer mood"
- **What it shows:** Pie chart of customer sentiment across all calls
- **Sentiments tracked:** Happy, Satisfied, Neutral, Upset, Angry, Frustrated, etc.
- **Color coded:** Different colors for each emotion
- **Use case:** Understand overall customer experience and satisfaction

**Example queries:**
- "Show sentiment distribution"
- "How many happy vs angry customers?"
- "Customer emotion breakdown"

---

### 6. **Agent Rating Distribution**
- **Triggered by keywords:** "rating", "ratings", "stars", "agent rating"
- **What it shows:** Distribution of 1-5 star ratings for agents
- **Color coding:**
  - 🔴 Red: 1 star
  - 🟠 Orange: 2 stars
  - 🟡 Yellow: 3 stars
  - 🟢 Green: 4 stars
  - 🟢 Dark Green: 5 stars
- **Use case:** See overall agent satisfaction ratings

**Example queries:**
- "Show agent rating distribution"
- "What are the average ratings?"
- "How many 5-star ratings?"

---

### 7. **Call Resolution Status**
- **Triggered by keywords:** "resolution", "resolved", "unresolved", "resolution status"
- **What it shows:** Pie chart showing percentage of calls resolved vs unresolved
- **Metrics:** 
  - Resolved rate (%)
  - Unresolved rate (%)
- **Color:** Green (Resolved) vs Red (Unresolved)
- **Use case:** Track resolution success rate and identify problem areas

**Example queries:**
- "Show resolution status"
- "How many calls are resolved?"
- "What's the resolution rate?"

---

## 📊 Generic Chart Requests

If you request a chart with generic keywords like "chart", "graph", "plot", "visualization", or "diagram" without specifying a type, the system will default to the **Agent Performance Bar Chart**.

**Example queries:**
- "Create a chart"
- "Show me a graph"
- "Visualize the data"

---

## 🎨 Chart Features

All charts include:
- ✅ **Clear titles** - Descriptive chart names
- ✅ **Labeled axes** - Easy-to-understand x and y axes
- ✅ **Value labels** - Numbers displayed on bars/slices
- ✅ **Color coding** - Semantic colors (green for good, red for bad)
- ✅ **Professional styling** - Clean, readable fonts and layout
- ✅ **Summary text** - LLM-generated insights about the chart data

---

## 💬 How to Request Charts in Chat

1. **Open the View Summaries page**
2. **Scroll to the Chat with Summaries section**
3. **Type your request** in the chat input box
4. **Example requests:**
   - "Show me a bar chart of agent performance"
   - "Create a pie chart for score distribution"
   - "How many calls per agent in a bar chart?"
   - "Chart the customer sentiment"
   - "Display agent ratings distribution"

---

## 🔄 Chart + Text Response

The system intelligently decides whether to:
- **Generate a chart** - If chart keywords are detected
- **Provide text response** - If you ask a general question
- **Combine both** - Charts always include LLM-generated summary text

**Example:**
- Request: "Show agent performance"
  - Response: Bar chart + "Average scores range from 75 to 95..."

---

## 📈 Data Extracted for Charts

The charting system analyzes the following summary fields:
- `agentName` - Agent identifier
- `agentScore` - Performance score (0-100)
- `agentRating` - Star rating (1-5)
- `customerTone` - Customer sentiment
- `conversationlength` - Duration of call
- `callSummary` - To detect resolution status

---

## ⚙️ Technical Details

- **Charting Library:** Matplotlib + Seaborn
- **Format:** PNG images embedded in chat
- **Resolution:** 100 DPI (web-optimized)
- **Size:** Responsive to container width
- **Error Handling:** Graceful fallbacks if data is missing

---

## 🚀 Performance Tips

- Charts are generated **on-demand** (only when requested)
- No performance impact on normal chat queries
- Charts are **not stored** in chat history (to save space)
- Each chart is rendered fresh with latest data

---

## 📝 Example Chat Session

```
User: "Show me agent performance"
Assistant: [Bar chart of agent scores with analysis]

User: "What about sentiment?"
Assistant: [Pie chart of customer sentiment distribution]

User: "How many calls per agent?"
Assistant: [Bar chart of conversation counts]

User: "What's our resolution rate?"
Assistant: [Pie chart with resolution statistics]
```

---

## 🔧 Customization

To add new chart types:

1. Create a new function in `src/plotter.py`:
   ```python
   def generate_custom_chart(summaries: list) -> Tuple[str, str]:
       # Your chart generation code
       return img_base64, summary_text
   ```

2. Add keyword detection in `detect_chart_request()`:
   ```python
   'custom chart': ['keyword1', 'keyword2', 'keyword3']
   ```

3. Register in `generate_chart()`:
   ```python
   'custom chart': generate_custom_chart
   ```

---

**Happy charting! 📊📈📉**
