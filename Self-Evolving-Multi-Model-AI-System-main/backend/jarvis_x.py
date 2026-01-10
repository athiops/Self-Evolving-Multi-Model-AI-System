"""
JARVIS-X: Voice-enabled, Speaker-aware, Multi-domain AI Assistant
Built on Self-Evolving AI Architecture

Modules:
- Voice Interaction (Browser Web Speech API - frontend)
- Conversational Intelligence (GPT-5.2)
- Intent Router
- Multi-Domain Business Intelligence (FinTech, EduTech, MedTech, Elder Care)
- AI-Assisted Software Generation
- Internet-Aware Knowledge Retrieval (RAG)
"""

import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from collections import deque
from dotenv import load_dotenv

load_dotenv()

# LLM Integration
from emergentintegrations.llm.chat import LlmChat, UserMessage

# =============================================================================
# SPEAKER RECOGNITION (SIMULATED)
# =============================================================================

class SpeakerRecognition:
    """Simulated speaker recognition for demo purposes"""
    
    def __init__(self):
        # Demo voice profiles
        self.voice_profiles = {
            "admin": {
                "name": "Admin User",
                "access_level": "admin",
                "voice_signature": "demo_admin_signature",
                "registered_at": datetime.now(timezone.utc).isoformat()
            },
            "guest": {
                "name": "Guest User",
                "access_level": "restricted",
                "voice_signature": "demo_guest_signature",
                "registered_at": datetime.now(timezone.utc).isoformat()
            }
        }
        self.current_speaker = None
        self.is_verified = False
    
    def verify_speaker(self, speaker_id: str = "admin") -> Dict[str, Any]:
        """Simulate speaker verification"""
        if speaker_id in self.voice_profiles:
            self.current_speaker = self.voice_profiles[speaker_id]
            self.is_verified = True
            return {
                "verified": True,
                "speaker": self.current_speaker["name"],
                "access_level": self.current_speaker["access_level"],
                "message": "Voice verified. Welcome back."
            }
        else:
            self.is_verified = False
            self.current_speaker = None
            return {
                "verified": False,
                "speaker": None,
                "access_level": "none",
                "message": "Access restricted. Voice not recognized."
            }
    
    def get_current_speaker(self) -> Optional[Dict[str, Any]]:
        return self.current_speaker
    
    def register_voice_profile(self, user_id: str, name: str) -> Dict[str, Any]:
        """Register a new voice profile (simulated)"""
        self.voice_profiles[user_id] = {
            "name": name,
            "access_level": "user",
            "voice_signature": f"demo_{user_id}_signature",
            "registered_at": datetime.now(timezone.utc).isoformat()
        }
        return {"success": True, "message": f"Voice profile registered for {name}"}

# =============================================================================
# INTENT ROUTER
# =============================================================================

class IntentRouter:
    """Routes user queries to appropriate modules"""
    
    INTENT_CATEGORIES = {
        "system_intelligence": [
            "health", "status", "anomaly", "drift", "federated", "node", 
            "prediction", "forecast", "explain", "digital twin", "risk"
        ],
        "fintech": [
            "expense", "budget", "money", "finance", "spend", "income",
            "savings", "investment", "transaction", "payment", "cost",
            "financial", "profit", "loss", "balance"
        ],
        "edutech": [
            "learn", "study", "course", "lesson", "quiz", "education",
            "tutorial", "skill", "progress", "topic", "understand", "teach"
        ],
        "medtech": [
            "health", "vital", "heart", "blood", "medicine", "medication",
            "reminder", "elderly", "care", "alert", "symptom", "pressure"
        ],
        "software_generation": [
            "build", "create", "develop", "generate", "code", "website",
            "app", "dashboard", "startup", "mvp", "api", "frontend",
            "backend", "scaffold", "template", "software"
        ],
        "general_knowledge": [
            "what is", "who is", "when", "where", "how", "why", "tell me",
            "explain", "search", "find", "look up", "information"
        ]
    }
    
    def detect_intent(self, query: str) -> Dict[str, Any]:
        """Detect user intent from query"""
        query_lower = query.lower()
        
        # Score each category
        scores = {}
        for category, keywords in self.INTENT_CATEGORIES.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > 0:
                scores[category] = score
        
        if not scores:
            return {"intent": "general_conversation", "confidence": 0.5}
        
        # Get highest scoring intent
        best_intent = max(scores, key=scores.get)
        confidence = min(scores[best_intent] / 3, 1.0)
        
        return {
            "intent": best_intent,
            "confidence": round(confidence, 2),
            "all_scores": scores
        }

# =============================================================================
# FINTECH MODULE (SIMULATED - INDIAN RUPEE ₹)
# =============================================================================

class FinTechModule:
    """Personal Financial Management - Decision Support Only (INR ₹)"""
    
    CURRENCY = "₹"
    CURRENCY_NAME = "INR"
    
    def __init__(self):
        # Simulated expense data in INR (Indian Rupee)
        self.expenses = [
            {"category": "Food", "amount": 5500, "date": "2026-01-01", "description": "Groceries"},
            {"category": "Transport", "amount": 2500, "date": "2026-01-02", "description": "Fuel"},
            {"category": "Entertainment", "amount": 799, "date": "2026-01-03", "description": "Netflix"},
            {"category": "Utilities", "amount": 3200, "date": "2026-01-04", "description": "Electricity"},
            {"category": "Food", "amount": 1500, "date": "2026-01-05", "description": "Restaurant"},
            {"category": "Shopping", "amount": 4500, "date": "2026-01-06", "description": "Clothes"},
            {"category": "Health", "amount": 1200, "date": "2026-01-07", "description": "Pharmacy"},
            {"category": "Education", "amount": 2500, "date": "2026-01-08", "description": "Online Course"},
            {"category": "Recharge", "amount": 999, "date": "2026-01-09", "description": "Mobile Recharge"},
        ]
        self.budget = {
            "Food": 12000,
            "Transport": 5000,
            "Entertainment": 2000,
            "Utilities": 4000,
            "Shopping": 8000,
            "Health": 3000,
            "Education": 5000,
            "Recharge": 1500
        }
        self.income = 75000  # Monthly income in INR
    
    def get_expense_summary(self) -> Dict[str, Any]:
        """Get expense summary by category"""
        summary = {}
        for expense in self.expenses:
            cat = expense["category"]
            summary[cat] = summary.get(cat, 0) + expense["amount"]
        
        total_spent = sum(summary.values())
        remaining = self.income - total_spent
        
        return {
            "by_category": summary,
            "total_spent": total_spent,
            "income": self.income,
            "remaining": remaining,
            "savings_rate": round((remaining / self.income) * 100, 1)
        }
    
    def get_budget_status(self) -> Dict[str, Any]:
        """Check budget vs actual spending"""
        summary = self.get_expense_summary()
        status = {}
        
        for category, budget in self.budget.items():
            spent = summary["by_category"].get(category, 0)
            remaining = budget - spent
            percentage = round((spent / budget) * 100, 1) if budget > 0 else 0
            
            if percentage >= 100:
                alert = "OVER_BUDGET"
            elif percentage >= 80:
                alert = "WARNING"
            else:
                alert = "OK"
            
            status[category] = {
                "budget": budget,
                "spent": spent,
                "remaining": remaining,
                "percentage": percentage,
                "alert": alert
            }
        
        return status
    
    def get_financial_insights(self) -> List[str]:
        """Generate financial insights"""
        summary = self.get_expense_summary()
        budget_status = self.get_budget_status()
        
        insights = []
        
        # Savings insight
        if summary["savings_rate"] >= 20:
            insights.append(f"Great job! You're saving {summary['savings_rate']}% of your income.")
        elif summary["savings_rate"] >= 10:
            insights.append(f"You're saving {summary['savings_rate']}% - aim for 20% for better security.")
        else:
            insights.append(f"Warning: Low savings rate of {summary['savings_rate']}%. Consider reducing expenses.")
        
        # Budget alerts
        over_budget = [cat for cat, status in budget_status.items() if status["alert"] == "OVER_BUDGET"]
        if over_budget:
            insights.append(f"You've exceeded budget in: {', '.join(over_budget)}")
        
        warning_cats = [cat for cat, status in budget_status.items() if status["alert"] == "WARNING"]
        if warning_cats:
            insights.append(f"Approaching budget limit in: {', '.join(warning_cats)}")
        
        # Top spending category
        top_cat = max(summary["by_category"], key=summary["by_category"].get)
        insights.append(f"Your highest expense category is {top_cat} at ₹{summary['by_category'][top_cat]:,}")
        
        return insights
    
    def add_expense(self, category: str, amount: float, description: str) -> Dict[str, Any]:
        """Add a new expense (simulation)"""
        expense = {
            "category": category,
            "amount": amount,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "description": description
        }
        self.expenses.append(expense)
        return {"success": True, "expense": expense, "message": f"Expense of ₹{amount:,} recorded (simulated)", "currency": "INR"}

# =============================================================================
# SOFTWARE GENERATION MODULE
# =============================================================================

class SoftwareGenerationModule:
    """AI-Assisted Software Generation"""
    
    TEMPLATES = {
        "website": {
            "structure": [
                "src/",
                "src/components/",
                "src/pages/",
                "src/styles/",
                "public/",
                "package.json",
                "README.md"
            ],
            "tech_stack": ["React", "Tailwind CSS", "Vite"]
        },
        "dashboard": {
            "structure": [
                "src/",
                "src/components/",
                "src/components/charts/",
                "src/components/cards/",
                "src/pages/Dashboard.jsx",
                "src/api/",
                "package.json"
            ],
            "tech_stack": ["React", "Recharts", "Tailwind CSS", "Axios"]
        },
        "api": {
            "structure": [
                "app/",
                "app/routes/",
                "app/models/",
                "app/services/",
                "app/main.py",
                "requirements.txt",
                "README.md"
            ],
            "tech_stack": ["FastAPI", "Python", "MongoDB"]
        },
        "startup_mvp": {
            "structure": [
                "backend/",
                "backend/routes/",
                "backend/models/",
                "backend/server.py",
                "frontend/",
                "frontend/src/",
                "frontend/src/pages/",
                "frontend/src/components/",
                "docker-compose.yml",
                "README.md"
            ],
            "tech_stack": ["FastAPI", "React", "MongoDB", "Docker"]
        }
    }
    
    def analyze_requirements(self, requirements: str) -> Dict[str, Any]:
        """Analyze user requirements and suggest architecture"""
        req_lower = requirements.lower()
        
        # Detect project type
        if any(word in req_lower for word in ["dashboard", "analytics", "metrics"]):
            project_type = "dashboard"
        elif any(word in req_lower for word in ["api", "backend", "endpoints"]):
            project_type = "api"
        elif any(word in req_lower for word in ["startup", "mvp", "full-stack", "fullstack"]):
            project_type = "startup_mvp"
        else:
            project_type = "website"
        
        template = self.TEMPLATES[project_type]
        
        return {
            "project_type": project_type,
            "recommended_structure": template["structure"],
            "tech_stack": template["tech_stack"],
            "analysis": {
                "complexity": "medium" if project_type in ["dashboard", "api"] else "high" if project_type == "startup_mvp" else "low",
                "estimated_files": len(template["structure"]),
                "requires_backend": project_type in ["api", "startup_mvp", "dashboard"]
            }
        }
    
    def generate_scaffold(self, project_type: str, project_name: str) -> Dict[str, Any]:
        """Generate project scaffold"""
        if project_type not in self.TEMPLATES:
            project_type = "website"
        
        template = self.TEMPLATES[project_type]
        
        # Generate README
        readme = f"""# {project_name}

## Overview
This is an AI-generated {project_type} scaffold.

## Tech Stack
{chr(10).join(f'- {tech}' for tech in template['tech_stack'])}

## Project Structure
```
{chr(10).join(template['structure'])}
```

## Getting Started
1. Install dependencies
2. Configure environment variables
3. Run the development server

## ⚠️ Important Notice
This is AI-assisted code and requires human review before production use.

Generated by JARVIS-X Software Generation Module
"""
        
        return {
            "project_name": project_name,
            "project_type": project_type,
            "structure": template["structure"],
            "tech_stack": template["tech_stack"],
            "readme": readme,
            "disclaimer": "This is AI-assisted code and requires human review.",
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

# =============================================================================
# EDUTECH MODULE
# =============================================================================

class EduTechModule:
    """Educational Technology - Learning Support"""
    
    def __init__(self):
        self.learning_paths = {
            "python": ["Variables", "Data Types", "Control Flow", "Functions", "OOP", "Modules"],
            "web_dev": ["HTML", "CSS", "JavaScript", "React", "APIs", "Deployment"],
            "ai_ml": ["Python Basics", "NumPy", "Pandas", "Sklearn", "Deep Learning", "Projects"],
            "data_science": ["Statistics", "Python", "SQL", "Visualization", "ML", "Big Data"]
        }
        self.user_progress = {}
    
    def get_learning_path(self, topic: str) -> Dict[str, Any]:
        """Get recommended learning path"""
        topic_lower = topic.lower().replace(" ", "_")
        
        if topic_lower in self.learning_paths:
            path = self.learning_paths[topic_lower]
        else:
            # Default generic path
            path = ["Fundamentals", "Core Concepts", "Practice", "Projects", "Advanced Topics"]
        
        return {
            "topic": topic,
            "path": path,
            "total_modules": len(path),
            "estimated_hours": len(path) * 5,
            "difficulty": "beginner_to_intermediate"
        }
    
    def track_progress(self, user_id: str, topic: str, completed_module: int) -> Dict[str, Any]:
        """Track learning progress"""
        key = f"{user_id}_{topic}"
        if key not in self.user_progress:
            self.user_progress[key] = {"completed": [], "started_at": datetime.now(timezone.utc).isoformat()}
        
        if completed_module not in self.user_progress[key]["completed"]:
            self.user_progress[key]["completed"].append(completed_module)
        
        path = self.get_learning_path(topic)
        progress_pct = len(self.user_progress[key]["completed"]) / path["total_modules"] * 100
        
        return {
            "topic": topic,
            "completed_modules": self.user_progress[key]["completed"],
            "progress_percentage": round(progress_pct, 1),
            "remaining": path["total_modules"] - len(self.user_progress[key]["completed"])
        }

# =============================================================================
# MEDTECH / ELDER CARE MODULE (ASSISTIVE ONLY)
# =============================================================================

class MedTechModule:
    """Healthcare & Elder Care - Assistive Only (NO Diagnosis)"""
    
    def __init__(self):
        # Simulated vitals
        self.vitals_history = [
            {"heart_rate": 72, "blood_pressure": "120/80", "temperature": 98.6, "timestamp": "2026-01-10T08:00:00Z"},
            {"heart_rate": 75, "blood_pressure": "118/78", "temperature": 98.4, "timestamp": "2026-01-10T12:00:00Z"},
            {"heart_rate": 78, "blood_pressure": "122/82", "temperature": 98.7, "timestamp": "2026-01-10T16:00:00Z"},
        ]
        self.reminders = [
            {"type": "medication", "name": "Vitamin D", "time": "08:00", "frequency": "daily"},
            {"type": "medication", "name": "Blood Pressure Med", "time": "09:00", "frequency": "daily"},
            {"type": "activity", "name": "Morning Walk", "time": "07:00", "frequency": "daily"},
            {"type": "checkup", "name": "Doctor Appointment", "time": "10:00", "frequency": "monthly"},
        ]
    
    def get_current_vitals(self) -> Dict[str, Any]:
        """Get current vitals (simulated)"""
        import random
        
        vitals = {
            "heart_rate": random.randint(68, 82),
            "blood_pressure": f"{random.randint(115, 125)}/{random.randint(75, 85)}",
            "temperature": round(random.uniform(97.8, 99.0), 1),
            "oxygen_saturation": random.randint(95, 100),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Check for alerts (assistive)
        alerts = []
        if vitals["heart_rate"] > 100:
            alerts.append("Elevated heart rate detected. Consider resting.")
        if vitals["heart_rate"] < 60:
            alerts.append("Low heart rate detected. Monitor closely.")
        if vitals["oxygen_saturation"] < 95:
            alerts.append("Low oxygen saturation. Consider contacting healthcare provider.")
        
        return {
            "vitals": vitals,
            "alerts": alerts,
            "status": "ALERT" if alerts else "NORMAL",
            "disclaimer": "This is assistive monitoring only. Not a medical diagnosis."
        }
    
    def get_reminders(self) -> List[Dict[str, Any]]:
        """Get active reminders"""
        current_hour = datetime.now().hour
        
        upcoming = []
        for reminder in self.reminders:
            reminder_hour = int(reminder["time"].split(":")[0])
            if reminder_hour >= current_hour:
                upcoming.append(reminder)
        
        return upcoming
    
    def add_reminder(self, reminder_type: str, name: str, time: str, frequency: str) -> Dict[str, Any]:
        """Add a new reminder"""
        reminder = {
            "type": reminder_type,
            "name": name,
            "time": time,
            "frequency": frequency
        }
        self.reminders.append(reminder)
        return {"success": True, "reminder": reminder}

# =============================================================================
# JARVIS-X CONVERSATIONAL AI
# =============================================================================

class JarvisXConversation:
    """Main conversational AI powered by GPT-5.2"""
    
    SYSTEM_PROMPT = """You are JARVIS-X, a voice-enabled, speaker-aware, multi-domain AI assistant.

IDENTITY:
- Name: JARVIS-X (Just A Rather Very Intelligent System - Extended)
- Style: Professional, calm, helpful, Tony-Stark-inspired but realistic
- Always explain decisions clearly

CAPABILITIES:
1. System Intelligence - Monitor AI system health, anomalies, federated learning, drift detection
2. FinTech - Personal finance insights, expense analysis, budget tracking (NO transactions)
3. EduTech - Learning paths, progress tracking, topic explanations
4. MedTech - Vitals monitoring, reminders (ASSISTIVE ONLY, no diagnosis)
5. Software Generation - Create scaffolds, templates, MVPs
6. General Knowledge - Answer questions with sourced information

RULES:
- Always be helpful and clear
- Explain confidence levels for system decisions
- For medical/financial: always add appropriate disclaimers
- Never perform actual transactions or provide medical diagnosis
- Say "Decision support" or "Simulation-based" when appropriate

When asked about building software, ask clarifying questions first.
When providing health/financial info, remind user it's for informational purposes."""
    
    def __init__(self):
        self.api_key = os.environ.get("EMERGENT_LLM_KEY")
        self.sessions: Dict[str, LlmChat] = {}
        self.conversation_history: Dict[str, List[Dict]] = {}
    
    def get_or_create_session(self, session_id: str) -> LlmChat:
        """Get or create a chat session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = LlmChat(
                api_key=self.api_key,
                session_id=session_id,
                system_message=self.SYSTEM_PROMPT
            ).with_model("openai", "gpt-5.2")
            self.conversation_history[session_id] = []
        
        return self.sessions[session_id]
    
    async def chat(self, session_id: str, user_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a chat message"""
        chat = self.get_or_create_session(session_id)
        
        # Add context to message if provided
        full_message = user_message
        if context:
            context_str = f"\n\n[Context: {context}]"
            full_message = user_message + context_str
        
        try:
            # Send message to LLM
            message = UserMessage(text=full_message)
            response = await chat.send_message(message)
            
            # Store in history
            self.conversation_history[session_id].append({
                "role": "user",
                "content": user_message,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            self.conversation_history[session_id].append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            return {
                "response": response,
                "session_id": session_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "response": f"I apologize, I encountered an error: {str(e)}",
                "error": str(e),
                "session_id": session_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def get_history(self, session_id: str) -> List[Dict]:
        """Get conversation history"""
        return self.conversation_history.get(session_id, [])
    
    def clear_session(self, session_id: str):
        """Clear a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]

# =============================================================================
# INITIALIZE MODULES
# =============================================================================

speaker_recognition = SpeakerRecognition()
intent_router = IntentRouter()
fintech_module = FinTechModule()
software_module = SoftwareGenerationModule()
edutech_module = EduTechModule()
medtech_module = MedTechModule()
jarvis_conversation = JarvisXConversation()
