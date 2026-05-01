# Agent Design Plan for Gateway API

## 1. Architectural Overview: Supervisor (Router) Agent Pattern
The `gateway_api` module acts as the single entry point and orchestrator for all calls coming from the `App-React` frontend. It implements a **Supervisor Multi-Agent Pattern**. 

Instead of processing requests directly, the Gateway acts as a smart dispatcher. It evaluates the user's natural language input, understands the business domain of the request, and delegates the work to a specialized "Worker" or "Domain" Agent.

**Frontend Interface:** A single endpoint (e.g., `POST /api/gateway/chat`) handles all user requests.

## 2. Core Concepts

### Domain-Based Routing (The Supervisor)
Routing is determined by the **business domain** or **subject matter** of the text, not the desired output format. 
The Supervisor uses a Semantic Router (powered by LangChain) to classify the intent (e.g., HR Query, General Chat, Data Analysis) and passes the payload to the corresponding agent.

### Format-Agnostic Worker Agents
Once a Domain Agent (e.g., `HR_Agent`) receives the request, *that agent* decides how to fulfill it and format the output.
If the user asks for a diagram, a table, or plain text, the Domain Agent will utilize its prompts or shared tools to generate the correct format (such as Markdown or Mermaid.js syntax). The format generation is handled entirely within the chosen chain.

## 3. Extensibility & Scalability (Plug-and-Play)
The architecture is designed to support the continuous addition of new agents.
- **Agent Registry:** The Supervisor does not rely on hardcoded `if/else` logic. Instead, it uses an Agent Registry where each agent is defined by a `name` and a `description` (e.g., `"DataAnalysisAgent": "Use this for questions about metrics"`).
- **Dynamic Selection:** The LangChain routing logic reads these descriptions dynamically to route the request, meaning new agents can be dropped into the system seamlessly.

## 4. Modern LangChain Implementation
- **LCEL (LangChain Expression Language):** All agents and sub-agents will be built using the modern `|` pipe syntax for clean, readable chains.
- **LangGraph:** Recommended for managing the state and flow between the Supervisor node and the Worker nodes, providing robust memory and execution control.

## 5. Proposed Folder Structure
```text
apilayer/
└── api/
    └── gateway_api/
        ├── router.py          # FastAPI endpoint (receives App-React calls)
        ├── orchestrator.py    # The LangChain Supervisor (routes based on descriptions)
        ├── shared_tools/      # Shared utilities (e.g., Mermaid generator, parsers)
        └── domain_agents/     # Directory for plug-and-play domain agents
            ├── __init__.py
            ├── general_agent.py
            ├── hr_agent.py
            └── ... (more agents added over time)
```

## 6. Execution Flow
1. **Input:** `gateway_api` receives JSON text payload from App-React.
2. **Analysis:** The `orchestrator.py` (Supervisor) analyzes the text against registered agent descriptions.
3. **Delegation:** The request is routed to the appropriate module in `domain_agents/`.
4. **Processing:** The Domain Agent executes its LCEL chain, applying specific formats (Diagrams, Tables) if requested.
5. **Output:** The result is returned to the Supervisor, which formats a unified response back to App-React.
