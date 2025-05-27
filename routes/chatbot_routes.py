from flask import Blueprint, request, jsonify, session
from datetime import datetime
import json
import os
from typing import Dict, Any
from models.fitness_trainer import FitnessAITrainer, FitnessMemoryManager  # Import your FitnessAITrainer class

fitness_bp = Blueprint('fitness', __name__)

# Store active trainers in memory (in production, use Redis or database)
active_trainers = {}

def get_or_create_trainer(session_id: str) -> FitnessAITrainer:
    """Get existing trainer or create new one for session"""
    if session_id not in active_trainers:
        # Initialize with your Groq API key
        active_trainers[session_id] = FitnessAITrainer(api_key=os.getenv("GROQ_API_KEY"))
    return active_trainers[session_id]

@fitness_bp.route('/session/start', methods=['POST'])
def start_session():
    """Start a new fitness training session"""
    try:
        # Generate or get session ID
        if 'fitness_session_id' not in session:
            session['fitness_session_id'] = str(datetime.now().timestamp())
        
        # Initialize trainer
        trainer = get_or_create_trainer(session['fitness_session_id'])
        
        return jsonify({
            'success': True,
            'session_id': session['fitness_session_id'],
            'message': 'Fitness training session started'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@fitness_bp.route('/profile', methods=['POST'])
def create_profile():
    """Create or update user fitness profile"""
    
    if 'fitness_session_id' not in session:
        return jsonify({'success': False, 'error': 'No active session'}), 400
    
    data = request.json
    trainer = get_or_create_trainer(session['fitness_session_id'])
    
    # Required fields
    required = ['name', 'age', 'weight', 'height', 'fitness_goal', 'experience']
    if not all(field in data for field in required):
        return jsonify({
            'success': False,
            'error': f'Missing required fields: {required}'
        }), 400
    
    # Set up profile
    trainer.user_profile = {
        'name': data['name'],
        'age': int(data['age']),
        'weight': float(data['weight']),
        'height': float(data['height']),
        'fitness_goal': data['fitness_goal'],
        'experience': data['experience'],
        'equipment': data.get('equipment', ''),
        'limitations': data.get('limitations', ''),
        'bmi': round(float(data['weight']) / ((float(data['height'])/100)**2, 1))
    }
    
    # Initialize memory system
    trainer.memory_manager = FitnessMemoryManager(trainer.client, trainer.user_profile)
    
    return jsonify({
        'success': True,
        'profile': trainer.user_profile
    })
        
    # except Exception as e:
    #     return jsonify({
    #         'success': False,
    #         'error': str(e)
    #     }), 500

@fitness_bp.route('/chat', methods=['POST'])
def chat():
    """Handle chat with fitness AI"""
    try:
        if 'fitness_session_id' not in session:
            return jsonify({'success': False, 'error': 'No active session'}), 400
        
        data = request.json
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message cannot be empty'
            }), 400
        
        trainer = get_or_create_trainer(session['fitness_session_id'])
        
        if not hasattr(trainer, 'memory_manager'):
            return jsonify({
                'success': False,
                'error': 'Profile not set up'
            }), 400
        
        response = trainer.get_ai_response(message)
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@fitness_bp.route('/workout/generate', methods=['POST'])
def generate_workout():
    """Generate personalized workout"""
    try:
        if 'fitness_session_id' not in session:
            return jsonify({'success': False, 'error': 'No active session'}), 400
        
        trainer = get_or_create_trainer(session['fitness_session_id'])
        
        if not hasattr(trainer, 'memory_manager'):
            return jsonify({
                'success': False,
                'error': 'Profile not set up'
            }), 400
        
        data = request.json or {}
        workout_type = data.get('type', 'general')
        duration = data.get('duration', 30)
        intensity = data.get('intensity', 'moderate')
        
        # Generate workout prompt
        prompt = f"""Generate a detailed {intensity} {workout_type} workout plan for {duration} minutes.
        User profile:
        - Goal: {trainer.user_profile['fitness_goal']}
        - Experience: {trainer.user_profile['experience']}
        - Equipment: {trainer.user_profile['equipment']}
        - Limitations: {trainer.user_profile['limitations']}
        
        Provide warmup, main exercises, and cooldown."""
        
        response = trainer.get_ai_response(prompt)
        
        return jsonify({
            'success': True,
            'workout': response,
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

@fitness_bp.route('/session/end', methods=['POST'])
def end_session():
    """End current session"""
    try:
        if 'fitness_session_id' in session:
            session_id = session['fitness_session_id']
            if session_id in active_trainers:
                # Save session data if needed
                if request.json and request.json.get('save', False):
                    active_trainers[session_id].save_session_data()
                del active_trainers[session_id]
            session.pop('fitness_session_id', None)
        
        return jsonify({
            'success': True,
            'message': 'Session ended'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@fitness_bp.route('/session/status', methods=['GET'])
def session_status():
    """Get session status"""
    try:
        if 'fitness_session_id' not in session:
            return jsonify({'active': False}), 200
        
        trainer = active_trainers.get(session['fitness_session_id'])
        
        status = {
            'active': True,
            'session_id': session['fitness_session_id'],
            'profile_created': hasattr(trainer, 'memory_manager') if trainer else False,
            'start_time': trainer.session_start_time.isoformat() if trainer else None
        }
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
