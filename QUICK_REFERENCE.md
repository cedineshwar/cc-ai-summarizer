# 📊 Chart Generation Quick Reference

## 🎯 Quick Start

### Example Queries in Chat:

```
"Show agent performance"
↓
[Bar Chart] Agent scores displayed

"What's the sentiment distribution?"
↓
[Pie Chart] Customer emotions shown

"How many calls per agent?"
↓
[Bar Chart] Conversation counts shown

"Agent ratings breakdown"
↓
[Pie Chart] 1-5 star distribution shown

"Call duration by agent"
↓
[Bar Chart] Minutes per agent shown

"Resolution status?"
↓
[Pie Chart] Resolved vs unresolved shown

"Score distribution"
↓
[Pie Chart] Performance tiers shown
```

---

## 📊 Chart Type Guide

| Chart | Use Case | Keywords | Output |
|-------|----------|----------|--------|
| 📈 Agent Performance | Compare agent scores | performance, scores, skill | Bar chart (0-100) |
| 🥧 Score Distribution | Performance tiers | distribution, breakdown | Pie chart (4 tiers) |
| ⏱️ Duration | Call lengths | duration, length, time | Bar chart (minutes) |
| 👥 Agent Count | Workload | conversation count, calls per agent | Bar chart (count) |
| 😊 Sentiment | Customer emotions | sentiment, tone, emotion | Pie chart (emotions) |
| ⭐ Ratings | Agent satisfaction | rating, stars | Bar chart (1-5 stars) |
| ✅ Resolution | Success rate | resolution, resolved | Pie chart (%) |

---

## 🎨 Color Meanings

### Performance Scores:
- 🟢 **Green (80+):** Excellent
- 🟡 **Orange (60-79):** Good
- 🔴 **Red (<60):** Needs Improvement

### Ratings (1-5 stars):
- 🔴 **Red:** 1 star
- 🟠 **Orange:** 2 stars
- 🟡 **Yellow:** 3 stars
- 🟢 **Green:** 4 stars
- 🟢 **Dark Green:** 5 stars

### Sentiment:
- 💚 Happy → Green
- 💙 Satisfied → Blue
- ⚪ Neutral → Gray
- 🟠 Upset → Orange
- ❤️ Angry → Red

---

## 💡 Tips

1. **Natural Language:** No special syntax needed
2. **Multiple Queries:** Keep chatting, request multiple charts
3. **Context:** Charts use all summaries in view
4. **Real-time:** Charts generated fresh each time
5. **Combined:** Charts + text analysis together

---

## 🔍 What Each Chart Shows

### Agent Performance Bar
```
Sarah Chen  ████████████████░░ 90
Marcus J.  ██████████████░░░░░ 78
Jennifer L ████████████████░ 82
```
✅ See individual agent performance at a glance

### Score Distribution Pie
```
Excellent (85+):   45%
Very Good (75-84): 35%
Good (60-74):      15%
Needs Imp (<60):    5%
```
✅ Understand overall team performance level

### Call Duration
```
Sarah Chen  ████ 18 mins
Marcus J.  ██████ 24 mins
Jennifer L  ██ 12 mins
```
✅ Identify patterns in call handling time

### Agent vs Conversation Count
```
Sarah Chen  ████████ 12
Marcus J.  ███████ 10
Jennifer L ████ 6
```
✅ See who handles most calls

### Customer Sentiment
```
Happy:       40%
Satisfied:   35%
Neutral:     15%
Upset:       10%
```
✅ Understand customer satisfaction

### Agent Ratings
```
⭐⭐⭐⭐⭐: 8 agents
⭐⭐⭐⭐:  5 agents
⭐⭐⭐:   2 agents
⭐⭐:    1 agent
```
✅ Quick view of agent satisfaction ratings

### Resolution Status
```
Resolved:   ████████░ 90%
Unresolved: ██░░░░░░░ 10%
```
✅ Track overall resolution success rate

---

## ❓ FAQ

**Q: Do I need special syntax?**
A: No! Use natural language like "show agent performance"

**Q: Can I request multiple charts?**
A: Yes! Keep chatting and request as many as you want

**Q: How fast are charts generated?**
A: Usually 0.5-2 seconds per chart

**Q: Can I use the data for reports?**
A: Yes! Charts are high-quality PNG images

**Q: What if my question doesn't match chart keywords?**
A: System will provide a text response from the LLM

**Q: Can I customize chart colors?**
A: Yes! Edit color mappings in src/plotter.py

---

## 🚀 Getting Started

1. Navigate to **View Summaries** page
2. Scroll to **Chat with Summaries** section
3. Type a chart request
4. Chart appears instantly!

### Try These First:
```
"Show me agent performance"
"What's our resolution rate?"
"Customer sentiment breakdown?"
"How many calls per agent?"
```

---

## ⚙️ Technical Notes

- Charts use **matplotlib** for rendering
- Styled with **seaborn** for professional look
- Encoded as **base64** for web display
- Generated **on-demand** (no caching)
- Support **1000+ summaries** per chart
- **Error handling** for missing data

---

## 📞 Support

For issues or questions:
1. Check logs in `/logs/` directory
2. Review `CHART_FEATURES.md` for details
3. Check `CHARTING_IMPLEMENTATION.md` for troubleshooting

---

**Happy charting! 📊✨**

Remember: The system is smart enough to understand you - just ask naturally!
