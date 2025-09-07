import json
import datetime
from typing import List, Dict, Optional
import re
from dataclasses import dataclass, asdict
from enum import Enum

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class Task:
    id: int
    title: str
    description: str
    priority: Priority
    status: TaskStatus
    due_date: Optional[datetime.datetime] = None
    created_at: datetime.datetime = None
    completed_at: Optional[datetime.datetime] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.datetime.now()
        if self.tags is None:
            self.tags = []

class SmartTaskAgent:
    """
    An AI Agent that understands natural language and manages tasks intelligently.
    
    Key Agent Capabilities:
    1. Natural Language Processing - understands user intents
    2. Decision Making - prioritizes and categorizes tasks
    3. Memory - persists task data
    4. Autonomous Actions - suggests optimizations and reminders
    """
    
    def __init__(self, data_file: str = "tasks.json"):
        self.data_file = data_file
        self.tasks: Dict[int, Task] = {}
        self.next_id = 1
        self.load_tasks()
        
        # Intent patterns for natural language understanding
        self.intent_patterns = {
            'add_task': [
                r'add (task|todo|item)',
                r'create (task|todo|item)',
                r'new (task|todo|item)',
                r'i need to',
                r'remind me to',
                r'schedule'
            ],
            'complete_task': [
                r'complete',
                r'finish',
                r'done with',
                r'finished',
                r'mark.*done'
            ],
            'list_tasks': [
                r'show.*tasks',
                r'list.*tasks',
                r'what.*tasks',
                r'my tasks',
                r'todo list'
            ],
            'high_priority': [
                r'urgent',
                r'important',
                r'asap',
                r'critical',
                r'priority',
                r'rush'
            ],
            'due_today': [
                r'today',
                r'by today',
                r'due today'
            ],
            'due_tomorrow': [
                r'tomorrow',
                r'by tomorrow',
                r'due tomorrow'
            ]
        }

    def perceive_environment(self, user_input: str) -> Dict:
        """
        PERCEPTION: Agent analyzes the input to understand context and intent
        """
        user_input_lower = user_input.lower()
        
        perception = {
            'raw_input': user_input,
            'intent': self._classify_intent(user_input_lower),
            'priority': self._extract_priority(user_input_lower),
            'due_date': self._extract_due_date(user_input_lower),
            'task_content': self._extract_task_content(user_input),
            'task_id': self._extract_task_id(user_input_lower)
        }
        
        return perception

    def decide_action(self, perception: Dict) -> str:
        """
        DECISION MAKING: Agent decides what action to take based on perception
        """
        intent = perception['intent']
        
        if intent == 'add_task':
            return 'create_task'
        elif intent == 'complete_task':
            return 'mark_complete'
        elif intent == 'list_tasks':
            return 'show_tasks'
        else:
            return 'clarify_request'

    def execute_action(self, action: str, perception: Dict) -> str:
        """
        ACTION EXECUTION: Agent performs the decided action
        """
        if action == 'create_task':
            return self._create_task(perception)
        elif action == 'mark_complete':
            return self._complete_task(perception)
        elif action == 'show_tasks':
            return self._list_tasks(perception)
        elif action == 'clarify_request':
            return self._ask_for_clarification()
        else:
            return "I'm not sure how to help with that."

    def process_request(self, user_input: str) -> str:
        """
        MAIN AGENT LOOP: Perceive -> Decide -> Act
        """
        # Step 1: Perceive the environment
        perception = self.perceive_environment(user_input)
        
        # Step 2: Decide on action
        action = self.decide_action(perception)
        
        # Step 3: Execute action
        response = self.execute_action(action, perception)
        
        # Step 4: Learn and adapt (save state)
        self.save_tasks()
        
        return response

    def _classify_intent(self, text: str) -> str:
        """Natural Language Understanding - classify user intent"""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return intent
        return 'unknown'

    def _extract_priority(self, text: str) -> Priority:
        """Extract priority level from text"""
        if any(word in text for word in ['urgent', 'critical', 'asap']):
            return Priority.URGENT
        elif any(word in text for word in ['important', 'high priority']):
            return Priority.HIGH
        elif any(word in text for word in ['medium', 'normal']):
            return Priority.MEDIUM
        else:
            return Priority.MEDIUM  # default

    def _extract_due_date(self, text: str) -> Optional[datetime.datetime]:
        """Extract due date from text"""
        today = datetime.datetime.now().replace(hour=23, minute=59, second=59)
        
        if any(word in text for word in ['today', 'by today']):
            return today
        elif any(word in text for word in ['tomorrow', 'by tomorrow']):
            return today + datetime.timedelta(days=1)
        elif 'next week' in text:
            return today + datetime.timedelta(days=7)
        
        return None

    def _extract_task_content(self, text: str) -> str:
        """Extract the actual task description from text"""
        # Remove common command words to get the core task
        text = re.sub(r'^(add task|create task|new task|remind me to|i need to)\s*', '', text.lower())
        text = re.sub(r'\s*(urgent|important|today|tomorrow|asap).*$', '', text)
        return text.strip().capitalize()

    def _extract_task_id(self, text: str) -> Optional[int]:
        """Extract task ID from text for operations on existing tasks"""
        match = re.search(r'task (\d+)', text)
        if match:
            return int(match.group(1))
        return None

    def _create_task(self, perception: Dict) -> str:
        """Create a new task"""
        task = Task(
            id=self.next_id,
            title=perception['task_content'],
            description=perception['raw_input'],
            priority=perception['priority'],
            status=TaskStatus.PENDING,
            due_date=perception['due_date']
        )
        
        self.tasks[self.next_id] = task
        self.next_id += 1
        
        response = f"✅ Created task #{task.id}: '{task.title}'"
        response += f"\n   Priority: {task.priority.name}"
        if task.due_date:
            response += f"\n   Due: {task.due_date.strftime('%Y-%m-%d %H:%M')}"
            
        return response

    def _complete_task(self, perception: Dict) -> str:
        """Mark a task as complete"""
        task_id = perception['task_id']
        
        if task_id and task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.datetime.now()
            return f"🎉 Completed task #{task_id}: '{task.title}'"
        else:
            # Try to complete the most recent pending task
            pending_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]
            if pending_tasks:
                task = max(pending_tasks, key=lambda t: t.created_at)
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.datetime.now()
                return f"🎉 Completed task #{task.id}: '{task.title}'"
            else:
                return "❌ No pending tasks found to complete."

    def _list_tasks(self, perception: Dict) -> str:
        """List all tasks with intelligent filtering and sorting"""
        if not self.tasks:
            return "📝 You have no tasks yet. Try saying 'Add task: Buy groceries'"
        
        # Separate tasks by status
        pending_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]
        completed_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]
        
        response = "📋 **YOUR TASKS**\n\n"
        
        if pending_tasks:
            # Sort pending tasks by priority and due date
            pending_tasks.sort(key=lambda t: (t.priority.value, t.due_date or datetime.datetime.max), reverse=True)
            
            response += "🔄 **PENDING TASKS:**\n"
            for task in pending_tasks:
                response += f"#{task.id} - {task.title}"
                response += f" [{task.priority.name}]"
                if task.due_date:
                    days_until_due = (task.due_date - datetime.datetime.now()).days
                    if days_until_due < 0:
                        response += " ⚠️ OVERDUE"
                    elif days_until_due == 0:
                        response += " ⏰ DUE TODAY"
                    elif days_until_due == 1:
                        response += " 📅 DUE TOMORROW"
                response += "\n"
        
        if completed_tasks:
            response += f"\n✅ **COMPLETED:** {len(completed_tasks)} tasks\n"
            
        # Agent provides intelligent insights
        response += self._provide_insights(pending_tasks, completed_tasks)
        
        return response

    def _provide_insights(self, pending_tasks: List[Task], completed_tasks: List[Task]) -> str:
        """Agent provides autonomous insights and recommendations"""
        insights = "\n🤖 **AGENT INSIGHTS:**\n"
        
        if pending_tasks:
            urgent_tasks = [t for t in pending_tasks if t.priority == Priority.URGENT]
            overdue_tasks = [t for t in pending_tasks if t.due_date and t.due_date < datetime.datetime.now()]
            
            if urgent_tasks:
                insights += f"⚡ You have {len(urgent_tasks)} urgent tasks - consider tackling these first!\n"
            
            if overdue_tasks:
                insights += f"⚠️ {len(overdue_tasks)} tasks are overdue. Need help prioritizing?\n"
            
            if len(pending_tasks) > 10:
                insights += "📊 You have many pending tasks. Consider breaking them into smaller chunks.\n"
        
        if completed_tasks:
            insights += f"🎯 Great job! You've completed {len(completed_tasks)} tasks.\n"
        
        return insights

    def _ask_for_clarification(self) -> str:
        """Agent asks for clarification when it doesn't understand"""
        return """🤔 I'm not sure what you'd like me to do. I can help you with:

• "Add task: [description]" - Create a new task
• "Complete task [number]" - Mark a task as done  
• "Show my tasks" - List all your tasks
• "Add urgent task: [description]" - Create high-priority task

Try one of these commands!"""

    def get_autonomous_suggestions(self) -> str:
        """Agent autonomously provides helpful suggestions"""
        pending_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]
        
        if not pending_tasks:
            return "🎉 All caught up! No pending tasks."
        
        # Find the most important task to work on
        urgent_tasks = [t for t in pending_tasks if t.priority == Priority.URGENT]
        due_today = [t for t in pending_tasks if t.due_date and t.due_date.date() == datetime.date.today()]
        
        suggestion = "🤖 **AUTONOMOUS SUGGESTION:**\n"
        
        if urgent_tasks:
            task = urgent_tasks[0]
            suggestion += f"Focus on urgent task: '{task.title}' (Task #{task.id})"
        elif due_today:
            task = due_today[0]
            suggestion += f"Don't forget: '{task.title}' is due today! (Task #{task.id})"
        else:
            # Suggest highest priority task
            highest_priority = max(pending_tasks, key=lambda t: t.priority.value)
            suggestion += f"Next suggested task: '{highest_priority.title}' (Task #{highest_priority.id})"
        
        return suggestion

    def save_tasks(self):
        """Persist tasks to file (Agent memory)"""
        try:
            tasks_data = {}
            for task_id, task in self.tasks.items():
                task_dict = asdict(task)
                # Convert datetime objects to strings for JSON serialization
                if task_dict['due_date']:
                    task_dict['due_date'] = task.due_date.isoformat()
                if task_dict['created_at']:
                    task_dict['created_at'] = task.created_at.isoformat()
                if task_dict['completed_at']:
                    task_dict['completed_at'] = task.completed_at.isoformat()
                task_dict['priority'] = task.priority.value
                task_dict['status'] = task.status.value
                tasks_data[task_id] = task_dict
            
            with open(self.data_file, 'w') as f:
                json.dump({'tasks': tasks_data, 'next_id': self.next_id}, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save tasks: {e}")

    def load_tasks(self):
        """Load tasks from file (Agent memory restoration)"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                
            self.next_id = data.get('next_id', 1)
            
            for task_id, task_data in data.get('tasks', {}).items():
                # Convert strings back to datetime objects
                if task_data['due_date']:
                    task_data['due_date'] = datetime.datetime.fromisoformat(task_data['due_date'])
                if task_data['created_at']:
                    task_data['created_at'] = datetime.datetime.fromisoformat(task_data['created_at'])
                if task_data['completed_at']:
                    task_data['completed_at'] = datetime.datetime.fromisoformat(task_data['completed_at'])
                
                task_data['priority'] = Priority(task_data['priority'])
                task_data['status'] = TaskStatus(task_data['status'])
                
                task = Task(**task_data)
                self.tasks[int(task_id)] = task
                
        except FileNotFoundError:
            # First run, no saved tasks
            pass
        except Exception as e:
            print(f"Warning: Could not load tasks: {e}")

def main():
    """Demo of the Smart Task Management Agent"""
    print("🤖 Smart Task Management Agent Started!")
    print("=" * 50)
    
    agent = SmartTaskAgent()
    
    # Demo interactions
    demo_inputs = [
        "Add task: Buy groceries for dinner tonight",
        "Create urgent task: Submit project report by tomorrow", 
        "Remind me to call mom today",
        "Show my tasks",
        "Complete task 1",
        "List all tasks"
    ]
    
    print("🎯 DEMO MODE - Showing agent capabilities:\n")
    
    for user_input in demo_inputs:
        print(f"👤 USER: {user_input}")
        response = agent.process_request(user_input)
        print(f"🤖 AGENT: {response}")
        print("-" * 40)
    
    # Show autonomous suggestions
    print("\n" + agent.get_autonomous_suggestions())
    
    print("\n🎯 INTERACTIVE MODE - Try your own commands!")
    print("Type 'quit' to exit\n")
    
    while True:
        try:
            user_input = input("👤 YOU: ").strip()
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("🤖 AGENT: Goodbye! Your tasks are saved.")
                break
            
            if user_input:
                response = agent.process_request(user_input)
                print(f"🤖 AGENT: {response}")
                print()
        except KeyboardInterrupt:
            print("\n🤖 AGENT: Goodbye! Your tasks are saved.")
            break

if __name__ == "__main__":
    main()