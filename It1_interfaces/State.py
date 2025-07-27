from .Command import Command
from .Moves import Moves
from .Graphics import Graphics  
from .Physics import Physics
from typing import Dict
import time
import copy
import pathlib

def extract_piece_type_from_sprites_path(sprites_folder_path):
    """Extract piece type from sprites folder path like 'pieces/PW/states/idle/sprites'"""
    if isinstance(sprites_folder_path, str):
        path = pathlib.Path(sprites_folder_path)
    else:
        path = sprites_folder_path
    
    # Extract piece type from path structure: pieces/{PIECE_TYPE}/states/{STATE}/sprites
    parts = path.parts
    if len(parts) >= 4 and parts[-3] == 'states' and parts[-1] == 'sprites':
        piece_type = parts[-4]
        return piece_type
    return None

def construct_sprites_path_for_state(current_sprites_folder, target_state_name):
    """Construct correct sprites folder path for target state"""
    piece_type = extract_piece_type_from_sprites_path(current_sprites_folder)
    if piece_type:
        # Construct: pieces/{piece_type}/states/{target_state_name}/sprites
        return pathlib.Path("pieces") / piece_type / "states" / target_state_name / "sprites"
    return current_sprites_folder  # Fallback to current if extraction fails

class State:
    def __init__(self, moves: Moves, graphics: Graphics, physics: Physics, state_name: str = "idle"):
        """Initialize state with moves, graphics, and physics components."""
        self.moves = moves
        self.graphics = graphics
        self.physics = physics
        self.transitions: Dict[str, "State"] = {}
        self.state_start_time = 0
        self.current_command = None
        
        # State-specific properties
        self.is_rest_state = False
        self.rest_duration_ms = 0

        # State name identifier
        self.state = state_name
        
        print(f"[DEBUG] State initialized with name: {self.state}")

    def copy(self) -> "State":
        """Create a deep copy of this state."""
        print(f"[DEBUG] 🔄 State.copy() called for state '{self.state}'")
        new_graphics = self.graphics.copy()
        # Fix: Ensure the copied graphics has the correct state_name
        print(f"[DEBUG] 🔄 Before fix: new_graphics.state_name = '{new_graphics.state_name}'")
        new_graphics.state_name = self.state
        print(f"[DEBUG] 🔄 After fix: new_graphics.state_name = '{new_graphics.state_name}'")
        new_physics = self.physics.copy()
    
        new_state = State(self.moves, new_graphics, new_physics, self.state)
        new_state.transitions = {}  # Transitions will be set up separately
        new_state.is_rest_state = self.is_rest_state
        new_state.rest_duration_ms = self.rest_duration_ms
    
        return new_state

    def set_transition(self, event: str, target: "State"):
        """Set a transition from this state to another state on an event."""
        self.transitions[event] = target
        print(f"[DEBUG] Set transition: {self.state} --{event}--> {target.state}")

    def reset(self, cmd: Command):
        """Reset the state with a new command."""
        self.current_command = cmd
        self.state_start_time = cmd.timestamp
        self.graphics.reset(cmd)
        self.physics.reset(cmd)
        print(f"[DEBUG] State '{self.state}' reset with command: {cmd.type}")

    def can_transition(self, now_ms: int) -> bool:
        """Check if the state can transition."""
        if self.is_rest_state:
            elapsed = now_ms - self.state_start_time
            can_transition = elapsed >= self.rest_duration_ms
            print(f"[DEBUG] Rest state '{self.state}' can transition: {can_transition} (elapsed: {elapsed}ms, required: {self.rest_duration_ms}ms)")
            return can_transition
        else:
            # Non-rest states can always transition
            return True

    def get_state_after_command(self, cmd: Command, now_ms: int) -> "State":
        """Get the next state after processing a command."""
        if not self.can_transition(now_ms):
            print(f"[DEBUG] State '{self.state}' cannot transition yet (in cooldown/rest)")
            return self  # Stay in current state if can't transition
            
        if cmd.type in self.transitions:
            template_state = self.transitions[cmd.type]
            print(f"[DEBUG] State '{self.state}' transitioning to '{template_state.state}' via command '{cmd.type}'")
            
            # CRITICAL: Create NEW instance instead of using template
            next_state = self.copy()
            next_state.state = template_state.state
            next_state.is_rest_state = template_state.is_rest_state
            next_state.rest_duration_ms = template_state.rest_duration_ms
            next_state.transitions = template_state.transitions.copy()
            
            # Create NEW Graphics object with correct state_name
            from .GraphicsFactory import GraphicsFactory
            
            # Construct correct sprites folder path for target state
            correct_sprites_folder = construct_sprites_path_for_state(
                template_state.graphics.sprites_folder, 
                template_state.state
            )
            print(f"[DEBUG] 🎯 Manual transition: Corrected sprites folder from '{template_state.graphics.sprites_folder}' to '{correct_sprites_folder}' for state '{template_state.state}'")
            
            next_state.graphics = GraphicsFactory.create(
                correct_sprites_folder,  # Use corrected sprites folder
                {},  # Empty config - use defaults
                template_state.graphics.cell_size,  # Use same cell size
                template_state.state  # CRITICAL: Pass the correct state name!
            )
            print(f"[DEBUG] Created NEW graphics for state '{template_state.state}' with state_name: '{next_state.graphics.state_name}'")
            print(f"[DEBUG] New graphics object ID: {id(next_state.graphics)}")
            
            # CRITICAL: Copy current physics state to the next state
            if hasattr(self.physics, 'current_cell'):
                next_state.physics.current_cell = self.physics.current_cell
                next_state.physics.target_cell = self.physics.target_cell
                print(f"[DEBUG] Copied position {self.physics.current_cell} to next state '{next_state.state}'")
            
            next_state.reset(cmd)
            return next_state
        else:
            print(f"[DEBUG] State '{self.state}' has no transition for command '{cmd.type}'. Available: {list(self.transitions.keys())}")
            return self

    def update(self, now_ms: int) -> "State":
        """Update the state based on current time."""
        self.graphics.update(now_ms)
        movement_complete = self.physics.update(now_ms)
        
        # Check if movement was completed and we should transition
        if movement_complete and "complete" in self.transitions:
            print(f"[DEBUG] Movement completed in state '{self.state}', transitioning via 'complete'")
            template_state = self.transitions["complete"]
            
            # CRITICAL: Create NEW instance instead of using template
            next_state = self.copy()
            next_state.state = template_state.state
            next_state.is_rest_state = template_state.is_rest_state
            next_state.rest_duration_ms = template_state.rest_duration_ms
            next_state.transitions = template_state.transitions.copy()
            
            # Create NEW Graphics object with correct state_name
            from .GraphicsFactory import GraphicsFactory
            
            # Construct correct sprites folder path for target state
            correct_sprites_folder = construct_sprites_path_for_state(
                template_state.graphics.sprites_folder, 
                template_state.state
            )
            print(f"[DEBUG] 🎯 Auto-complete transition: Corrected sprites folder from '{template_state.graphics.sprites_folder}' to '{correct_sprites_folder}' for state '{template_state.state}'")
            
            next_state.graphics = GraphicsFactory.create(
                correct_sprites_folder,  # Use corrected sprites folder
                {},  # Empty config - use defaults
                template_state.graphics.cell_size,  # Use same cell size
                template_state.state  # CRITICAL: Pass the correct state name!
            )
            print(f"[DEBUG] Created NEW graphics for auto-transition '{template_state.state}' with state_name: '{next_state.graphics.state_name}'")
            
            # CRITICAL: Copy current physics state to the next state
            if hasattr(self.physics, 'current_cell'):
                next_state.physics.current_cell = self.physics.current_cell
                next_state.physics.target_cell = self.physics.target_cell
                print(f"[DEBUG] Copied position {self.physics.current_cell} to next state '{next_state.state}'")
            
            # Create a completion command
            completion_cmd = Command(now_ms, "", "complete", [])
            next_state.reset(completion_cmd)
            return next_state

        # Check for automatic transitions (like rest state expiring)
        if self.is_rest_state and self.can_transition(now_ms):
            if "timeout" in self.transitions:
                print(f"[DEBUG] Rest state '{self.state}' timeout, transitioning to '{self.transitions['timeout'].state}'")
                template_state = self.transitions["timeout"]
                
                # CRITICAL: Create NEW instance instead of using template
                next_state = self.copy()
                next_state.state = template_state.state
                next_state.is_rest_state = template_state.is_rest_state
                next_state.rest_duration_ms = template_state.rest_duration_ms
                next_state.transitions = template_state.transitions.copy()
                
                # Create NEW Graphics object with correct state_name
                from .GraphicsFactory import GraphicsFactory
                
                # Construct correct sprites folder path for target state
                correct_sprites_folder = construct_sprites_path_for_state(
                    template_state.graphics.sprites_folder, 
                    template_state.state
                )
                print(f"[DEBUG] 🎯 Timeout transition: Corrected sprites folder from '{template_state.graphics.sprites_folder}' to '{correct_sprites_folder}' for state '{template_state.state}'")
                
                next_state.graphics = GraphicsFactory.create(
                    correct_sprites_folder,  # Use corrected sprites folder
                    {},  # Empty config - use defaults
                    template_state.graphics.cell_size,  # Use same cell size
                    template_state.state  # CRITICAL: Pass the correct state name!
                )
                print(f"[DEBUG] Created NEW graphics for timeout-transition '{template_state.state}' with state_name: '{next_state.graphics.state_name}'")
                
                # CRITICAL: Copy current physics state to the next state
                if hasattr(self.physics, 'current_cell'):
                    next_state.physics.current_cell = self.physics.current_cell
                    next_state.physics.target_cell = self.physics.target_cell
                    print(f"[DEBUG] Copied position {self.physics.current_cell} to next state '{next_state.state}'")
                
                # Create a timeout command for the transition
                timeout_cmd = Command(now_ms, "", "timeout", [])
                next_state.reset(timeout_cmd)
                return next_state
            else:
                print(f"[DEBUG] Rest state '{self.state}' timed out but no timeout transition defined")

        if self.state == "move":
            print(f"[DEBUG] Graphics loaded for MOVE state: {self.graphics}")
        elif self.state == "long_rest":
            print(f"[DEBUG] Graphics loaded for LONG_REST state: {self.graphics} (state_name: {self.graphics.state_name})")

        return self
    
    def get_command(self) -> Command:
        """Get the current command for this state."""
        return self.current_command

# Helper function to create rest states
def create_long_rest_state(idle_state: State, moves: Moves, graphics: Graphics, physics: Physics) -> State:
    """Create a 2-second rest state that transitions back to idle."""
    rest_state = State(moves, graphics, physics, "long_rest")
    rest_state.is_rest_state = True
    rest_state.rest_duration_ms = 2000  # 2 seconds
    rest_state.set_transition("timeout", idle_state)
    return rest_state

def create_short_rest_state(idle_state: State, moves: Moves, graphics: Graphics, physics: Physics) -> State:
    """Create a 1-second rest state that transitions back to idle."""
    rest_state = State(moves, graphics, physics, "short_rest")
    rest_state.is_rest_state = True
    rest_state.rest_duration_ms = 1000  # 1 second
    rest_state.set_transition("timeout", idle_state)
    return rest_state

def create_move_state(idle_state: State, moves: Moves, graphics: Graphics, physics: Physics) -> State:
    """Create a move state that transitions to long rest upon completion."""
    from It1_interfaces.State import create_long_rest_state
    long_rest_state = create_long_rest_state(idle_state, moves, graphics, physics)
    move_state = State(moves, graphics, physics, "move")
    move_state.set_transition("complete", long_rest_state)
    return move_state