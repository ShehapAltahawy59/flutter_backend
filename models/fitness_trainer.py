import os
from groq import Groq
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import re

# LangChain imports
from langchain.memory import ConversationSummaryBufferMemory, VectorStoreRetrieverMemory
from langchain.schema.messages import HumanMessage, AIMessage
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.schema import BaseRetriever, Document
from pydantic import Field
import chromadb

# Custom Groq LLM wrapper for LangChain - FIXED VERSION
class GroqLLM(LLM):
    """Custom LangChain LLM wrapper for Groq - Fixed to work with Pydantic validation"""

    # Define fields properly for Pydantic validation
    groq_client: Any = Field(default=None, exclude=True)
    model_name: str = Field(default="llama3-70b-8192")

    def __init__(self, groq_client, model_name="llama3-70b-8192", **kwargs):
        super().__init__(**kwargs)
        # Use object.__setattr__ to bypass Pydantic validation for the client
        object.__setattr__(self, 'groq_client', groq_client)
        object.__setattr__(self, 'model_name', model_name)

    @property
    def _llm_type(self) -> str:
        return "groq"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any
    ) -> str:
        try:
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model_name,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 1500),
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

class FitnessMemoryManager:
    """Enhanced memory management using LangChain components"""

    def __init__(self, groq_client, user_profile: Dict):
        self.groq_client = groq_client
        self.user_profile = user_profile

        # Initialize LangChain LLM wrapper
        self.llm = GroqLLM(groq_client)

        # Initialize embeddings for vector storage
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )

        # Initialize vector store for long-term memory (fitness-specific memories)
        self.chroma_client = chromadb.Client()
        self.vector_store = Chroma(
            client=self.chroma_client,
            collection_name=f"fitness_memories_{user_profile.get('name', 'user')}",
            embedding_function=self.embeddings
        )

        # Conversation buffer with summary for recent chat
        self.conversation_memory = ConversationSummaryBufferMemory(
            llm=self.llm,
            max_token_limit=2000,  # Adjust based on your needs
            return_messages=True,
            memory_key="chat_history"
        )

        # Vector memory for retrieving relevant past conversations
        self.vector_memory = VectorStoreRetrieverMemory(
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 5}),
            memory_key="fitness_context"
        )

        # Fitness-specific memory categories
        self.workout_plans = []
        self.progress_tracking = []
        self.preferences = {}
        self.limitations_updates = []

    def add_conversation_turn(self, human_input: str, ai_response: str):
        """Add a conversation turn to memory systems"""

        # Add to conversation buffer memory
        self.conversation_memory.chat_memory.add_user_message(human_input)
        self.conversation_memory.chat_memory.add_ai_message(ai_response)

        # Analyze and categorize the conversation for vector storage
        self._categorize_and_store_conversation(human_input, ai_response)

    def _categorize_and_store_conversation(self, human_input: str, ai_response: str):
        """Analyze conversation and store important parts in vector memory"""

        combined_text = f"User: {human_input}\nTrainer: {ai_response}"

        # Check if this contains important fitness information
        importance_score = self._calculate_fitness_importance(combined_text)

        if importance_score > 0.6:  # Threshold for storing in long-term memory
            # Create metadata for better retrieval
            metadata = {
                "timestamp": datetime.now().isoformat(),
                "importance_score": importance_score,
                "category": self._categorize_content(combined_text),
                "user_name": self.user_profile.get('name', 'user')
            }

            # Store in vector memory
            self.vector_memory.save_context(
                {"input": human_input},
                {"output": ai_response}
            )

            # Also store in vector store directly for more control
            self.vector_store.add_texts(
                texts=[combined_text],
                metadatas=[metadata]
            )

    def _calculate_fitness_importance(self, text: str) -> float:
        """Calculate importance score for fitness-related content"""
        text_lower = text.lower()

        # Fitness-specific keywords with weights
        fitness_keywords = {
            'workout': 0.3, 'exercise': 0.3, 'routine': 0.3,
            'progress': 0.4, 'improvement': 0.4, 'goal': 0.3,
            'weight': 0.2, 'reps': 0.3, 'sets': 0.3,
            'diet': 0.3, 'nutrition': 0.3, 'meal': 0.2,
            'injury': 0.5, 'pain': 0.4, 'limitation': 0.4,
            'schedule': 0.3, 'plan': 0.3, 'struggle': 0.4,
            'achievement': 0.4, 'milestone': 0.4, 'difficulty': 0.3
        }

        score = 0.0
        word_count = len(text.split())

        # Calculate keyword-based score
        for keyword, weight in fitness_keywords.items():
            if keyword in text_lower:
                score += weight

        # Bonus for structured content (workout plans, numbered lists)
        if re.search(r'\d+\.|•|\n.*:|\n\s*-', text):
            score += 0.3

        # Bonus for measurements and specific numbers
        if re.search(r'\d+\s*(kg|lbs|reps|sets|minutes|hours|days|weeks|%)', text_lower):
            score += 0.2

        # Length normalization (longer detailed conversations are often more important)
        if word_count > 50:
            score += 0.1
        elif word_count < 10:
            score *= 0.7  # Penalty for very short messages

        return min(score, 1.0)

    def _categorize_content(self, text: str) -> str:
        """Categorize content for better organization"""
        text_lower = text.lower()

        if any(word in text_lower for word in ['workout', 'exercise', 'routine', 'plan']):
            return 'workout_plan'
        elif any(word in text_lower for word in ['progress', 'improvement', 'achievement']):
            return 'progress'
        elif any(word in text_lower for word in ['diet', 'nutrition', 'meal', 'food']):
            return 'nutrition'
        elif any(word in text_lower for word in ['injury', 'pain', 'limitation']):
            return 'limitations'
        elif any(word in text_lower for word in ['schedule', 'time', 'frequency']):
            return 'scheduling'
        else:
            return 'general'

    def get_relevant_context(self, current_input: str) -> str:
        """Get relevant context for current conversation"""
        context_parts = []

        # Get recent conversation context
        recent_context = self.conversation_memory.load_memory_variables({})
        if recent_context.get('chat_history'):
            context_parts.append("RECENT CONVERSATION CONTEXT:")
            context_parts.append(str(recent_context['chat_history']))
            context_parts.append("")

        # Get relevant past conversations using vector similarity
        try:
            relevant_docs = self.vector_store.similarity_search(
                current_input,
                k=3,  # Get top 3 most relevant past conversations
                filter={"user_name": self.user_profile.get('name', 'user')}
            )

            if relevant_docs:
                context_parts.append("RELEVANT PAST CONVERSATIONS:")
                for i, doc in enumerate(relevant_docs, 1):
                    metadata = doc.metadata
                    category = metadata.get('category', 'general')
                    timestamp = metadata.get('timestamp', 'unknown')
                    score = metadata.get('importance_score', 0)

                    context_parts.append(f"{i}. [{category.upper()}] ({timestamp[:10]}) Score: {score:.2f}")
                    context_parts.append(doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content)
                    context_parts.append("")
        except Exception as e:
            print(f"Warning: Could not retrieve vector context: {e}")

        return "\n".join(context_parts)

    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of current memory state"""
        total_messages = len(self.conversation_memory.chat_memory.messages)

        # Count documents in vector store
        try:
            vector_count = len(self.vector_store._collection.get()['ids'])
        except:
            vector_count = 0

        return {
            'total_conversation_messages': total_messages,
            'stored_important_memories': vector_count,
            'buffer_summary_length': len(self.conversation_memory.buffer) if hasattr(self.conversation_memory, 'buffer') else 0,
            'user_profile': self.user_profile.get('name', 'unknown')
        }

    def clear_session_memory(self):
        """Clear session memory while keeping long-term memories"""
        self.conversation_memory.clear()

    def export_memories(self) -> Dict[str, Any]:
        """Export all memories for saving"""
        try:
            # Get all documents from vector store
            all_docs = self.vector_store._collection.get()

            vector_memories = []
            if all_docs['ids']:
                for i, doc_id in enumerate(all_docs['ids']):
                    vector_memories.append({
                        'id': doc_id,
                        'content': all_docs['documents'][i],
                        'metadata': all_docs['metadatas'][i] if all_docs['metadatas'] else {}
                    })

            return {
                'conversation_messages': [
                    {"type": type(msg).__name__, "content": msg.content}
                    for msg in self.conversation_memory.chat_memory.messages
                ],
                'vector_memories': vector_memories,
                'memory_summary': self.get_memory_summary(),
                'export_timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Warning: Could not export all memories: {e}")
            return {'error': str(e)}

class FitnessAITrainer:
    def __init__(self, api_key):
        """Initialize the Groq client with API key and LangChain memory"""
        self.client = Groq(api_key=api_key)
        self.user_profile = {}
        self.memory_manager = None
        self.session_start_time = datetime.now()
        self.loaded_from_save = False

    def find_saved_sessions(self) -> List[str]:
        """Find all saved session files"""
        import glob
        return glob.glob("fitness_session_*.json")

    def load_session_data(self, filename: str) -> bool:
        """Load session data from file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)

            # Load user profile
            self.user_profile = data.get('user_profile', {})

            # Initialize memory manager with loaded profile
            self.memory_manager = FitnessMemoryManager(self.client, self.user_profile)

            # Load memories back into LangChain components
            memories = data.get('memories', {})

            # Restore conversation messages
            conversation_messages = memories.get('conversation_messages', [])
            for msg_data in conversation_messages:
                if msg_data['type'] == 'HumanMessage':
                    self.memory_manager.conversation_memory.chat_memory.add_user_message(msg_data['content'])
                elif msg_data['type'] == 'AIMessage':
                    self.memory_manager.conversation_memory.chat_memory.add_ai_message(msg_data['content'])

            # Restore vector memories
            vector_memories = memories.get('vector_memories', [])
            if vector_memories:
                texts = [mem['content'] for mem in vector_memories]
                metadatas = [mem['metadata'] for mem in vector_memories]
                self.memory_manager.vector_store.add_texts(texts=texts, metadatas=metadatas)

            self.loaded_from_save = True
            print(f"✅ Session loaded successfully!")
            print(f"📊 Restored {len(conversation_messages)} conversation messages")
            print(f"🧠 Restored {len(vector_memories)} important memories")

            return True

        except Exception as e:
            print(f"❌ Error loading session data: {str(e)}")
            return False

    def choose_session_to_load(self) -> bool:
        """Let user choose which saved session to load"""
        saved_files = self.find_saved_sessions()

        if not saved_files:
            print("No saved sessions found. Starting fresh session.")
            return False

        print(f"\n📁 Found {len(saved_files)} saved session(s):")
        print("0. Start new session")

        # Sort files by modification time (newest first)
        saved_files.sort(key=os.path.getmtime, reverse=True)

        for i, filename in enumerate(saved_files, 1):
            # Extract info from filename
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                user_name = data.get('user_profile', {}).get('name', 'Unknown')
                session_date = data.get('session_start_time', 'Unknown')
                if session_date != 'Unknown':
                    session_date = datetime.fromisoformat(session_date).strftime('%Y-%m-%d %H:%M')

                # Get memory stats
                memories = data.get('memories', {})
                msg_count = len(memories.get('conversation_messages', []))
                vector_count = len(memories.get('vector_memories', []))

                print(f"{i}. {user_name} - {session_date} ({msg_count} messages, {vector_count} memories)")
            except:
                print(f"{i}. {filename}")

        try:
            choice = input(f"\nChoose session to load (0-{len(saved_files)}): ").strip()

            if choice == '0' or choice == '':
                return False

            choice_num = int(choice)
            if 1 <= choice_num <= len(saved_files):
                return self.load_session_data(saved_files[choice_num - 1])
            else:
                print("Invalid choice. Starting new session.")
                return False

        except (ValueError, KeyboardInterrupt):
            print("Starting new session.")
            return False

    def setup_user_profile(self):
        """Set up user profile - either load existing or create new"""
        print("🏋️  Welcome to AI Fitness Trainer with Advanced Memory! 🏋️")

        # Check if there are saved sessions to load
        if self.choose_session_to_load():
            return True

        # If no session loaded, create new profile
        return self.create_new_profile()

    def create_new_profile(self,data):
        """Collect user fitness information"""
        print("Let's set up your fitness profile first.\n")

        try:
            # self.user_profile['name'] = input("What's your name? ").strip()
            # self.user_profile['age'] = int(input("How old are you? "))
            # self.user_profile['weight'] = float(input("What's your weight (kg)? "))
            # self.user_profile['height'] = float(input("What's your height (cm)? "))

            # print("\nFitness Goals:")
            # print("1. Weight Loss")
            # print("2. Muscle Gain")
            # print("3. General Fitness")
            # print("4. Strength Training")
            # print("5. Endurance")
            # goal_choice = input("Select your primary goal (1-5): ")
            # goals = {
            #     '1': 'Weight Loss',
            #     '2': 'Muscle Gain',
            #     '3': 'General Fitness',
            #     '4': 'Strength Training',
            #     '5': 'Endurance'
            # }
            # self.user_profile['fitness_goal'] = goals.get(goal_choice, 'General Fitness')

            # print("\nExperience Level:")
            # print("1. Beginner")
            # print("2. Intermediate")
            # print("3. Advanced")
            # exp_choice = input("Select your experience level (1-3): ")
            # experience_levels = {
            #     '1': 'Beginner',
            #     '2': 'Intermediate',
            #     '3': 'Advanced'
            # }
            # self.user_profile['experience'] = experience_levels.get(exp_choice, 'Beginner')

            # self.user_profile['equipment'] = input("What equipment do you have access to? (e.g., dumbbells, gym membership, bodyweight only): ").strip()

            # self.user_profile['limitations'] = input("Any injuries or physical limitations? (optional): ").strip()
            self.user_profile = data
            # Calculate BMI
            height_m = self.user_profile['height'] / 100
            bmi = self.user_profile['weight'] / (height_m ** 2)
            self.user_profile['bmi'] = round(bmi, 1)

            # Initialize memory manager with user profile
            self.memory_manager = FitnessMemoryManager(self.client, self.user_profile)

            print(f"\n✅ Profile created successfully!")
            self.display_profile()

        except ValueError:
            print("❌ Invalid input. Please enter valid numbers for age, weight, and height.")
            return False
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            return False
        except Exception as e:
            print(f"❌ Error setting up profile: {str(e)}")
            return False

        return True

    def display_profile(self):
        """Display current user profile"""
        print("\n" + "="*50)
        print(f"👤 Name: {self.user_profile['name']}")
        print(f"🎂 Age: {self.user_profile['age']} years")
        print(f"⚖️  Weight: {self.user_profile['weight']} kg")
        print(f"📏 Height: {self.user_profile['height']} cm")
        print(f"📊 BMI: {self.user_profile['bmi']}")
        print(f"🎯 Goal: {self.user_profile['fitness_goal']}")
        print(f"💪 Experience: {self.user_profile['experience']}")
        print(f"🏃 Equipment: {self.user_profile['equipment']}")
        if self.user_profile['limitations']:
            print(f"⚠️  Limitations: {self.user_profile['limitations']}")
        print("="*50 + "\n")

    def create_system_prompt(self, context: str = ""):
        """Create a personalized system prompt with memory context"""
        bmi_category = ""
        if self.user_profile['bmi'] < 18.5:
            bmi_category = "underweight"
        elif self.user_profile['bmi'] < 25:
            bmi_category = "normal weight"
        elif self.user_profile['bmi'] < 30:
            bmi_category = "overweight"
        else:
            bmi_category = "obese"

        session_duration = datetime.now() - self.session_start_time
        memory_summary = self.memory_manager.get_memory_summary() if self.memory_manager else {}

        system_prompt = f"""You are an expert AI fitness trainer and nutritionist with advanced memory capabilities powered by LangChain.

CLIENT PROFILE:
Name: {self.user_profile['name']}
Age: {self.user_profile['age']} years old
Weight: {self.user_profile['weight']} kg
Height: {self.user_profile['height']} cm
BMI: {self.user_profile['bmi']} ({bmi_category})
Primary Goal: {self.user_profile['fitness_goal']}
Experience Level: {self.user_profile['experience']}
Available Equipment: {self.user_profile['equipment']}
Physical Limitations: {self.user_profile['limitations'] if self.user_profile['limitations'] else 'None reported'}

SESSION INFO:
Duration: {session_duration.seconds // 60} minutes
Memory Status: {memory_summary.get('total_conversation_messages', 0)} conversation messages, {memory_summary.get('stored_important_memories', 0)} important memories stored

{context}

GUIDELINES:
1. Use the memory context to maintain continuity and build on previous conversations
2. Reference relevant past conversations when they apply to current discussion
3. Track progress and adapt recommendations based on historical context
4. Build progressively on workout plans and advice from memory
5. Remember preferences, struggles, and successes from past sessions
6. Maintain consistency with previous recommendations
7. Acknowledge improvements and changes mentioned in memory context
8. Always recommend consulting healthcare professionals for medical concerns

Remember: You have access to both recent conversation history and semantically relevant past conversations through advanced vector-based memory retrieval."""

        return system_prompt

    def get_ai_response(self, user_message):
        """Get response from Groq AI using LangChain memory"""
        try:
            if not self.memory_manager:
                return "❌ Memory system not initialized. Please restart the application."

            # Get relevant context from memory
            context = self.memory_manager.get_relevant_context(user_message)

            # Create system prompt with context
            system_prompt = self.create_system_prompt(context)

            # Prepare messages for API call
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]

            # Get response from Groq
            response = self.client.chat.completions.create(
                messages=messages,
                model="llama-3.1-70b-versatile",
                temperature=0.7,
                max_tokens=1500,
                top_p=1,
                stream=False
            )

            ai_response = response.choices[0].message.content

            # Add conversation turn to memory
            self.memory_manager.add_conversation_turn(user_message, ai_response)

            return ai_response

        except Exception as e:
            return f"❌ Error getting AI response: {str(e)}"

    def save_session_data(self):
        """Save session data including LangChain memories"""
        try:
            filename = f"fitness_session_{self.user_profile['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            # Export memories from LangChain components
            exported_memories = self.memory_manager.export_memories() if self.memory_manager else {}

            data = {
                'user_profile': self.user_profile,
                'memories': exported_memories,
                'session_start_time': self.session_start_time.isoformat(),
                'session_end_time': datetime.now().isoformat(),
            }

            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)

            print(f"💾 Session data saved to: {filename}")

        except Exception as e:
            print(f"❌ Error saving session data: {str(e)}")

    def show_memory_stats(self):
        """Display current memory statistics"""
        if not self.memory_manager:
            print("❌ Memory system not available")
            return

        stats = self.memory_manager.get_memory_summary()
        print("\n" + "="*50)
        print("🧠 LANGCHAIN MEMORY STATISTICS")
        print("="*50)
        print(f"Conversation messages: {stats['total_conversation_messages']}")
        print(f"Important memories stored: {stats['stored_important_memories']}")
        print(f"Buffer summary length: {stats['buffer_summary_length']}")
        print(f"User: {stats['user_profile']}")
        print("="*50 + "\n")

    def start_chat(self):
        """Start the main chat loop with LangChain memory"""
        welcome_msg = f"\n🤖 Hi {self.user_profile['name']}! I'm your AI fitness trainer powered by LangChain memory!"

        if self.loaded_from_save:
            welcome_msg += "\n🔄 I've loaded our previous conversations and remember our training history!"
        else:
            welcome_msg += "\n🆕 This is a fresh session. I'll start building memories of our conversations."

        print(welcome_msg)
        print("I'll remember our conversations using advanced semantic search and maintain context over time.")
        print("Ask me about workouts, exercises, nutrition, or any fitness-related questions.")
        print("\nCommands:")
        print("- 'quit', 'exit', 'bye': End conversation")
        print("- 'profile': View your profile")
        print("- 'save': Save session data")
        print("- 'memory': View memory statistics")
        print("- 'clear': Clear session memory (keep long-term memories)")
        print("- 'load': Load a different saved session\n")

        while True:
            try:
                user_input = input(f"💬 {self.user_profile['name']}: ").strip()

                if not user_input:
                    continue

                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print(f"\n👋 Thanks for training with me, {self.user_profile['name']}!")
                    save_choice = input("Would you like to save your session data? (y/n): ").lower()
                    if save_choice in ['y', 'yes']:
                        self.save_session_data()
                    print("Keep up the great work! 💪")
                    break

                elif user_input.lower() == 'profile':
                    self.display_profile()
                    continue

                elif user_input.lower() == 'save':
                    self.save_session_data()
                    continue

                elif user_input.lower() == 'memory':
                    self.show_memory_stats()
                    continue

                elif user_input.lower() == 'clear':
                    if self.memory_manager:
                        self.memory_manager.clear_session_memory()
                        print("✅ Session memory cleared (long-term memories preserved)")
                    continue

                elif user_input.lower() == 'load':
                    print("Loading a different session will end the current session.")
                    confirm = input("Continue? (y/n): ").lower()
                    if confirm in ['y', 'yes']:
                        if self.choose_session_to_load():
                            print(f"✅ Switched to {self.user_profile['name']}'s session")
                            self.display_profile()
                        else:
                            print("No session loaded. Continuing current session.")
                    continue

                # Get AI response using LangChain memory
                print("\n🤖 AI Trainer: ", end="")
                response = self.get_ai_response(user_input)
                print(response)
                print("\n" + "-"*50 + "\n")

            except KeyboardInterrupt:
                print(f"\n\n👋 Goodbye, {self.user_profile['name']}!")
                break
            except Exception as e:
                print(f"❌ An error occurred: {str(e)}")

