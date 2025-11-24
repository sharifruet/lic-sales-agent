# LangGraph Migration Playbook

This document breaks down the work required to replace the legacy “conversation service” with a LangGraph-based agent pipeline. Each milestone builds on the previous one; follow in order to keep the application running while we migrate.

---

## Milestone 0 — Foundations (Done)
- ✅ New directory layout (`apps/`, `graph/`, `chains/`, `rag/`, `tools/`, `state/`, `observability/`, `config/`, `tests/`, `scripts/`).
- ✅ Shared configuration re-exported via `config.settings`.
- ✅ FastAPI app factory in `apps/api/bootstrap.py` used by both new and legacy entrypoints.

---

## Milestone 1 — Planner Skeleton
1. **State Schema Updates**
   - Extend `state.schemas.ConversationState` with planner-specific fields (e.g., `plan_steps: list[str]`, `current_objective: str`, `pending_tool_call: Optional[str]`).
   - Add enums/constants for planner decision types (e.g., `ActionType`, `PlanDecision`).

2. **Planner Chain**
   - Implement `chains/prompts/planner.prompt` with draft template describing available nodes and tools.
   - Implement `chains/runnables.build_planner_chain()` returning a LangChain `Runnable` (LLM + prompt + parser).
   - Implement `chains/parsers.parse_planner_output()` producing a dataclass or Pydantic model with next-step metadata.

3. **Planner Node**
   - Implement `graph/nodes/planner.plan_next_step()`:
     - Pull context from `ConversationState`.
     - Call the planner chain.
     - Update state with planner output (e.g., selected action, rationale).

4. **Tests**
   - Add unit test in `tests/test_graph.py` mocking the planner chain and verifying state updates.
   - Add snapshot prompt test (optional) to guard against accidental prompt regressions.

Deliverable: LangGraph planner node can read state, produce structured plan info, and update state without running the rest of the graph.

---

## Milestone 2 — Retriever Skeleton
1. **RAG Infrastructure**
   - Stub `rag/ingest.ingest_documents(source_path: str)` that loads sample YAML/JSON data into an in-memory vector store (e.g., FAISS or Chroma).
   - Implement `rag/retriever.get_retriever()` returning a LangChain retriever (even if in-memory/hardcoded for now).
   - Define metadata schemas in `rag/schemas.py` (DocumentMetadata, ChunkMetadata) and ensure they’re used by ingestion.

2. **Retriever Chain**
   - Update `chains/prompts/retriever.prompt` with context on how to retrieve relevant knowledge.
   - Implement `chains/runnables.build_retriever_chain()` that coordinates retrieval + optional rerank.
   - Implement `chains/parsers.parse_retriever_output()` to structure retrieved context for downstream nodes.

3. **Retriever Node**
   - Implement `graph/nodes/retriever.retrieve_context()`:
     - Use planner output (selected action/tool) to construct retrieval query.
     - Attach retrieved documents/snippets to state (`ConversationState.retrieved_context`).

4. **Tests**
   - In `tests/test_rag.py`, add ingestion + retrieval roundtrip test using sample corpus.
   - Unit test retriever node with mocked retriever to ensure state mutation works.

Deliverable: Graph can run planner ➜ retriever sequentially, storing retrieved context in state.

---

## Milestone 3 — Action Skeleton
1. **Action Prompt & Chain**
   - Author `chains/prompts/action.prompt` instructing the model to craft a response or tool invocation based on planner decision and retrieved context.
   - Implement `chains/runnables.build_action_chain()` (LLM + prompt + parser).
   - Implement `chains/parsers.parse_action_output()` returning structured result (`assistant_message`, optional `tool_call`).

2. **Action Node**
   - Implement `graph/nodes/action.execute_action()`:
     - Consume planner decision, retrieved context, and conversation history.
     - Call action chain and append assistant message to state.
     - Handle tool-call stub (e.g., set `state.pending_tool_call` for future tool execution).

3. **Message Management**
   - Update `state.schemas.Message` to include metadata for planner/action/retriever contributions (e.g., `message_type`).
   - Ensure state append logic is centralized (`state.memory.apply_short_term_memory`).

4. **Tests**
   - Unit test action node (mock chain) verifying message appended.
   - Integration test invoking planner ➜ retriever ➜ action with fixtures returning static outputs.

Deliverable: Core loop (planner ➜ retriever ➜ action) runs end-to-end.

---

## Milestone 4 — Decision & Reflection
1. **Decider Node**
   - Implement `graph/nodes/decider.decide_next_action()` reading current state (e.g., whether more info is needed, tool call required, lead capture triggered).
   - Map decisions to graph edges (`planner`, `retriever`, `action`, `reflector`, or `finalize`).

2. **Reflector Node**
   - Implement `graph/nodes/reflector.reflect_on_conversation()` to summarise progress, adjust plan, or reset memory when loops occur.
   - Optionally use LangChain summarisation or heuristics.

3. **Graph Assembly**
   - Implement `graph/build_graph.build_conversation_graph()`:
     - Define LangGraph nodes and edges.
     - Configure state schema (initial state, aggregator).
     - Return runnable graph object.

4. **Tests**
   - Add graph execution tests for simple conversation scenarios.
   - Validate decision logic leads to expected node transitions.

Deliverable: Graph runner can execute multiple turns with decision/reflection and stop criteria.

---

## Milestone 5 — Tooling, Memory, and Observability
1. **Tool Execution Pipeline**
   - Flesh out `tools/mcp_client.MCPClient` to support one or more test tools (e.g., policy lookup).
   - Define tool manifests in `tools/toolspecs/`.
   - Extend action node to branch into tool execution if `pending_tool_call` is set.

2. **Memory Policies**
   - Implement `state/memory.apply_short_term_memory` (context window pruning).
   - Implement `state/memory.apply_long_term_memory` (write summaries to DB / vector store for reuse).

3. **Observability**
   - Implement `observability/langsmith_init.init_langsmith()` to wrap graph runs with tracing if LangSmith keys present.
   - Build evaluation script `observability/evals/run_evals.py` exercising canned dialog flows.

4. **API Integration**
   - Add new API endpoint in `apps/api` (e.g., `POST /conversations/{id}/next`) to run one LangGraph turn.
   - Wrap graph invocation in background task / streaming response as needed.

Deliverable: Graph supports tool execution, memory updates, and is instrumented for tracing/testing.

---

## Milestone 6 — Deprecate Legacy Path
1. Replace legacy conversation services with LangGraph invocation inside FastAPI routes.
2. Update legacy modules to either delegate to new packages or remove them after parity achieved.
3. Update documentation (technical design, LLM integration design) to describe the new architecture.
4. Remove temporary xfail tests; add regression suite for LangGraph flows.

---

## Granular Task Checklist

### Planner Tasks
- [x] Update `ConversationState` with planner fields.
- [x] Implement `build_planner_chain`.
- [x] Implement `parse_planner_output`.
- [x] Implement `plan_next_step`.
- [x] Add unit tests for planner node.

### Retriever Tasks
- [x] Implement ingestion stub and seed data.
- [x] Implement `get_retriever`.
- [x] Implement `build_retriever_chain`.
- [x] Implement `retrieve_context`.
- [x] Add unit tests and integration tests.

### Action Tasks
- [x] Implement `build_action_chain`.
- [x] Implement `parse_action_output`.
- [x] Implement `execute_action`.
- [x] Update message schema/memory helpers.
- [x] Add unit and integration tests.

### Graph Assembly & Decision
- [x] Implement decider logic.
- [x] Implement reflector node (optional but recommended).
- [x] Implement `build_conversation_graph`.
- [x] Write graph end-to-end tests.

### Tooling & Memory
- [x] Flesh out MCP client & tool specs.
- [x] Implement memory policies.
- [x] Integrate LangSmith tracing.
- [x] Add evaluation scripts/datasets.

---

## References
- LangGraph docs: https://langchain-ai.github.io/langgraph/
- LangChain runnables: https://python.langchain.com/docs/expression_language
- MCP (Model Context Protocol): https://modelcontextprotocol.io/

Keep this playbook updated as milestones are completed or scope changes. Each completed milestone should trigger doc updates in the architecture and technical design repositories.

