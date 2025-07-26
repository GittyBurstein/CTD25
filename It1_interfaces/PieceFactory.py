import pathlib
from typing import Dict, Tuple
import json
from .Board import Board
from .GraphicsFactory import GraphicsFactory
from .Moves import Moves
from .PhysicsFactory import PhysicsFactory
from .Piece import Piece
from .State import State

class PieceFactory:
    def __init__(self, board: Board, pieces_root: pathlib.Path):
        """Initialize piece factory with board and pieces directory."""
        self.board = board
        self.pieces_root = pieces_root
        self.graphics_factory = GraphicsFactory()
        self.physics_factory = PhysicsFactory(board)
        
        # Cache of piece templates
        self.piece_templates: Dict[str, Dict[str, State]] = {}
        
        # Build templates from pieces directory
        self._build_templates()
    
    def _build_templates(self):
        """Build piece templates from the pieces directory structure."""
        if not self.pieces_root.exists():
            print(f"Warning: Pieces directory {self.pieces_root} does not exist")
            return
            
        for piece_dir in self.pieces_root.iterdir():
            if piece_dir.is_dir():
                try:
                    states = self._build_state_machine(piece_dir)
                    self.piece_templates[piece_dir.name] = states
                    print(f"[DEBUG] Built template for piece type: {piece_dir.name} with states: {list(states.keys())}")
                except Exception as e:
                    print(f"Warning: Could not build template for {piece_dir.name}: {e}")

    def _build_state_machine(self, piece_dir: pathlib.Path) -> Dict[str, State]:
        """Build a state machine for a piece from its directory."""
        print(f"[DEBUG] Building state machine for {piece_dir.name}")
        
        # Load moves
        moves_file = piece_dir / "moves.txt"
        moves = Moves(moves_file, (self.board.H_cells, self.board.W_cells))
        
        # Load config if exists
        config_file = piece_dir / "config.json"
        config = {}
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config = json.load(f)
            except:
                pass
        
        # Try to build states from directory structure
        states_dir = piece_dir / "states"
        states = {}
        
        if states_dir.exists() and states_dir.is_dir():
            print(f"[DEBUG] Found states directory: {states_dir}")
            for state_dir in states_dir.iterdir():
                if state_dir.is_dir():
                    state_name = state_dir.name
                    print(f"[DEBUG] Building state: {state_name}")
                    
                    # Load graphics from state-specific sprites directory
                    sprites_dir = state_dir / "sprites"
                    graphics = self.graphics_factory.create(
                        sprites_dir, 
                        config.get(state_name, {}), 
                        (self.board.cell_W_pix, self.board.cell_H_pix)
                    )
                    
                    # Create physics (will be customized per instance)
                    physics = self.physics_factory.create(
                        (0, 0), 
                        config.get(state_name, {})
                    )
                    
                    # Create state with special properties
                    state = State(moves, graphics, physics, state_name)
                    
                    # Configure rest states
                    if state_name == "long_rest":
                        state.is_rest_state = True
                        state.rest_duration_ms = 2000  # 2 seconds
                    elif state_name == "short_rest":
                        state.is_rest_state = True
                        state.rest_duration_ms = 1000  # 1 second
                    
                    states[state_name] = state
                    # Debugging: Verify state creation
                    print(f"[DEBUG] Created state: {state_name}")
        
        # If no states found or missing critical states, create them programmatically
        missing_states = self._get_missing_states(states)
        if missing_states:
            print(f"[DEBUG] Creating missing states programmatically: {missing_states}")
            self._create_missing_states(piece_dir, states, moves, config, missing_states)
        
        # Set up transitions between states
        self._setup_transitions(states)
        
        return states
    
    def _get_missing_states(self, states: Dict[str, State]) -> list:
        """Check which essential states are missing."""
        required_states = ["idle", "move", "long_rest"]
        missing = []
        
        for state_name in required_states:
            if state_name not in states:
                missing.append(state_name)
        
        # Debugging: Verify missing states
        print(f"[DEBUG] Missing states: {missing}")
        
        return missing
    
    def _create_missing_states(self, piece_dir: pathlib.Path, states: Dict[str, State], 
                             moves: Moves, config: dict, missing_states: list):
        """Create missing states programmatically."""
        
        for state_name in missing_states:
            print(f"[DEBUG] Creating programmatic state: {state_name}")
            
            # Try to load state-specific graphics first
            state_sprites_dir = piece_dir / "states" / state_name / "sprites"
            
            if not state_sprites_dir.exists():
                # Fallback to general sprites directory
                state_sprites_dir = piece_dir / "sprites"
                print(f"[DEBUG] Using fallback sprites directory for {state_name}: {state_sprites_dir}")
            else:
                print(f"[DEBUG] Using state-specific sprites for {state_name}: {state_sprites_dir}")
            
            # Create graphics for this specific state
            graphics = self.graphics_factory.create(
                state_sprites_dir,
                config.get(state_name, {}),
                (self.board.cell_W_pix, self.board.cell_H_pix)
            )
            
            # Create physics
            physics = self.physics_factory.create((0, 0), config.get(state_name, {}))
            
            # Create state
            state = State(moves, graphics, physics, state_name)
            
            # Configure special properties
            if state_name == "long_rest":
                state.is_rest_state = True
                state.rest_duration_ms = 2000
                print(f"[DEBUG] Configured {state_name} as rest state with 2000ms duration")
            elif state_name == "short_rest":
                state.is_rest_state = True
                state.rest_duration_ms = 1000
                print(f"[DEBUG] Configured {state_name} as rest state with 1000ms duration")
            
            states[state_name] = state
            # Debugging: Verify state creation
            print(f"[DEBUG] Created state: {state_name}")

    def _setup_transitions(self, states: Dict[str, State]):
        """Set up transitions between states."""
        print(f"[DEBUG] Setting up transitions for states: {list(states.keys())}")
        
        # Basic transitions for movement
        if "idle" in states:
            if "move" in states:
                # Debugging: Verify available states
                print(f"[DEBUG] Available states: {list(states.keys())}")

                # Debugging: Verify transition from 'idle' to 'move'
                if "idle" in states and "move" in states:
                    print(f"[DEBUG] Adding transition from 'idle' to 'move'")
                    states["idle"].set_transition("Move", states["move"])
                    print("[DEBUG] Set up idle -> move transition")
            
            if "jump" in states:
                states["idle"].set_transition("Jump", states["jump"])
                print("[DEBUG] Set up idle -> jump transition")
                
            if "attack" in states:
                states["idle"].set_transition("Attack", states["attack"])
                print("[DEBUG] Set up idle -> attack transition")
        
        # Move completion transitions
        if "move" in states:
            if "long_rest" in states:
                states["move"].set_transition("complete", states["long_rest"])
                print("[DEBUG] Set up move -> long_rest transition")
            elif "idle" in states:
                states["move"].set_transition("complete", states["idle"])
                print("[DEBUG] Set up move -> idle transition (fallback)")
        
        # Jump completion transitions
        if "jump" in states:
            if "short_rest" in states:
                states["jump"].set_transition("complete", states["short_rest"])
                print("[DEBUG] Set up jump -> short_rest transition")
            elif "idle" in states:
                states["jump"].set_transition("complete", states["idle"])
                print("[DEBUG] Set up jump -> idle transition (fallback)")
        
        # Rest state timeout transitions
        if "long_rest" in states and "idle" in states:
            states["long_rest"].set_transition("timeout", states["idle"])
            print("[DEBUG] Set up long_rest -> idle timeout transition")
        
        if "short_rest" in states and "idle" in states:
            states["short_rest"].set_transition("timeout", states["idle"])
            print("[DEBUG] Set up short_rest -> idle timeout transition")
        
        # Attack completion
        if "attack" in states and "idle" in states:
            states["attack"].set_transition("complete", states["idle"])
            print("[DEBUG] Set up attack -> idle transition")
        
        # Print all transitions for debugging
        for state_name, state in states.items():
            transitions_list = list(state.transitions.keys())
            print(f"[DEBUG] State '{state_name}' has transitions: {transitions_list}")

    def create_piece(self, p_type: str, cell: Tuple[int, int]) -> Piece:
        """Create a piece of the specified type at the given cell."""
        if p_type not in self.piece_templates:
            raise ValueError(f"Unknown piece type: {p_type}")
        
        print(f"[DEBUG] Creating piece of type {p_type} at {cell}")
        
        # Clone the template state machine
        template_states = self.piece_templates[p_type]
        
        # Create new states for this piece instance
        new_states = {}
        for state_name, template_state in template_states.items():
            # Create new components
            moves = template_state.moves  # Moves can be shared
            graphics = template_state.graphics.copy()
            physics = self.physics_factory.create(cell, {})
            
            # Create new state
            new_state = State(moves, graphics, physics, state_name)
            new_state.is_rest_state = template_state.is_rest_state
            new_state.rest_duration_ms = template_state.rest_duration_ms
            new_states[state_name] = new_state
        
        # Set up transitions between the new states
        for state_name, template_state in template_states.items():
            for event, target_template in template_state.transitions.items():
                target_state_name = target_template.state
                if target_state_name in new_states:
                    new_states[state_name].set_transition(event, new_states[target_state_name])
                    print(f"[DEBUG] Set transition: {state_name} --{event}--> {target_state_name}")
        
        # Get the initial state (idle by default)
        initial_state = new_states.get("idle", list(new_states.values())[0])
        
        # Generate unique piece ID
        piece_id = f"{p_type}_{cell[0]}_{cell[1]}_{id(initial_state)}"
        
        piece = Piece(piece_id, initial_state, p_type)
        print(f"[DEBUG] Created piece: {piece_id} of type {p_type} at {cell} in state '{initial_state.state}'")
        # Debugging: Verify initial state transitions
        print(f"[DEBUG] Initial state transitions: {list(initial_state.transitions.keys())}")
        
        return piece