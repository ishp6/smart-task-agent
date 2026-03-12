# Smart Task Management AI Agent
 
A Python-based AI agent that manages tasks through natural language. No external dependencies — built on Python's standard library.
 
---
 
## What it does
 
- Create tasks from plain English ("Remind me to submit report by tomorrow")
- Auto-detects priority (urgent / high / medium / low) and due dates
- Lists tasks with progress insights
- Persists tasks across sessions via JSON storage
 
---
 
## How it works
 
```
Input → Perception → Decision → Action → Output
             ↑                              ↓
             ←———— Memory (JSON) ←—————————
```
 
- **Perception** — intent classification + entity extraction (dates, priorities)
- **Decision** — maps intent to action
- **Memory** — saves and loads task state between sessions
 
---
 
## Run it
 
```bash
git clone https://github.com/ishp6/smart-task-agent.git
cd smart-task-agent
python task_agent.py
```
 
**Python 3.7+** · No pip installs needed
 
---
 
Made by [Ishwari Patil](https://github.com/ishp6)
 
