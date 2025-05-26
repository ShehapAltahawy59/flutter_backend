# routes/fitness_trainer_routes.py - Fitness Trainer AI Routes
from flask import Blueprint, request, jsonify, session
import os
import json
import uuid
import glob
from datetime import datetime
from typing import Dict, Any, List, Optional

# Import your fitness trainer classes (adjust imports based on your structure)
try:
    from groq import Groq
    from langchain.memory import ConversationSummaryBufferMemory, VectorStoreRetrieverMemory
    from langchain.schema.messages import HumanMessage, AIMessage
    from langchain.vectorstores import Chroma
    from langchain.embeddings import HuggingFaceEmbeddings
    from langchain.llms.base import LLM
    from langchain.callbacks.manager import CallbackManagerForLLMRun
    from pydantic import Field
    import chromadb
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Some fitness trainer dependencies not available: {e}")
    DEPENDENCIES_AVAILABLE = False

# Create blueprint
fitness_bp = Blueprint('fitness', __name__)

# Store active trainers in memory (in production, use Redis or database)
active_trainers = {}

class FlutterFitnessAPI:
    """Flask API wrapper for the Fitness AI Trainer"""
    
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            print("⚠️  Warning: GROQ_API_KEY not found")
    
    def get_or_create_trainer(self, session_id: str):
        """Get existing trainer or create new one for session"""
        if not DEPENDENCIES_AVAILABLE:
            raise Exception("Fitness trainer dependencies not available")
            
        if session_id not in active_trainers:
            # Import your fitness trainer class here
            # from fitness_trainer import FitnessAITrainer
            # trainer = FitnessAITrainer(self.groq_api_key)
            # active_trainers[session_id] = trainer
            
            # Placeholder for now - replace with your actual trainer class
            active_trainers[session_id] = {
                'session_id': session_id,
                'user_profile': None,
                'memory_manager': None,
                'created_at': datetime.now().isoformat()
            }
        return active_trainers[session_id]
    
    def cleanup_session(self, session_id: str):
        """Clean up trainer session"""
        if session_id in active_trainers:
            del active_trainers[session_id]

# Initialize API
fitness_api = FlutterFitnessAPI()

@fitness_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'fitness-ai-trainer',
        'dependencies_available': DEPENDENCIES_AVAILABLE,
        'active_sessions': len(active_trainers)
    })

@fitness_bp.route('/session/start', methods=['POST'])
def start_session():
    """Start a new fitness session"""
    try:
        if not DEPENDENCIES_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Fitness trainer dependencies not available'
            }), 503
            
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        session['fitness_session_id'] = session_id
        
        # Create trainer instance
        trainer = fitness_api.get_or_create_trainer(session_id)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Fitness training session started successfully'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@fitness_bp.route('/profile/create', methods=['POST'])
def create_profile():
    """Create user fitness profile"""
    try:
        session_id = session.get('fitness_session_id')
        if not session_id:
            return jsonify({'success': False, 'error': 'No active fitness session'}), 400
        
        data = request.json
        trainer = fitness_api.get_or_create_trainer(session_id)
        
        # Validate required fields
        required_fields = ['name', 'age', 'weight', 'height', 'fitness_goal', 'experience']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False, 
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Set up user profile
        profile = {
            'name': data['name'],
            'age': int(data['age']),
            'weight': float(data['weight']),
            'height': float(data['height']),
            'fitness_goal': data['fitness_goal'],
            'experience': data['experience'],
            'equipment': data.get('equipment', ''),
            'limitations': data.get('limitations', ''),
            'created_at': datetime.now().isoformat()
        }
        
        # Calculate BMI
        height_m = profile['height'] / 100
        bmi = profile['weight'] / (height_m ** 2)
        profile['bmi'] = round(bmi, 1)
        
        # Store profile in trainer
        if isinstance(trainer, dict):
            trainer['user_profile'] = profile
        else:
            trainer.user_profile = profile
        
        return jsonify({
            'success': True,
            'profile': profile,
            'message': 'Fitness profile created successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@fitness_bp.route('/profile/get', methods=['GET'])
def get_profile():
    """Get user profile"""
    try:
        session_id = session.get('fitness_session_id')
        if not session_id:
            return jsonify({'success': False, 'error': 'No active fitness session'}), 400
        
        trainer = fitness_api.get_or_create_trainer(session_id)
        
        profile = trainer.get('user_profile') if isinstance(trainer, dict) else getattr(trainer, 'user_profile', None)
        
        if not profile:
            return jsonify({
                'success': False,
                'error': 'No fitness profile found'
            }), 404
        
        return jsonify({
            'success': True,
            'profile': profile
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@fitness_bp.route('/profile/update', methods=['PUT'])
def update_profile():
    """Update user profile"""
    try:
        session_id = session.get('fitness_session_id')
        if not session_id:
            return jsonify({'success': False, 'error': 'No active fitness session'}), 400
        
        trainer = fitness_api.get_or_create_trainer(session_id)
        profile = trainer.get('user_profile') if isinstance(trainer, dict) else getattr(trainer, 'user_profile', None)
        
        if not profile:
            return jsonify({
                'success': False,
                'error': 'No fitness profile found to update'
            }), 404
        
        data = request.json
        
        # Update allowed fields
        updatable_fields = ['name', 'age', 'weight', 'height', 'fitness_goal', 'experience', 'equipment', 'limitations']
        
        for field in updatable_fields:
            if field in data:
                if field in ['age', 'weight', 'height']:
                    profile[field] = float(data[field]) if field in ['weight', 'height'] else int(data[field])
                else:
                    profile[field] = data[field]
        
        # Recalculate BMI if weight or height changed
        if 'weight' in data or 'height' in data:
            height_m = profile['height'] / 100
            bmi = profile['weight'] / (height_m ** 2)
            profile['bmi'] = round(bmi, 1)
        
        profile['updated_at'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'profile': profile,
            'message': 'Fitness profile updated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@fitness_bp.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages with fitness AI"""
    try:
        session_id = session.get('fitness_session_id')
        if not session_id:
            return jsonify({'success': False, 'error': 'No active fitness session'}), 400
        
        data = request.json
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message cannot be empty'
            }), 400
        
        trainer = fitness_api.get_or_create_trainer(session_id)
        profile = trainer.get('user_profile') if isinstance(trainer, dict) else getattr(trainer, 'user_profile', None)
        
        if not profile:
            return jsonify({
                'success': False,
                'error': 'Fitness profile not set up. Please create profile first.'
            }), 400
        
        # For now, return a mock response
        # Replace this with actual AI integration
        mock_response = f"Hello {profile['name']}! I understand you want to know about: '{message}'. As your AI fitness trainer, I'm here to help you achieve your goal of {profile['fitness_goal']}. Based on your {profile['experience']} experience level, I can provide personalized guidance."
        
        # Store conversation (in production, use proper storage)
        if 'conversations' not in trainer:
            trainer['conversations'] = []
        
        trainer['conversations'].append({
            'timestamp': datetime.now().isoformat(),
            'user_message': message,
            'ai_response': mock_response
        })
        
        return jsonify({
            'success': True,
            'response': mock_response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@fitness_bp.route('/chat/history', methods=['GET'])
def get_chat_history():
    """Get chat history for current session"""
    try:
        session_id = session.get('fitness_session_id')
        if not session_id:
            return jsonify({'success': False, 'error': 'No active fitness session'}), 400
        
        trainer = fitness_api.get_or_create_trainer(session_id)
        conversations = trainer.get('conversations', [])
        
        return jsonify({
            'success': True,
            'history': conversations,
            'total_messages': len(conversations)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@fitness_bp.route('/workout/generate', methods=['POST'])
def generate_workout():
    """Generate a personalized workout plan"""
    try:
        session_id = session.get('fitness_session_id')
        if not session_id:
            return jsonify({'success': False, 'error': 'No active fitness session'}), 400
        
        trainer = fitness_api.get_or_create_trainer(session_id)
        profile = trainer.get('user_profile') if isinstance(trainer, dict) else getattr(trainer, 'user_profile', None)
        
        if not profile:
            return jsonify({
                'success': False,
                'error': 'Fitness profile not found. Please create profile first.'
            }), 400
        
        data = request.json or {}
        workout_type = data.get('workout_type', 'general')
        duration = data.get('duration', 30)  # minutes
        intensity = data.get('intensity', 'moderate')
        
        # Mock workout generation (replace with AI integration)
        mock_workout = {
            'title': f'{intensity.title()} {workout_type.title()} Workout',
            'duration': duration,
            'intensity': intensity,
            'target_goal': profile['fitness_goal'],
            'exercises': [
                {
                    'name': 'Warm-up',
                    'duration': '5 minutes',
                    'description': 'Light cardio and dynamic stretching'
                },
                {
                    'name': 'Main Workout',
                    'duration': f'{duration - 10} minutes',
                    'description': f'Focused {workout_type} exercises'
                },
                {
                    'name': 'Cool Down',
                    'duration': '5 minutes', 
                    'description': 'Static stretching and breathing'
                }
            ],
            'notes': f'Customized for {profile["experience"]} level',
            'generated_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'workout_plan': mock_workout,
            'parameters': {
                'type': workout_type,
                'duration': duration,
                'intensity': intensity
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@fitness_bp.route('/session/stats', methods=['GET'])
def get_session_stats():
    """Get current session statistics"""
    try:
        session_id = session.get('fitness_session_id')
        if not session_id:
            return jsonify({'success': False, 'error': 'No active fitness session'}), 400
        
        trainer = fitness_api.get_or_create_trainer(session_id)
        conversations = trainer.get('conversations', [])
        
        stats = {
            'session_id': session_id,
            'session_start': trainer.get('created_at'),
            'total_messages': len(conversations),
            'profile_created': trainer.get('user_profile') is not None,
            'last_activity': conversations[-1]['timestamp'] if conversations else trainer.get('created_at')
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@fitness_bp.route('/session/end', methods=['POST'])
def end_session():
    """End current fitness session"""
    try:
        session_id = session.get('fitness_session_id')
        if session_id:
            fitness_api.cleanup_session(session_id)
            session.pop('fitness_session_id', None)
        
        return jsonify({
            'success': True,
            'message': 'Fitness training session ended successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Error handlers for the blueprint
@fitness_bp.errorhandler(404)
def fitness_not_found(error):
    return jsonify({
        'success': False,
        'error': 'Fitness API endpoint not found'
    }), 404

@fitness_bp.errorhandler(500)
def fitness_internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error in fitness API'
    }), 500
