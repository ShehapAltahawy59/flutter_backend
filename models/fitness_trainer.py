import os
from typing import Dict, Any, List, Optional
from groq import Groq
import json
from datetime import datetime
import re
import gc

# LangChain imports
from langchain.memory import ConversationSummaryBufferMemory, VectorStoreRetrieverMemory
from langchain.schema.messages import HumanMessage, AIMessage
from langchain.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.schema import BaseRetriever, Document
from pydantic import Field
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from langchain.memory import ConversationBufferMemory
from utils.memory_manager import FitnessMemoryManager

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

class FitnessAITrainer:
    _instance = None
    _profile = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(FitnessAITrainer, cls).__new__(cls)
        return cls._instance

    def __init__(self, api_key):
        """Initialize the Groq client with API key and LangChain memory"""
        if not hasattr(self, 'initialized'):
            print("\n=== Initializing FitnessAITrainer ===")
            # Force garbage collection before initialization
            gc.collect()
            
            # Validate API key
            if not api_key or not isinstance(api_key, str) or len(api_key.strip()) == 0:
                print("Invalid API key provided")
                raise ValueError("Invalid API key provided")
            
            try:
                print("Initializing Groq client...")
                # Initialize Groq client with API key
                self.client = Groq(api_key=api_key.strip())
                
                print("Testing API key with simple request...")
                # Test the API key with a simple request
                self.client.chat.completions.create(
                    messages=[{"role": "user", "content": "test"}],
                    model="llama3-70b-8192",
                    max_tokens=5
                )
                print("API key test successful")
                
                # If we get here, the API key is valid
                print("Setting up trainer instance...")
                self.user_profile = FitnessAITrainer._profile or {}
                self.memory_manager = None
                self.session_start_time = datetime.now()
                self.loaded_from_save = False
                self.initialized = True
                print(f"Trainer initialized successfully with profile: {self.user_profile}")
                
            except Exception as e:
                error_msg = str(e)
                print(f"Error during initialization: {error_msg}")
                if "invalid_api_key" in error_msg.lower():
                    raise ValueError("Invalid Groq API key. Please check your API key in the .env file.")
                elif "authentication" in error_msg.lower():
                    raise ValueError("Authentication failed. Please check your API key in the .env file.")
                else:
                    raise ValueError(f"Failed to initialize Groq client: {error_msg}")

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

    def create_new_profile(self, data):
        """Collect user fitness information"""
        print("Let's set up your fitness profile first.\n")
        print(f"Debug - Received profile data: {data}")

        try:
            # Store the profile data in both instance and class
            self.user_profile = data.copy()
            FitnessAITrainer._profile = data.copy()
            
            # Calculate BMI
            height_m = self.user_profile['height'] / 100
            bmi = self.user_profile['weight'] / (height_m ** 2)
            self.user_profile['bmi'] = round(bmi, 1)
            FitnessAITrainer._profile['bmi'] = round(bmi, 1)

            print(f"\nDebug - Stored Profile: {self.user_profile}")

            # Initialize memory manager with user profile
            self.memory_manager = FitnessMemoryManager(self.client, self.user_profile)

            print(f"\n✅ Profile created successfully!")
            self.display_profile()
            return True

        except ValueError as e:
            print(f"❌ Invalid input: {str(e)}")
            return False
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            return False
        except Exception as e:
            print(f"❌ Error setting up profile: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return False

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
            print("\n=== Getting AI Response ===")
            # Debug logging
            print(f"User Profile: {self.user_profile}")
            print(f"Class Profile: {FitnessAITrainer._profile}")
            
            # Try to recover profile from class variable if instance profile is empty
            if not self.user_profile and FitnessAITrainer._profile:
                print("Recovering profile from class variable...")
                self.user_profile = FitnessAITrainer._profile.copy()
            
            # Verify user profile exists and has required fields
            if not self.user_profile or not isinstance(self.user_profile, dict):
                print("Error: User profile is not a dictionary or is None")
                raise ValueError("User profile not properly initialized")
            
            required_fields = ['name', 'age', 'weight', 'height', 'fitness_goal', 'experience', 'equipment', 'limitations']
            missing_fields = [field for field in required_fields if field not in self.user_profile]
            if missing_fields:
                print(f"Error: Missing fields in profile: {missing_fields}")
                raise ValueError(f"Missing required profile fields: {', '.join(missing_fields)}")
            
            # Check if memory manager exists and is properly initialized
            if not hasattr(self, 'memory_manager') or self.memory_manager is None:
                print("Initializing memory manager...")
                self.memory_manager = FitnessMemoryManager(self.client, self.user_profile)
                print("Memory manager initialized")
            
            # Get relevant context from memory
            print("Getting relevant context from memory...")
            context = self.memory_manager.get_relevant_context(user_message)
            print("Context retrieved successfully")

            # Create system prompt with context
            print("Creating system prompt...")
            system_prompt = self.create_system_prompt(context)
            print("System prompt created")

            # Prepare messages for API call
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]

            # Get response from Groq
            print("Sending request to Groq...")
            response = self.client.chat.completions.create(
                messages=messages,
                model="llama3-70b-8192",
                temperature=0.7,
                max_tokens=1500,
                top_p=1,
                stream=False
            )
            print("Response received from Groq")

            ai_response = response.choices[0].message.content

            # Add conversation turn to memory
            print("Adding conversation to memory...")
            self.memory_manager.add_conversation_turn(user_message, ai_response)
            print("Conversation added to memory")

            return ai_response

        except ValueError as ve:
            print(f"Profile validation error: {str(ve)}")
            return f"❌ Error: {str(ve)}. Please ensure your profile is properly set up."
        except Exception as e:
            print(f"Error in get_ai_response: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
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

    def update_profile(self, new_data: Dict[str, Any]) -> bool:
        """Update user profile with new data"""
        try:
            print("\n=== Updating Profile ===")
            print(f"Current profile: {self.user_profile}")
            print(f"New data: {new_data}")
            
            if not isinstance(new_data, dict):
                print("Invalid data type for profile update")
                return False
                
            if not self.user_profile:
                print("No existing profile to update")
                return False
            
            # Create a copy of current profile for safe update
            updated_profile = self.user_profile.copy()
            
            # Update only the fields that are provided
            for key, value in new_data.items():
                if key in ['name', 'age', 'weight', 'height', 'fitness_goal', 
                          'experience', 'equipment', 'limitations']:
                    updated_profile[key] = value
            
            # Recalculate BMI if weight or height changed
            if 'weight' in new_data or 'height' in new_data:
                weight = updated_profile.get('weight', 0)
                height = updated_profile.get('height', 0) / 100  # convert to meters
                if weight and height:
                    updated_profile['bmi'] = round(weight / (height * height), 1)
                    print(f"BMI recalculated: {updated_profile['bmi']}")
            
            # Update both instance and class profile
            self.user_profile = updated_profile
            FitnessAITrainer.user_profile = updated_profile
            
            # Reinitialize memory manager with updated profile
            if hasattr(self, 'memory_manager'):
                try:
                    self.memory_manager = FitnessMemoryManager(self.client, self.user_profile)
                    print("Memory manager reinitialized with updated profile")
                except Exception as e:
                    print(f"Warning: Failed to reinitialize memory manager: {str(e)}")
                    # Don't fail the update if memory manager reinitialization fails
            
            print("Profile updated successfully")
            return True
            
        except Exception as e:
            print(f"Error updating profile: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return False

