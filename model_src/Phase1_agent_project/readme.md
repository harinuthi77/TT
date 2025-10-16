# 🤖 Universal AI Agent

**A general-purpose autonomous agent that handles ANY task:**
- 🌐 Web automation (browsing, searching, data extraction)
- 📁 File operations (read, write, analyze)
- 💻 Code execution (write and run Python scripts)
- 🔍 Research and data gathering

---

## 📋 Features

### Web Automation
- ✅ Browse any website
- ✅ Search and navigate
- ✅ Extract products, articles, tables, links
- ✅ Fill forms and submit data
- ✅ Handle e-commerce (cart, checkout)
- ✅ Research tasks (Wikipedia, GitHub, news sites)

### File Operations
- ✅ Read/write files (JSON, CSV, TXT)
- ✅ List and analyze files
- ✅ Create directories
- ✅ File metadata extraction

### Code Execution
- ✅ Generate Python code with AI
- ✅ Execute code safely
- ✅ Validate syntax
- ✅ Save and run scripts

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install playwright anthropic pillow
playwright install chromium
```

### 2. Set API Key

```bash
# Mac/Linux
export ANTHROPIC_API_KEY='your-api-key-here'

# Windows PowerShell
$env:ANTHROPIC_API_KEY='your-api-key-here'
```

### 3. Run the Agent

```bash
python main.py
```

---

## 📁 Project Structure

```
project/
├── main.py                          # Main entry point
├── src/
│   ├── core/                        # Core systems
│   │   ├── config.py                # Configuration
│   │   ├── memory.py                # Learning system
│   │   ├── vision.py                # Web element detection
│   │   ├── cognition.py             # AI decision making
│   │   ├── executor.py              # Action execution
│   │   ├── file_handler.py          # File operations
│   │   └── code_executor.py         # Code execution
│   └── agents/                      # Agent implementations
│       ├── universal_agent.py       # Universal agent (routes tasks)
│       └── continuous_agent.py      # Web automation agent
├── workspace/                       # Agent's workspace
└── results/                         # Results and screenshots
    ├── screenshots/
    └── agent_brain.db              # Learning database
```

---

## 💡 Usage Examples

### Web Automation

```python
from src.agents.universal_agent import UniversalAgent

agent = UniversalAgent(debug=True)

# E-commerce
agent.execute("Go to Amazon and find wireless headphones under $50")

# Research
agent.execute("Go to GitHub and find trending Python repositories")

# News
agent.execute("Visit Hacker News and extract top 10 stories")

# Wikipedia
agent.execute("Search Wikipedia for quantum computing and summarize")
```

### File Operations

```python
# Read file
agent.execute("Read config.json and show me the contents")

# List files
agent.execute("List all Python files in the current directory")
```

### Code Execution

```python
# Generate and run code
agent.execute("Write a Python script to calculate fibonacci numbers")

# The agent will:
# 1. Generate the code using AI
# 2. Show you the code
# 3. Ask if you want to execute it
# 4. Run it safely if you approve
```

---

## 🎯 Example Tasks

### E-commerce
```
Go to Amazon and find laptops under $800 with 4+ star ratings
```

### Research
```
Go to GitHub and find the most popular machine learning libraries
```

### News
```
Visit news.ycombinator.com and extract the top 5 stories
```

### Social
```
Go to Reddit programming subreddit and get top posts from today
```

### Data Extraction
```
Visit Wikipedia, search for "artificial intelligence", and extract the main sections
```

---

## ⚙️ Configuration

Edit `src/core/config.py` to customize:

```python
# API Settings
ANTHROPIC_MODEL = "claude-sonnet-4-5-20250929"
ANTHROPIC_MAX_TOKENS = 3000

# Execution
MIN_CONFIDENCE_TO_ACT = 7  # Lower = more aggressive
MAX_STEPS_PER_TASK = 50

# Timing
MIN_ACTION_DELAY = 0.8  # seconds
MAX_ACTION_DELAY = 2.5  # seconds

# Browser
HEADLESS = False  # Set True for background mode
VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080
```

---

## 🧠 How It Works

1. **Task Analysis**: Detects task type (web/file/code)
2. **Route**: Sends to appropriate subsystem
3. **Execute**: Performs actions step-by-step
4. **Learn**: Records successes/failures in memory
5. **Adapt**: Improves over time

---

## 🔒 Safety Features

- ✅ Safe code execution with timeout
- ✅ Sandboxed file operations in workspace
- ✅ CAPTCHA detection and handling
- ✅ Bot detection awareness
- ✅ Stuck loop detection
- ✅ Memory-based learning (avoids repeated mistakes)

---

## 📊 Results

After each task:
- Screenshots saved to `results/screenshots/`
- Data saved to JSON files
- Learning database updated

---

## 🐛 Troubleshooting

### "ANTHROPIC_API_KEY not set"
```bash
export ANTHROPIC_API_KEY='your-key'
```

### "playwright not found"
```bash
pip install playwright
playwright install chromium
```

### Agent gets stuck
- The agent has built-in stuck detection
- It will automatically try a different approach
- Max 50 steps per task by default

### CAPTCHA detected
- Agent will pause and wait
- Solve it manually in the browser
- Agent will continue automatically

---

## 🎨 Customization

### Add Custom Actions

Edit `src/core/executor.py` to add new action types:

```python
def _handle_custom_action(self, details: str) -> Tuple[bool, str]:
    # Your custom logic here
    return True, "Success message"
```

### Add Custom Content Extraction

Edit `src/core/vision.py` to extract new content types:

```javascript
// In extract_page_content()
// Add your custom selectors
document.querySelectorAll('.your-selector').forEach(...)
```

---

## 📈 Performance Tips

1. **Start specific**: "Go to github.com" vs "find repositories"
2. **Use keywords**: Include domain names for faster navigation
3. **Be clear**: "Extract top 10 stories" vs "get some data"
4. **Trust the agent**: It learns from mistakes and improves

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional action types
- Better CAPTCHA handling
- Multi-tab support
- API integrations

---

## 📝 License

MIT License - Use freely for any purpose

---

## 🆘 Support

**Common Issues:**

1. **Slow execution**: Lower `MIN_CONFIDENCE_TO_ACT` in config
2. **Too aggressive**: Raise `MIN_CONFIDENCE_TO_ACT`
3. **Bot detection**: Agent has built-in handling, but some sites are strict

---

## 🎓 Learning Resources

The agent learns automatically, but you can help by:
- Giving clear, specific tasks
- Letting it complete tasks (don't interrupt)
- Checking `results/agent_brain.db` for learned patterns

---

## 🚦 Status Indicators

- ✅ Success
- ⏸️ Incomplete (max steps reached)
- ❌ Error
- ⚠️ Warning (CAPTCHA, stuck, etc.)
- 🔄 Retrying

---

**Ready to start? Run:**

```bash
python main.py
```

🎉 **Enjoy your universal AI agent!**