# 🥋 Kung Fu Chess - Real-Time Chess - Reorganized Architecture

## 🏗️ New Project Structure

The project has been reorganized into a client-server architecture for better modularity and maintainability:

```
CTD25/
├── 📁 client/              # Client-side components (UI, Graphics, Input, Sound)
│   ├── interfaces/         # Client interface modules
│   ├── pictures/          # Game images and UI assets
│   ├── sounds/            # Sound effects and audio files
│   ├── main.py           # Client main entry point
│   └── run_game.bat      # Windows batch file to run the game
│
├── 📁 server/              # Server-side components (Game Logic, Rules, State)
│   ├── interfaces/         # Server interface modules
│   ├── debug_pieces.py    # Piece debugging utilities
│   └── debug_promotion.py # Promotion system debugging
│
├── 📁 shared/              # Shared components (Events, Board, Common Data)
│   ├── interfaces/         # Shared interface modules
│   ├── pieces/            # Chess piece assets and configurations
│   ├── board.png          # Board background image
│   ├── requirements.txt   # Python dependencies
│   └── README.md          # This documentation
│
└── launch_game.py          # Main launcher script (NEW!)
```

## 🚀 How to Run

### Option 1: Use the Launcher (Recommended)
```bash
python launch_game.py
```

### Option 2: Use the Batch File (Windows)
```bash
client\run_game.bat
```

### Option 3: Run Client Directly
```bash
cd client
python main.py
```

## 📂 Architecture Details

### Client Components
- **GameUI**: User interface and display management
- **Graphics/GraphicsFactory**: Visual rendering and sprite management
- **img**: Image processing utilities
- **SoundManager**: Audio effects and music
- **ThreadedInputManager**: Player input handling
- **PromotionUI**: Promotion selection interface
- **AnimationManager**: Piece animation system

### Server Components
- **Game**: Core game loop and logic
- **ChessRulesValidator**: Chess rule enforcement
- **CollisionManager**: Piece collision detection
- **Command**: Action command pattern
- **MoveLogger**: Move history tracking
- **Moves/Physics**: Piece movement and physics
- **Piece/PieceFactory**: Piece state management
- **PromotionManager**: Promotion logic
- **ScoreManager**: Score tracking
- **StatisticsManager**: Game statistics

### Shared Components
- **EventBus**: Inter-component communication
- **EventTypes**: Event type definitions
- **Board**: Game board representation
- **pieces/**: Chess piece sprites and configurations

## 🎮 Game Controls

| Player   | Movement       | Select/Move/Jump |
|----------|----------------|------------------|
| Player A | Arrow Keys     | Enter            |
| Player B | W A S D        | Spacebar         |

### 📊 System Controls:
- **TAB**: Show live game statistics  
- **ESC**: Quit game

## 🔧 Development

The new architecture provides better separation of concerns:
- **Client**: Handles all user interface, graphics, and input
- **Server**: Manages game logic, rules, and state
- **Shared**: Contains common components used by both

This makes the codebase more maintainable and sets the foundation for potential future networking capabilities.

## 📋 Requirements

See `shared/requirements.txt` for Python dependencies.

## 🧪 Testing

Tests are organized within each component directory under `interfaces/tests/`.
