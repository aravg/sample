Here's a breakdown of each key primitive in the OpenAI Agents SDK:

## 1. Agents

An **Agent** is a configuration object — it defines *what* an LLM should do, but doesn't execute anything on its own. Think of it as a blueprint.

```python
agent = Agent(
    name="Support Bot",
    instructions="Help users with billing questions",
    model="gpt-5.5",
    tools=[lookup_invoice, refund_payment]
)
```

An agent bundles together: a model (which LLM to use), instructions (the system prompt defining its personality and rules), tools (functions it can call), and optional things like guardrails and output schemas. You can have many agents in one application, each specialized for different tasks — a triage agent, a billing agent, a writing agent, etc.

## 2. Runner

The **Runner** is the execution engine. It takes an agent and an input, then runs the *agent loop*: call the model → if the model wants to use a tool, run the tool → feed the result back to the model → repeat until the model produces a final answer.

```python
result = Runner.run_sync(agent, "What's my invoice for March?")
print(result.final_output)
```

Without the Runner, you'd have to write this loop yourself: parsing tool calls from the model, executing them, formatting results, sending them back, handling errors, tracking turns. The Runner does all of that. It also handles handoffs between agents, applies guardrails, manages sessions, and emits trace events.

## 3. Tools

**Tools** are capabilities you give an agent. The model decides when to call them based on the user's request.

Three main categories:

**Function tools** — your Python functions, exposed to the model:
```python
@function_tool
def get_weather(city: str) -> str:
    return f"Weather in {city}: sunny"
```

**Built-in hosted tools** — things OpenAI runs for you: `WebSearchTool`, `FileSearchTool` (vector store retrieval), `CodeInterpreterTool`, `ImageGenerationTool`, `ShellTool` (sandboxed shell).

**MCP tools** — connect to remote MCP servers (Asana, GitHub, etc.) via `HostedMCPTool`.

The model sees each tool's name, description, and parameters as a JSON schema and picks which one to call.

## 4. Handoffs

**Handoffs** let one agent transfer control to another. This enables specialization — instead of one giant agent that does everything, you build a network of focused agents.

```python
triage_agent = Agent(
    name="Triage",
    instructions="Route to the right specialist",
    tools=[
        Handoff(agent=billing_agent, description="For billing"),
        Handoff(agent=tech_agent, description="For technical issues"),
    ]
)
```

A handoff appears to the model as a special kind of tool. When the model calls it, the Runner switches to the target agent and continues the conversation with that agent's instructions and tools. The user-facing experience is seamless — they don't know they were "transferred."

## 5. Guardrails

**Guardrails** are validation layers that run before input reaches the agent or after output leaves it. They catch problems early: jailbreak attempts, PII leaks, off-topic requests, malformed outputs.

```python
def block_competitor_mentions(input_text):
    if "competitor_name" in input_text.lower():
        raise GuardrailViolation("Cannot discuss competitors")
    return input_text

agent = Agent(
    name="Sales Bot",
    instructions="...",
    input_guardrail=Guardrail(handler=block_competitor_mentions)
)
```

Input guardrails validate what goes *into* the agent; output guardrails validate what comes *out*. They run as fast checks (often using a cheaper model) so a violation can short-circuit an expensive agent call.

## 6. Sessions

**Sessions** persist conversation history across multiple Runner calls. Without them, every `Runner.run()` is stateless — the agent has no memory of previous turns.

```python
# Turn 1
result1 = await Runner.run(agent, "I'm planning a trip to Tokyo")

# Turn 2 — agent remembers the Tokyo context
result2 = await Runner.run(
    agent,
    "What about food recommendations?",
    conversation_id=result1.conversation_id
)
```

Three storage options: **server-managed** (OpenAI stores the conversation, you just pass `conversation_id`), **local SQLite** (stored on your machine), and **Redis** (for distributed apps). Sessions are what turn a one-shot agent into a real chatbot or assistant.

---

## How They Fit Together

Here's the mental model: you **define** an `Agent` with `Tools` and optional `Guardrails`. You hand it to the `Runner` along with an input. The Runner executes the agent loop, calling tools as needed. If the agent does a `Handoff`, the Runner swaps to a new agent and keeps going. A `Session` ties multiple Runner calls together into a coherent conversation.

A full example pulling everything together:

```python
from agents import Agent, Runner, Handoff, Guardrail, function_tool

@function_tool
def check_balance(account_id: str) -> str:
    return f"Balance: $1,234"

billing_agent = Agent(
    name="Billing",
    instructions="Handle billing questions",
    tools=[check_balance],
)

triage_agent = Agent(
    name="Triage",
    instructions="Route the user to the right specialist",
    tools=[Handoff(agent=billing_agent, description="Billing issues")],
    input_guardrail=Guardrail(handler=block_pii),
)

# Runner orchestrates everything; conversation_id maintains the session
result = await Runner.run(
    triage_agent,
    "What's my account balance?",
    conversation_id="conv_abc123"
)
```

Want me to go deeper on any one of these?
