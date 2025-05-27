from flask import Blueprint, request, jsonify, session
from datetime import datetime
import json
import os
from typing import Dict, Any
from models.fitness_trainer import FitnessAITrainer, FitnessMemoryManager  # Import your FitnessAITrainer class

fitness_bp = Blueprint('fitness', __name__,url_prefix='/api/fitness')

# Store active trainers in memory (in production, use Redis or database)
active_trainers = {}
trainer = None

def get_or_create_trainer(session_id: str) -> FitnessAITrainer:
    """Get existing trainer or create new one for session"""
    try:
        if session_id not in active_trainers:
            # Get API key from environment
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables")
            
            print(f"Creating new trainer instance for session {session_id}")
            active_trainers[session_id] = FitnessAITrainer(api_key=api_key)
            print("Trainer instance created successfully")
        
        return active_trainers[session_id]
    except Exception as e:
        print(f"Error in get_or_create_trainer: {str(e)}")
        import traceback
    if session_id not in active_trainers:
        # Initialize with your Groq API key
        active_trainers[session_id] = FitnessAITrainer(api_key=os.getenv("GROQ_API_KEY"))
    return active_trainers[session_id]

@fitness_bp.route('/session/start', methods=['POST'])
def start_session():
    """Start a new fitness training session"""
    try:
        # Check for GROQ_API_KEY
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            print("Error: GROQ_API_KEY not found in environment variables")
            return jsonify({
                'success': False,
                'error': 'GROQ_API_KEY not configured. Please check your .env file.'
            }), 500

        # Generate or get session ID
        if 'fitness_session_id' not in session:
            session['fitness_session_id'] = str(datetime.now().timestamp())
        
        # Initialize trainer
        try:
            trainer = get_or_create_trainer(session['fitness_session_id'])
            print(f"Trainer initialized successfully for session {session['fitness_session_id']}")
        except Exception as trainer_error:
            print(f"Error initializing trainer: {str(trainer_error)}")
            return jsonify({
                'success': False,
                'error': f'Failed to initialize trainer: {str(trainer_error)}'
            }), 500
        
        return jsonify({
            'success': True,
            'session_id': session['fitness_session_id'],
            'message': 'Fitness training session started'
        })
    
    except Exception as e:
        print(f"Error in start_session: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@fitness_bp.route('/profile', methods=['GET', 'POST', 'PUT'])
def create_profile():
    global trainer
    try:
        print("\n=== Profile Endpoint Called ===")
        print(f"Method: {request.method}")
        print(f"Headers: {dict(request.headers)}")
        
        if request.method == 'POST':
            print("\nProcessing POST request")
            data = request.get_json()
            print(f"Request data: {data}")
            
            if not data:
                print("No data received")
                return jsonify({
                    "status": "error",
                    "message": "No data provided"
                }), 400
                
            if not trainer:
                print("Creating new trainer instance")
                trainer = FitnessAITrainer(os.getenv('GROQ_API_KEY'))
            
            print("Creating profile...")
            trainer.create_new_profile(data)
            
            if not trainer.user_profile:
                print("Profile creation failed")
                return jsonify({
                    "status": "error",
                    "message": "Profile creation failed"
                }), 500
                
            print(f"Profile created: {trainer.user_profile}")
            
            response_data = {
                "status": "success",
                "message": "Profile created successfully",
                "profile": trainer.user_profile
            }
            print(f"Sending response: {response_data}")
            
            response = jsonify(response_data)
            response.headers['Content-Type'] = 'application/json'
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            
            print("Response headers set")
            return response
            
        elif request.method == 'PUT':
            print("\nProcessing PUT request")
            if not trainer:
                return jsonify({
                    "success": False,
                    "error": "No active trainer session"
                }), 400
                
            data = request.get_json()
            print(f"Update data received: {data}")
            
            if not data:
                return jsonify({
                    "success": False,
                    "error": "No update data provided"
                }), 400
                
            try:
                # Update profile using the update_profile method
                success = trainer.update_profile(data)
                if not success:
                    print("Profile update failed")
                    return jsonify({
                        "success": False,
                        "error": "Failed to update profile"
                    }), 500
                
                print("Profile updated successfully")
                response = jsonify({
                    "success": True,
                    "message": "Profile updated successfully",
                    "profile": trainer.user_profile
                })
                response.headers['Content-Type'] = 'application/json'
                response.headers['Access-Control-Allow-Origin'] = '*'
                return response
                
            except Exception as e:
                print(f"Error updating profile: {str(e)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                return jsonify({
                    "success": False,
                    "error": f"Failed to update profile: {str(e)}"
                }), 500
            
        elif request.method == 'GET':
            print("\nProcessing GET request")
            if trainer and trainer.user_profile:
                print(f"Returning profile: {trainer.user_profile}")
                response = jsonify(trainer.user_profile)
                response.headers['Content-Type'] = 'application/json'
                response.headers['Access-Control-Allow-Origin'] = '*'
                return response
                
            print("No profile found")
            return jsonify({
                "status": "error",
                "message": "No profile exists"
            }), 404
            
        elif request.method == 'OPTIONS':
            print("\nProcessing OPTIONS request")
            response = jsonify({"status": "ok"})
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            return response
            
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@fitness_bp.route('/profile/status', methods=['GET'])
def profile_status():
    """Check profile and memory initialization status"""
    try:
        print("\n=== Profile Status Check ===")
        if not trainer:
            print("No trainer instance found")
            return jsonify({
                'success': False,
                'error': 'No active trainer session'
            }), 400
        
        if not hasattr(trainer, 'user_profile'):
            print("No user profile found")
            return jsonify({
                'success': False,
                'error': 'Profile not created'
            }), 404
        
        # Try to initialize memory if not already initialized
        if not hasattr(trainer, 'memory_manager'):
            try:
                print(f"Initializing memory manager for user {trainer.user_profile.get('name', 'unknown')}...")
                trainer.memory_manager = FitnessMemoryManager(trainer.client, trainer.user_profile)
                # Verify memory manager is properly initialized
                if not trainer.memory_manager or not hasattr(trainer.memory_manager, 'collection'):
                    raise Exception("Memory manager initialization incomplete")
                memory_initialized = True
                print("Memory manager initialized successfully")
            except Exception as e:
                print(f"Error initializing memory manager: {str(e)}")
                print(f"Error type: {type(e).__name__}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                memory_initialized = False
                error_message = str(e)
        else:
            # Verify memory manager is still valid
            try:
                if not trainer.memory_manager or not hasattr(trainer.memory_manager, 'collection'):
                    raise Exception("Memory manager not properly initialized")
                memory_initialized = True
                error_message = None
            except Exception as e:
                memory_initialized = False
                error_message = str(e)
        
        response_data = {
            'success': True,
            'profile': trainer.user_profile,
            'memory_initialized': memory_initialized,
            'error': error_message
        }
        print(f"Sending response: {response_data}")
        
        response = jsonify(response_data)
        response.headers['Content-Type'] = 'application/json'
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
        
    except Exception as e:
        print(f"Error in profile_status: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
        
        # Check if memory manager exists and is ready
        if not hasattr(trainer, 'memory_manager'):
            # Try to initialize memory manager if it doesn't exist
            try:
                trainer.memory_manager = FitnessMemoryManager(trainer.client, trainer.user_profile)
            except Exception as e:
                print(f"Error initializing memory manager: {e}")
                return jsonify({
                    'success': False,
                    'error': 'AI trainer is still initializing. Please try again in a few seconds.'
                }), 503  # Service Unavailable
        
        try:
            response = trainer.get_ai_response(message)
            return jsonify({
                'success': True,
                'response': response,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            print(f"Error getting AI response: {e}")
            return jsonify({
                'success': False,
                'error': 'AI trainer is having trouble processing your request. Please try again.'
            }), 503
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
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
        print("\n=== Ending Session ===")
        if 'fitness_session_id' not in session:
            return jsonify({
                'success': False,
                'error': 'No active session found'
            }), 400
            
        session_id = session['fitness_session_id']
        print(f"Ending session: {session_id}")
        
        if session_id in active_trainers:
            trainer = active_trainers[session_id]
            # Save session data if requested
            should_save = False
            try:
                if request.is_json and request.json:
                    should_save = request.json.get('save', False)
            except Exception as e:
                print(f"Warning: Could not parse request JSON: {str(e)}")
            
            if should_save:
                try:
                    trainer.save_session_data()
                    print("Session data saved successfully")
                except Exception as e:
                    print(f"Warning: Failed to save session data: {str(e)}")
            
            # Clean up trainer instance
            try:
                if hasattr(trainer, 'memory_manager'):
                    trainer.memory_manager.clear_session_memory()
                del active_trainers[session_id]
                print("Trainer instance cleaned up")
            except Exception as e:
                print(f"Warning: Error during trainer cleanup: {str(e)}")
        
        # Clear session
        session.pop('fitness_session_id', None)
        print("Session cleared")
        
        return jsonify({
            'success': True,
            'message': 'Session ended successfully'
        })
        
    except Exception as e:
        print(f"Error ending session: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'Failed to end session: {str(e)}'
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

# Add a simple status check endpoint
@fitness_bp.route('/status', methods=['GET'])
def status():
    """Simple status check endpoint"""
    return jsonify({
        'success': True,
        'message': 'Fitness API is running'
    })
