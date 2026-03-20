# Multi-Agent Texas Hold'em Poker Game

A multi-agent Texas Hold'em poker game built with AgentScope framework, featuring AI agents with different personalities that can communicate with each other.

## Features

- **5 AI Agents with Different Personalities**:
  - Alice (Aggressive) - Likes to raise and take risks
  - Bob (Conservative) - Plays safe, only bets with strong hands
  - Charlie (Technical) - Analyzes opponents' behavior
  - David (Lucky) - Believes in luck, likes to gamble
  - Eve (Balanced) - Makes rational decisions based on hand strength

- **Agent Communication**: Agents can send messages to each other during the game
- **Distributed Architecture**: Each agent runs as an independent process
- **AgentScope Integration**: Uses AgentScope framework for AI decision-making
- **DeepSeek-V3.2 Model**: Powered by DeepSeek-V3.2 via SiliconFlow API

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Server                              │
│              (TCP Server on port 8888)                   │
│                                                          │
│  - Manages game state                                    │
│  - Routes messages between agents                        │
│  - Broadcasts game events                                │
└─────────────────────────────────────────────────────────┘
                           │
                           │ TCP Connections
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│    Alice     │  │     Bob      │  │   Charlie    │
│  (Aggressive)│  │(Conservative)│  │ (Technical)  │
└──────────────┘  └──────────────┘  └──────────────┘
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│    David     │  │     Eve      │  │     User     │
│   (Lucky)    │  │  (Balanced)  │  │   (Player)   │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Requirements

- Python 3.10 or higher
- AgentScope
- OpenAI-compatible API (DeepSeek-V3.2 via SiliconFlow)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/GCGH159/multi-agent-texas-holdEM.git
cd multi-agent-texas-holdEM
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure API key:
   - The project uses DeepSeek-V3.2 model via SiliconFlow API
   - API key is configured in each agent file
   - You can replace the API key with your own

## Usage

### Start the Game

**Windows:**
```bash
.\start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

### Manual Start (for debugging)

1. Start the server:
```bash
.venv\Scripts\python server.py
```

2. Start AI agents (in separate terminals):
```bash
.venv\Scripts\python agents\alice.py
.venv\Scripts\python agents\bob.py
.venv\Scripts\python agents\charlie.py
.venv\Scripts\python agents\david.py
.venv\Scripts\python agents\eve.py
```

3. Start user client:
```bash
.venv\Scripts\python user_client.py
```

## Project Structure

```
multi-agent-texas-holdEM/
├── server.py              # Game server
├── client.py              # Client library
├── user_client.py         # User client for playing
├── agent_framework.py     # Agent decision framework
├── agents/
│   ├── alice.py          # Aggressive agent
│   ├── bob.py            # Conservative agent
│   ├── charlie.py        # Technical agent
│   ├── david.py          # Lucky agent
│   └── eve.py            # Balanced agent
├── start.bat             # Windows startup script
├── start.sh              # Linux/Mac startup script
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## Agent Communication

Agents can communicate with each other using the chat system:

- **Broadcast**: Send message to all agents (`to="all"`)
- **Direct Message**: Send message to specific agent (`to="Alice"`)

Example chat messages:
- Alice: "我选择了raise！你们敢跟吗？" (I chose raise! Dare you follow?)
- Bob: "这把牌不好，我弃牌了。" (Bad hand, I fold.)
- Charlie: "经过分析，我选择raise。" (After analysis, I choose raise.)
- David: "我相信我的运气！全下！" (I believe in my luck! All in!)
- Eve: "我觉得这是个好机会，选择raise。" (I think this is a good opportunity, choosing raise.)

## Game Actions

Available actions:
- `fold` - Fold the hand
- `check` - Check (if no bet)
- `call` - Call the current bet
- `raise` - Raise the bet
- `all_in` - Go all in

## API Configuration

The project uses:
- **Model**: DeepSeek-V3.2
- **API**: SiliconFlow (OpenAI-compatible)
- **Endpoint**: https://api.siliconflow.cn/v1

To use your own API:
1. Get an API key from SiliconFlow
2. Update the `api_key` parameter in each agent file

## Technologies

- **AgentScope**: Multi-agent framework
- **DeepSeek-V3.2**: Large language model
- **Asyncio**: Asynchronous networking
- **TCP Sockets**: Inter-agent communication

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Acknowledgments

- [AgentScope](https://github.com/agentscope-ai/agentscope) - Multi-agent framework
- [DeepSeek](https://www.deepseek.com/) - AI model
- [SiliconFlow](https://siliconflow.cn/) - API provider
