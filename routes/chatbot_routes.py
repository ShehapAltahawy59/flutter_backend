import traceback
from flask import Blueprint, request, jsonify, session
from datetime import datetime
import json
import os
from typing import Dict, Any
from models.fitness_trainer import FitnessAITrainer, FitnessMemoryManager  # Import your FitnessAITrainer class
from models.workout import Workout
import re

fitness_bp = Blueprint('fitness', __name__,url_prefix='/api/fitness')

# Store active trainers in memory (in production, use Redis or database)
active_trainers = {}
trainer = None

def get_or_create_trainer(session_id: str) -> FitnessAITrainer:
    """Get existing trainer or create new one for session"""
    try:
        print(f"\n=== Getting/Creating Trainer for Session {session_id} ===")
        
        # Check if we have a valid API key
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("GROQ_API_KEY not found in environment variables")
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        # Check if trainer exists for this session
        if session_id in active_trainers:
            trainer = active_trainers[session_id]
            print(f"Found existing trainer for session {session_id}")
            
            # Verify trainer is still valid
            if not hasattr(trainer, 'initialized') or not trainer.initialized:
                print("Existing trainer not properly initialized, creating new instance")
                del active_trainers[session_id]
            elif not hasattr(trainer, 'memory_manager') or not trainer.memory_manager:
                print("Existing trainer missing memory manager, creating new instance")
                del active_trainers[session_id]
            elif not trainer.memory_manager.is_initialized():
                print("Existing trainer's memory manager not initialized, creating new instance")
                del active_trainers[session_id]
            else:
                print("Existing trainer is valid")
                return trainer
        
        # Create new trainer instance
        print(f"Creating new trainer instance for session {session_id}")
        trainer = FitnessAITrainer(api_key=api_key)
        
        # Verify trainer was created successfully
        if not hasattr(trainer, 'initialized') or not trainer.initialized:
            print("Failed to initialize trainer")
            raise ValueError("Failed to initialize trainer")
        
        # Initialize memory manager if needed
        if not hasattr(trainer, 'memory_manager') or not trainer.memory_manager:
            print("Initializing memory manager...")
            trainer.memory_manager = FitnessMemoryManager(trainer.client, trainer.user_profile)
            print("Memory manager initialized")
        
        # Verify memory manager initialization
        if not trainer.memory_manager.is_initialized():
            print("Failed to initialize memory manager")
            raise ValueError("Failed to initialize memory manager")
        
        # Store trainer in active trainers
        active_trainers[session_id] = trainer
        print("Trainer instance created and stored successfully")
        
        return trainer
        
    except Exception as e:
        print(f"Error in get_or_create_trainer: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise

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
    """Check the status of the current profile and memory manager"""
    try:
        print("\n=== Profile Status Check ===")
        
        # Check if we have a valid session
        if not session.get('fitness_session_id'):
            print("No active session found")
            return jsonify({
                'status': 'error',
                'message': 'No active session found',
                'data': {
                    'profile_exists': False,
                    'memory_initialized': False,
                    'debug_info': {
                        'session_id': None,
                        'has_memory_manager': False,
                        'has_client': False
                    }
                }
            }), 404

        # Get the trainer instance
        try:
            trainer = get_or_create_trainer(session['fitness_session_id'])
            print(f"Trainer instance retrieved for session {session['fitness_session_id']}")
        except Exception as e:
            print(f"Error getting trainer instance: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'Failed to get trainer instance: {str(e)}',
                'data': {
                    'profile_exists': False,
                    'memory_initialized': False,
                    'debug_info': {
                        'session_id': session.get('fitness_session_id'),
                        'has_memory_manager': False,
                        'has_client': False,
                        'error': str(e)
                    }
                }
            }), 500

        # Check if we have a valid API key
        if not os.getenv('GROQ_API_KEY'):
            print("GROQ_API_KEY not found in environment")
            return jsonify({
                'status': 'error',
                'message': 'GROQ_API_KEY not found in environment variables',
                'data': {
                    'profile_exists': bool(trainer.user_profile),
                    'memory_initialized': False,
                    'debug_info': {
                        'session_id': session.get('fitness_session_id'),
                        'has_memory_manager': hasattr(trainer, 'memory_manager'),
                        'has_client': hasattr(trainer, 'client'),
                        'api_key_set': False
                    }
                }
            }), 401

        # Check trainer initialization
        if not hasattr(trainer, 'initialized') or not trainer.initialized:
            print("Trainer not fully initialized")
            return jsonify({
                'status': 'initializing',
                'message': 'AI trainer is still initializing',
                'data': {
                    'profile_exists': bool(trainer.user_profile),
                    'memory_initialized': False,
                    'debug_info': {
                        'session_id': session.get('fitness_session_id'),
                        'has_memory_manager': hasattr(trainer, 'memory_manager'),
                        'has_client': hasattr(trainer, 'client'),
                        'api_key_set': True,
                        'trainer_initialized': False
                    }
                }
            }), 503

        # Verify memory manager initialization
        if not hasattr(trainer, 'memory_manager') or not trainer.memory_manager:
            print("Memory manager not created")
            return jsonify({
                'status': 'error',
                'message': 'Memory manager not created',
                'data': {
                    'profile_exists': bool(trainer.user_profile),
                    'memory_initialized': False,
                    'debug_info': {
                        'session_id': session.get('fitness_session_id'),
                        'has_memory_manager': False,
                        'has_client': hasattr(trainer, 'client'),
                        'api_key_set': True,
                        'trainer_initialized': True
                    }
                }
            }), 500

        if not trainer.memory_manager.is_initialized():
            print("Memory manager not initialized")
            return jsonify({
                'status': 'error',
                'message': 'Memory manager not properly initialized',
                'data': {
                    'profile_exists': bool(trainer.user_profile),
                    'memory_initialized': False,
                    'debug_info': {
                        'session_id': session.get('fitness_session_id'),
                        'has_memory_manager': True,
                        'has_client': hasattr(trainer, 'client'),
                        'api_key_set': True,
                        'trainer_initialized': True,
                        'memory_manager_initialized': False
                    }
                }
            }), 500

        # Verify client is properly initialized
        if not hasattr(trainer, 'client') or not trainer.client:
            print("Client not properly initialized")
            return jsonify({
                'status': 'error',
                'message': 'AI client not properly initialized',
                'data': {
                    'profile_exists': bool(trainer.user_profile),
                    'memory_initialized': True,
                    'debug_info': {
                        'session_id': session.get('fitness_session_id'),
                        'has_memory_manager': True,
                        'has_client': False,
                        'api_key_set': True,
                        'trainer_initialized': True,
                        'memory_manager_initialized': True
                    }
                }
            }), 500

        # All checks passed
        print("Profile and memory manager are properly initialized")
        response_data = {
            'status': 'success',
            'message': 'Profile and memory manager are properly initialized',
            'data': {
                'profile_exists': bool(trainer.user_profile),
                'memory_initialized': True,
                'debug_info': {
                    'session_id': session.get('fitness_session_id'),
                    'has_memory_manager': True,
                    'has_client': True,
                    'api_key_set': True,
                    'trainer_initialized': True,
                    'memory_manager_initialized': True
                }
            }
        }
        print(f"Status response: {response_data}")
        return jsonify(response_data), 200

    except ValueError as e:
        error_msg = str(e)
        print(f"ValueError in profile status check: {error_msg}")
        if "invalid_api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            return jsonify({
                'status': 'error',
                'message': error_msg,
                'data': {
                    'profile_exists': False,
                    'memory_initialized': False,
                    'debug_info': {
                        'session_id': session.get('fitness_session_id'),
                        'has_memory_manager': False,
                        'has_client': False,
                        'api_key_set': bool(os.getenv('GROQ_API_KEY')),
                        'error_type': 'api_key_error'
                    }
                }
            }), 401
        raise

    except Exception as e:
        print(f"Error in profile status check: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': f'Error checking profile status: {str(e)}',
            'data': {
                'profile_exists': False,
                'memory_initialized': False,
                'debug_info': {
                    'session_id': session.get('fitness_session_id'),
                    'has_memory_manager': False,
                    'has_client': False,
                    'api_key_set': bool(os.getenv('GROQ_API_KEY')),
                    'error_type': 'unknown_error',
                    'error_details': str(e)
                }
            }
        }), 500

@fitness_bp.route('/chat', methods=['POST'])
def chat():
    """Handle chat with fitness AI"""
    try:
        print("\n=== Chat Request ===")
        
        # Check for active session
        if 'fitness_session_id' not in session:
            print("No active session found")
            return jsonify({
                'success': False,
                'error': 'No active session'
            }), 400
        
        # Get request data
        data = request.json
        if not data:
            print("No request data provided")
            return jsonify({
                'success': False,
                'error': 'No request data provided'
            }), 400
            
        message = data.get('message', '').strip()
        if not message:
            print("Empty message received")
            return jsonify({
                'success': False,
                'error': 'Message cannot be empty'
            }), 400
        
        # Get trainer instance
        try:
            trainer = get_or_create_trainer(session['fitness_session_id'])
            print(f"Trainer instance retrieved for session {session['fitness_session_id']}")
        except Exception as e:
            print(f"Error getting trainer instance: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Failed to get trainer instance: {str(e)}'
            }), 500
        
        # Check trainer initialization
        if not hasattr(trainer, 'initialized') or not trainer.initialized:
            print("Trainer not fully initialized")
            return jsonify({
                'success': False,
                'error': 'AI trainer is still initializing',
                'status': 'initializing'
            }), 503
        
        # Check memory manager
        if not hasattr(trainer, 'memory_manager') or not trainer.memory_manager:
            print("Memory manager not created")
            try:
                print("Attempting to initialize memory manager...")
                trainer.memory_manager = FitnessMemoryManager(trainer.client, trainer.user_profile)
                print("Memory manager initialized successfully")
            except Exception as e:
                print(f"Failed to initialize memory manager: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': 'Failed to initialize memory manager',
                    'details': str(e)
                }), 500
        
        # Verify memory manager initialization
        if not trainer.memory_manager.is_initialized():
            print("Memory manager not properly initialized")
            return jsonify({
                'success': False,
                'error': 'Memory manager not properly initialized'
            }), 500
        
        # Get AI response
        try:
            print("Getting AI response...")
            response = trainer.get_ai_response(message)
            print("AI response received successfully")
            
            return jsonify({
                'success': True,
                'response': response,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Error getting AI response: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': f'Failed to get AI response: {str(e)}'
            }), 500
        
    except Exception as e:
        print(f"Unexpected error in chat endpoint: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@fitness_bp.route('/workout', methods=['POST'])
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
        
        # After generating the workout
        trainer.memory_manager.add_message(
            role="user",
            content=f"Requested a workout plan with profile: {data}"
        )
        trainer.memory_manager.add_message(
            role="assistant",
            content=f"Generated workout plan: {response}"
        )
        
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
        print(f"Error generating workout: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'Failed to generate workout: {str(e)}'
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

def summarize_workout(workout_data):
    # Simple summary: day titles and first exercise of each day
    days = workout_data.get('plan', {}).get('details', {}).get('days', [])
    summary_lines = []
    for day in days:
        title = day.get('title', '')
        exercises = day.get('exercises', [])
        if exercises:
            summary_lines.append(f"{title}: {exercises[0]}")
        else:
            summary_lines.append(title)
    return " | ".join(summary_lines)

@fitness_bp.route('/generate_workout', methods=['POST'])
def analyze_profile():
    """Analyze user profile and return AI response using memory based on user_id. Also save and retrieve workouts from fitness_data."""
    try:
        print("\n=== Profile Analysis Endpoint Called ===")
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No profile data provided"
            }), 400
        
        # Validate required fields
        required_fields = ['user_id', 'name', 'age', 'weight', 'height', 'fitness_goal', 'experience', 'equipment', 'limitations']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"{field} is required"
                }), 400
        
        # Check for GROQ_API_KEY
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            return jsonify({
                "success": False,
                "error": "GROQ_API_KEY not configured"
            }), 500
        
        # Use user_id as session_id for memory
        user_id = str(data['user_id'])
        trainer = get_or_create_trainer(user_id)
        
        # Create or update profile in memory
        trainer.create_new_profile(data)
        
        if not trainer.user_profile:
            return jsonify({
                "success": False,
                "error": "Failed to create profile"
            }), 500
        
        # Retrieve previous workouts for the user
        previous_workouts = Workout.get_user_workouts(user_id)
        for w in previous_workouts:
            w['_id'] = str(w['_id'])
        # Get last 3 summaries
        summaries = [w.get('summary', '') for w in previous_workouts if w.get('summary')]
        recent_summaries = summaries[:3]
        print(f"[DEBUG] Recent workout summaries to include in prompt: {recent_summaries}")
        
        # Generate workout using AI and parse response
        workout_type = "general"
        duration = 30
        intensity = "moderate"
        prompt = f"""Create a {intensity} {workout_type} workout plan for {duration} minutes.\n\nUser profile:\n- Goal: {trainer.user_profile['fitness_goal']}\n- Experience: {trainer.user_profile['experience']}\n- Equipment: {trainer.user_profile['equipment']}\n- Limitations: {trainer.user_profile['limitations']}\n"""
        if recent_summaries:
            prompt += "\nHere are summaries of my recent workouts:\n"
            for i, s in enumerate(recent_summaries, 1):
                prompt += f"Workout {i}: {s}\n"
            prompt += "Please avoid repeating the same exercises and make the new plan progressive.\n"
            print("[DEBUG] Summaries were included in the prompt.")
        else:
            print("[DEBUG] No summaries included in the prompt.")
        prompt += """\nPlease provide a structured workout plan with the following format:\n\nPLAN TITLE: [Workout Plan Title]\nDURATION: [Duration in minutes]\nINTENSITY: [Intensity level]\n\nDAY 1 - [Day Title]:\n• [Exercise 1 with sets and reps]\n• [Exercise 2 with sets and reps]\n• [Exercise 3 with sets and reps]\n• [Exercise 4 with sets and reps]\n• [Exercise 5 with sets and reps]\n\nDAY 2 - [Day Title]:\n• [Exercise 1 with sets and reps]\n• [Exercise 2 with sets and reps]\n• [Exercise 3 with sets and reps]\n• [Exercise 4 with sets and reps]\n\nDAY 3 - [Day Title]:\n• [Exercise 1 with sets and reps]\n• [Exercise 2 with sets and reps]\n• [Exercise 3 with sets and reps]\n• [Exercise 4 with sets and reps]\n\nInclude warm-up and cool-down exercises for each day. Provide 3-4 days of workouts based on the user's fitness goal and experience level."""
        print(f"[DEBUG] Final prompt sent to AI:\n{prompt}")
        workout_response = trainer.get_ai_response(prompt)
        print(workout_response)
        workout_data = _parse_ai_workout_response(workout_response, intensity, workout_type, duration)
        
        # Calculate BMI
        height_m = data['height'] / 100
        bmi = data['weight'] / (height_m * height_m)
        
        # Save the generated workout in fitness_data with summary
        summary = summarize_workout(workout_data)
        Workout.create_workout({
            "user_id": user_id,
            "profile": trainer.user_profile,
            "workout": workout_data,
            "summary": summary,
            "created_at": datetime.utcnow()
        })
        
        return jsonify({
            "success": True,
            "profile": trainer.user_profile,
            "bmi": round(bmi, 2),
            "workout": workout_data,
            "parameters": {
                'type': workout_type,
                'duration': duration,
                'intensity': intensity
            },
            "message": "Profile analyzed and workout plan generated successfully (with memory)"
        }), 200
        
    except Exception as e:
        print(f"Error in analyze_profile: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def _parse_ai_workout_response(ai_response: str, intensity: str, workout_type: str, duration: int) -> dict:
    """Parse AI workout response and convert to structured format (robust for markdown and flexible AI output)"""
    try:
        lines = ai_response.split('\n')
        days = []
        current_day = None
        current_exercises = []

        for line in lines:
            line = line.strip()
            # Remove markdown bold and bullets
            line = re.sub(r'^\*+\s*', '', line)
            line = re.sub(r'\*+$', '', line)
            line = line.strip()

            # Match day headers like "DAY 1 - Upper Body", with or without bold, with or without colon
            day_match = re.match(r'(DAY\s*\d+\s*-\s*.+)', line, re.IGNORECASE)
            if day_match:
                # Save previous day if exists
                if current_day and current_exercises:
                    days.append({
                        "title": current_day,
                        "exercises": current_exercises
                    })
                current_day = day_match.group(1)
                current_exercises = []
                continue

            # If line is not empty and not a day header, treat as exercise
            if line and current_day:
                current_exercises.append(line)

        # Add the last day
        if current_day and current_exercises:
            days.append({
                "title": current_day,
                "exercises": current_exercises
            })

        # If no days were parsed, create a default structure
        if not days:
            days = [
                {
                    "title": "Day 1 - Full Body Workout",
                    "exercises": [
                        "Warm-up: 5 minutes light cardio",
                        "Squats: 3 sets x 12-15 reps",
                        "Push-ups: 3 sets x 10-12 reps",
                        "Dumbbell rows: 3 sets x 12 reps per arm",
                        "Plank: 3 sets x 30 seconds",
                        "Cool-down: 5 minutes stretching"
                    ]
                }
            ]

        return {
            "plan": {
                "title": f"{intensity.title()} {workout_type.title()} Workout Plan",
                "duration": f"{duration} minutes",
                "intensity": intensity,
                "details": {
                    "days": days
                }
            }
        }

    except Exception as e:
        print(f"Error parsing AI response: {str(e)}")
        # Return default structure if parsing fails
        return {
            "plan": {
                "title": f"{intensity.title()} {workout_type.title()} Workout Plan",
                "duration": f"{duration} minutes",
                "intensity": intensity,
                "details": {
                    "days": [
                        {
                            "title": "Day 1 - Full Body Workout",
                            "exercises": [
                                "Warm-up: 5 minutes light cardio",
                                "Squats: 3 sets x 12-15 reps",
                                "Push-ups: 3 sets x 10-12 reps",
                                "Dumbbell rows: 3 sets x 12 reps per arm",
                                "Plank: 3 sets x 30 seconds",
                                "Cool-down: 5 minutes stretching"
                            ]
                        }
                    ]
                }
            }
        }
