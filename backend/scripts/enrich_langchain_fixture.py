#!/usr/bin/env python3
"""Rebuild the LangChain reference fixture with content a reader can act on.

Run once, from the repository root:

    python3 backend/scripts/enrich_langchain_fixture.py

Why a script rather than a hand-edited file: the fixture has 22 Stages, and the
content contract requires an example, an implementation detail, a command, an
expected result, and a caution on each. Editing that by hand invites exactly the
gap this batch exists to close -- a Stage with a plausible-looking but untested
example. Writing it as code makes each Stage's content reviewable as data and
regenerable.

The commands are real LangChain 1.x invocations. That is the point of a golden
case: "only using COP Studio, can a learner complete the minimal LangChain
case" is only answerable if the commands in it actually run.
"""

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "fixtures" / "reference-langchain-cop.json"
SOURCES_OUT = ROOT / "fixtures" / "reference-langchain-sources.json"
SCHEMA = ROOT / "schemas" / "cop-artifact.schema.json"

# --- Sources the fixture is built from -------------------------------------
#
# The artifact cites these six ids. Seeding creates a Source row per entry, so
# every `evidence_ref` resolves to something the user can open. The alternative
# -- citing ids that exist only in the JSON -- is the R3 orphan-reference bug.
SOURCES: dict[str, dict[str, str]] = {
    "lc-overview": {
        "title": "LangChain overview",
        "uri": "https://docs.langchain.com/oss/python/langchain/overview",
        "text": (
            "create_agent is the high-level entry point for building agents in LangChain. "
            "It takes a model, a list of tools, and optional instructions, and returns a "
            "compiled agent that can be invoked with messages. LangGraph is the lower-level "
            "runtime underneath it."
        ),
    },
    "lc-agents": {
        "title": "LangChain agents guide",
        "uri": "https://docs.langchain.com/oss/python/langchain/agents",
        "text": (
            "An agent is created with create_agent(model, tools, system_prompt). Invoke it "
            "with a message dict containing a 'human' role. The response contains an 'ai' "
            "message. Tools are plain Python functions; a docstring becomes the tool "
            "description the model uses to decide whether to call it."
        ),
    },
    "lc-tools": {
        "title": "LangChain tools guide",
        "uri": "https://docs.langchain.com/oss/python/langchain/tools",
        "text": (
            "Any Python callable can be a tool. @tool decorates a function and derives its "
            "schema from the type hints and docstring. When a tool needs a live capability "
            "-- a database, an HTTP endpoint, the filesystem -- the plain function is called "
            "inside a ToolNode, which is what lets the model's tool choice reach real code."
        ),
    },
    "lc-memory": {
        "title": "LangChain persistence and short-term memory",
        "uri": "https://docs.langchain.com/oss/python/langchain/long-term-memory",
        "text": (
            "Short-term memory keeps one conversation. Pass a thread_id in the config to "
            "invoke so state is scoped to that thread and can be recovered between calls. "
            "Checkpointer implementations include InMemorySaver for a single process and "
            "SqliteSaver or PostgresSaver to survive a restart."
        ),
    },
    "lc-retrieval": {
        "title": "LangChain retrieval guide",
        "uri": "https://docs.langchain.com/oss/python/langchain/retrieval",
        "text": (
            "A retrieval tool wraps a retriever as a callable the agent can choose. Split "
            "documents into overlapping chunks, embed them, and store them in a vector store. "
            "The agent decides when the question needs external knowledge, which is the "
            "difference from a pipeline that always retrieves."
        ),
    },
    "lc-middleware": {
        "title": "LangChain middleware guide",
        "uri": "https://docs.langchain.com/oss/python/langchain/middleware",
        "text": (
            "Middleware wraps agent execution to add control: guardrails, retries, human "
            "approval, summarisation, or custom logging. Middleware is passed to "
            "create_agent as a list. Ordering matters -- an outer middleware sees the request "
            "first and the response last."
        ),
    },
}

# --- Per-Stage content -----------------------------------------------------
#
# Keyed by Stage id. Each entry is what a reader needs in order to act:
#   detail    the followable step, with the literal command
#   example   the worked case, showing input and output
#   evidence  which source supports the claim

DETAILS: dict[str, list[dict[str, str]]] = {
    "stage.foundation.install": [
        {
            "title": "Install LangChain and a provider integration",
            "action": "Create a virtual environment and install LangChain plus one model provider.",
            "command": (
                "python3 -m venv .venv && source .venv/bin/activate && "
                "pip install -U langchain langchain-openai"
            ),
            "expected_result": (
                "pip ends with 'Successfully installed'. `python -c \"import langchain; "
                'print(langchain.__version__)"` prints a version and exits 0.'
            ),
            "caution": (
                "Install into the virtual environment, never the system interpreter. A global "
                "install is the usual cause of 'module not found' in a project that looks right."
            ),
        },
        {
            "title": "Set the API key the provider will read",
            "action": "Export the key in the shell that will run the code, or put it in a .env file.",
            "command": "export OPENAI_API_KEY=sk-...   # or: echo 'OPENAI_API_KEY=sk-...' > .env",
            "expected_result": "echo $OPENAI_API_KEY prints a non-empty value.",
            "caution": (
                'A key in .env is only read if something loads it. `python -c "import os; '
                "print(bool(os.environ.get('OPENAI_API_KEY')))\"` prints True, or you have not "
                "finished this step."
            ),
        },
        {
            # The 401 from an OpenAI-compatible endpoint names platform.openai.com
            # even when the key is valid, because the SDK only knows OpenAI's own
            # error text. That sends people to look for a key they already have.
            "title": "Point the SDK at your provider, if it is not OpenAI",
            "action": (
                "Skip this step if you use api.openai.com. Any other OpenAI-compatible endpoint "
                "has to be named explicitly, or the SDK sends your key to OpenAI by default."
            ),
            "command": "export OPENAI_API_BASE=https://your-provider.example/v1",
            "expected_result": (
                '`python -c "from langchain_openai import ChatOpenAI; '
                "print(ChatOpenAI(model='gpt-4o-mini').openai_api_base)\"` prints the endpoint. "
                "It prints `None` if the variable is misspelled."
            ),
            "caution": (
                "The two are independent: without the base URL a valid key still fails, and the "
                "error names OpenAI's key page. Do not test this against `/models` -- plenty of "
                "compatible gateways serve that path without checking the key at all, so it "
                'answers 200 either way. Verify with one real call instead: `python -c "from '
                "langchain_openai import ChatOpenAI; print(ChatOpenAI(model='gpt-4o-mini')"
                ".invoke('reply with the word ok').content)\"`. Note the variable is "
                "`OPENAI_API_BASE`, not `OPENAI_BASE_URL` -- the latter is silently ignored and "
                "the only symptom is the 401 below."
            ),
        },
        {
            # Later Stages write multi-line files with `cat > f <<'TAG'`. The
            # quoting rules are the only place this syntax is explained, and a
            # learner who meets it cold cannot tell why the terminator must be
            # flush left or why the tag is quoted.
            "title": "Read the heredoc used to write files",
            "action": (
                "Later Stages create files with `cat > tools.py <<'PY' ... PY`. The first line "
                "opens a heredoc: `cat` writes everything up to the line that says `PY`."
            ),
            # The filename deliberately is not notes.txt: the RAG process loads a
            # file by that name, and a learner who created this demo file first
            # would silently retrieve one line of shell trivia.
            "command": "cat > heredoc-demo.txt <<'TXT'\nline one $HOME is not expanded\nTXT",
            "expected_result": (
                "`cat heredoc-demo.txt` prints `line one $HOME is not expanded`. The single "
                "quotes around the tag are what stop the shell from expanding `$HOME`."
            ),
            "caution": (
                "The closing `PY` must be flush left, on its own line, or the shell keeps "
                "waiting for input. This is the only place heredoc is explained, so a Stage "
                "that uses it assumes you have read this -- and the file it writes has to be "
                "one a later Stage actually reads."
            ),
        },
    ],
    "stage.foundation.model": [
        {
            "title": "Create a chat model and call it directly",
            "action": (
                "Construct a model with no agent involved. If the model works here, every later "
                "failure is about the agent rather than about credentials."
            ),
            "command": (
                'python -c "from langchain_openai import ChatOpenAI; '
                "print(ChatOpenAI(model='gpt-4o-mini').invoke('reply with the word ok').content)\""
            ),
            "expected_result": "The script prints `ok`.",
            "caution": (
                "A 401 here means the key, the endpoint, or the model name is wrong -- check "
                "all three, in that order, because the three produce the same error. On a "
                "third-party endpoint the message also names platform.openai.com, which is "
                "misleading rather than evidence: the SDK does not know whose server it "
                "reached. A 429 means rate limited. Both look identical later inside an agent, "
                "which is why this step exists."
            ),
        },
        {
            # Every later command constructs `ChatOpenAI(model='...')` with no key
            # and no endpoint in it. That is deliberate, and without this detail
            # it reads as an omission rather than a mechanism -- so a learner
            # cannot tell whether the Foundation steps actually feed the Stages.
            "title": "Every later command reads these from the environment",
            "action": (
                "Notice that `ChatOpenAI(model='gpt-4o-mini')` names no key and no endpoint. It "
                "picks both up from the variables the Foundation exported, which is why no later "
                "Stage repeats them."
            ),
            "command": (
                'python -c "from langchain_openai import ChatOpenAI; '
                "m = ChatOpenAI(model='gpt-4o-mini'); "
                "print('key set:', bool(m.openai_api_key)); print('endpoint:', m.openai_api_base)\""
            ),
            "expected_result": (
                "`key set: True`. The endpoint line prints your provider, or `None` on "
                "api.openai.com -- both are correct, and `None` here is not the bug that a `None` "
                "endpoint causes later."
            ),
            "caution": (
                "Changing the key or endpoint means re-exporting in every shell you run from; a "
                "terminal opened before the export still holds the old value. This is also why "
                "the model is the only per-command argument: the rest is environment, so all "
                "15 later commands are identical in this respect."
            ),
        },
    ],
    "stage.basic.create-agent": [
        {
            "title": "Create the agent with no tools",
            "action": "Call create_agent with the model and a system prompt. Tools may be empty.",
            "command": (
                'python -c "from langchain.agents import create_agent; '
                "from langchain_openai import ChatOpenAI; "
                "a = create_agent(ChatOpenAI(model='gpt-4o-mini'), tools=[], "
                "system_prompt='You answer in one short sentence.'); print('created')\""
            ),
            "expected_result": "The script prints `created`.",
            "caution": (
                "The first positional argument is the model. Passing a string there is the "
                "most common error, and it fails with a type error rather than a useful message."
            ),
        },
    ],
    "stage.basic.invoke": [
        {
            "title": "Invoke the agent with one user message",
            "action": "Pass a message dict with a human role and read the returned state.",
            "command": (
                'python -c "from langchain.agents import create_agent; '
                "from langchain_openai import ChatOpenAI; "
                "a = create_agent(ChatOpenAI(model='gpt-4o-mini'), tools=[]); "
                "r = a.invoke({'messages': [{'role': 'user', 'content': 'Name one benefit of agents.'}]}); "
                "print(r['messages'][-1].content)\""
            ),
            "expected_result": "The script prints a sentence about the benefit of agents.",
            "caution": (
                "`r['messages'][-1]` is the final answer, not the first. With tools the first "
                "message is the model's tool request, so reading index 0 looks like a bug in "
                "the agent."
            ),
        },
    ],
    "stage.basic.inspect": [
        {
            "title": "Read the whole message list",
            "action": "Print every message with its type so the execution is legible.",
            "command": (
                'python -c "from langchain.agents import create_agent; '
                "from langchain_openai import ChatOpenAI; "
                "a = create_agent(ChatOpenAI(model='gpt-4o-mini'), tools=[]); "
                "r = a.invoke({'messages': [{'role': 'user', 'content': 'hi'}]}); "
                "[print(m.type, repr(m.content)[:60]) for m in r['messages']]\""
            ),
            "expected_result": "Two lines: `human 'hi'` then `ai ...`.",
            "caution": (
                "The state is a dict with a 'messages' key. Reaching for `.content` on the "
                "result object instead is the usual cause of an AttributeError."
            ),
        },
    ],
    "stage.tool.define": [
        {
            "title": "Write the tool as a typed function",
            "action": (
                "Write a plain Python function with type hints and a docstring. The docstring "
                "is what the model reads to decide whether to call it."
            ),
            "command": (
                "cat > tools.py <<'PY'\n"
                "from langchain.tools import tool\n\n"
                "@tool\n"
                "def word_count(text: str) -> int:\n"
                '    """Count the words in a piece of text."""\n'
                "    return len(text.split())\n"
                "PY"
            ),
            "expected_result": (
                '`ls tools.py` lists the file, and `python -c "from tools import word_count; '
                "print(word_count.invoke('a b c'))\"` prints 3. The import is the real check: "
                "it fails if the heredoc never closed."
            ),
            "caution": (
                "A tool with no docstring still works but is called far less often: the model "
                "has nothing to match the user's request against."
            ),
        },
    ],
    "stage.tool.create-agent": [
        {
            "title": "Attach the tool at construction time",
            "action": (
                "This imports tools.py, written by the step 'Define a tool'. The process order is what makes it exist; running this Stage on its own fails with ModuleNotFoundError, which means the step was skipped rather than that the code is wrong. "
                "Pass the tool objects as the second argument to create_agent."
            ),
            "command": (
                'python -c "from langchain.agents import create_agent; '
                "from langchain_openai import ChatOpenAI; from tools import word_count; "
                "a = create_agent(ChatOpenAI(model='gpt-4o-mini'), tools=[word_count]); "
                "print(list(a.get_graph().nodes['tools'].data.tools_by_name))\""
            ),
            "expected_result": "The script prints `['word_count']`.",
            "caution": (
                "Tools are bound at construction. Adding one to the list afterwards does "
                "nothing; the agent has to be created again."
            ),
        },
    ],
    "stage.tool.invoke": [
        {
            "title": "Ask something only the tool can answer",
            "action": (
                "This imports tools.py, written by the step 'Define a tool'. The process order is what makes it exist; running this Stage on its own fails with ModuleNotFoundError, which means the step was skipped rather than that the code is wrong. "
                "Invoke with a request that needs the external capability."
            ),
            "command": (
                'python -c "from langchain.agents import create_agent; '
                "from langchain_openai import ChatOpenAI; from tools import word_count; "
                "a = create_agent(ChatOpenAI(model='gpt-4o-mini'), tools=[word_count]); "
                "r = a.invoke({'messages': [{'role': 'user', 'content': "
                "'How many words are in: the quick brown fox jumps'}]}); "
                "[print(m.type) for m in r['messages']]\""
            ),
            "expected_result": "Four lines: human, ai (tool call), tool, ai (final answer).",
            "caution": (
                "If you see only human and ai, the model chose not to call the tool. That is a "
                "prompt problem, not a wiring problem -- reword the request or the tool docstring."
            ),
        },
    ],
    "stage.tool.verify-loop": [
        {
            "title": "Assert the four messages are present",
            "action": (
                "This imports tools.py, written by the step 'Define a tool'. The process order is what makes it exist; running this Stage on its own fails with ModuleNotFoundError, which means the step was skipped rather than that the code is wrong. "
                "Check the message types rather than reading the text."
            ),
            "command": (
                'python -c "from langchain.agents import create_agent; '
                "from langchain_openai import ChatOpenAI; from tools import word_count; "
                "a = create_agent(ChatOpenAI(model='gpt-4o-mini'), tools=[word_count]); "
                "r = a.invoke({'messages': [{'role': 'user', 'content': 'count the words in: a b c'}]}); "
                "types = [m.type for m in r['messages']]; "
                "print(types); assert 'tool' in types, 'the tool never ran'\""
            ),
            "expected_result": "The list contains a `tool` entry and the assertion passes.",
            "caution": (
                "Assert on types, not on wording. Checking for a specific number in the answer "
                "makes the test fail whenever the model phrases the result differently."
            ),
        },
    ],
    "stage.state.configure-persistence": [
        {
            "title": "Choose a checkpointer",
            "action": (
                "Use InMemorySaver while developing and SqliteSaver when the conversation has to "
                "survive a process restart."
            ),
            "command": (
                'python -c "from langgraph.checkpoint.memory import InMemorySaver; '
                'print(type(InMemorySaver()).__name__)"'
            ),
            "expected_result": "The script prints `InMemorySaver`.",
            "caution": (
                "InMemorySaver loses everything when the process exits. A multi-turn demo that "
                "works until you restart is this mistake, not a LangChain bug."
            ),
        },
    ],
    "stage.state.create-agent": [
        {
            "title": "Create the agent with a checkpointer",
            "action": "Pass the checkpointer into create_agent alongside the model and tools.",
            "command": (
                'python -c "from langchain.agents import create_agent; '
                "from langchain_openai import ChatOpenAI; "
                "from langgraph.checkpoint.memory import InMemorySaver; "
                "a = create_agent(ChatOpenAI(model='gpt-4o-mini'), tools=[], "
                "checkpointer=InMemorySaver()); print('created')\""
            ),
            "expected_result": "The script prints `created`.",
            "caution": (
                "An agent with a checkpointer but no thread_id raises at invoke time, not at "
                "creation time. The error appears one Stage later than the mistake."
            ),
        },
    ],
    "stage.state.invoke-thread": [
        {
            "title": "Invoke twice with the same thread_id",
            "action": "Send two turns in separate invoke calls, sharing one config.",
            "command": (
                'python -c "from langchain.agents import create_agent; '
                "from langchain_openai import ChatOpenAI; "
                "from langgraph.checkpoint.memory import InMemorySaver; "
                "a = create_agent(ChatOpenAI(model='gpt-4o-mini'), tools=[], "
                "checkpointer=InMemorySaver()); "
                "cfg = {'configurable': {'thread_id': 'demo-1'}}; "
                "a.invoke({'messages': [{'role': 'user', 'content': 'My name is Sam.'}]}, cfg); "
                "r = a.invoke({'messages': [{'role': 'user', 'content': 'What is my name?'}]}, cfg); "
                "print([m.content for m in r['messages'] if m.type == 'ai'][-1])\""
            ),
            "expected_result": "The printed answer mentions `Sam`.",
            "caution": (
                "The returned list ends with the question you just sent, so read the answer from "
                "the last `ai` message rather than `messages[-1]`. A new thread_id per call gives "
                "a new conversation every time, which looks like memory not working."
            ),
        },
    ],
    "stage.state.verify-memory": [
        {
            "title": "Assert the second turn saw the first",
            "action": (
                "Ask for the name and check the answer mentions it. Asking for a name is the "
                "weak choice available here, so also print the message count, which is what "
                "actually distinguishes remembered from forgotten."
            ),
            "command": (
                'python -c "from langchain.agents import create_agent; '
                "from langchain_openai import ChatOpenAI; "
                "from langgraph.checkpoint.memory import InMemorySaver; "
                "a = create_agent(ChatOpenAI(model='gpt-4o-mini'), tools=[], "
                "checkpointer=InMemorySaver()); "
                "cfg = {'configurable': {'thread_id': 'demo-1'}}; "
                "a.invoke({'messages': [{'role': 'user', 'content': 'My name is Sam.'}]}, cfg); "
                "r = a.invoke({'messages': [{'role': 'user', 'content': 'What is my name?'}]}, cfg); "
                "print('kept', len(r['messages']), 'messages:', [m.type for m in r['messages']]); "
                "assert len(r['messages']) >= 3, 'the first turn was not carried over'; "
                "answer = [m for m in r['messages'] if m.type == 'ai'][-1]; "
                "assert 'Sam' in answer.content, 'the answer did not use the first turn'; "
                "print('remembered')\""
            ),
            "expected_result": (
                "`kept 3 messages: ['human', 'ai', 'human']` and then `remembered`. Three "
                "messages on the second call means the first turn came back with the history; "
                "an agent with no checkpointer returns two."
            ),
            "caution": (
                "Read the answer out of the last `ai` message, not `messages[-1]`. With a "
                "checkpointer the list ends with the question you just asked, so `[-1]` is that "
                "question and asserting on it can never succeed. If only two messages come back, "
                "the model answered from general behaviour rather than from your thread. If this "
                "fails outright, check the thread_id first and the checkpointer second: a "
                "recreated agent with a fresh checkpointer starts empty every run."
            ),
        },
    ],
    "stage.rag.prepare-knowledge-access": [
        {
            # The loader is given a path that nothing in the COP creates, so this
            # Stage failed at its first command. Retrieval has to be grounded in
            # something, and that something has to exist before it is loaded.
            "title": "Create the document the retriever will read",
            "action": (
                "Write the source text to a file first. The next step loads this path, so it has "
                "to exist before anything can retrieve from it."
            ),
            "command": (
                "cat > notes.txt <<'TXT'\n"
                "The retry limit is three attempts.\n"
                "Uploads above 20 MB are rejected by the API.\n"
                "Session state is kept per thread_id, not per user.\n"
                "TXT"
            ),
            "expected_result": "`cat notes.txt` prints the three lines above.",
            "caution": (
                "A retriever over a file you did not write cannot be verified: the answer is "
                "then indistinguishable from the model answering from memory, which is the exact "
                "failure this Goal exists to rule out."
            ),
        },
        {
            "title": "Load and split a document set",
            "action": "Load the text, split it into overlapping chunks, and keep the chunks in memory.",
            "command": (
                'python -c "from langchain_community.document_loaders import TextLoader; '
                "from langchain_text_splitters import RecursiveCharacterTextSplitter; "
                "docs = TextLoader('notes.txt').load(); "
                "chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)"
                '.split_documents(docs); print(len(chunks))"'
            ),
            "expected_result": (
                "The script prints a chunk count greater than zero. Two extra packages are "
                "needed for this step alone: `pip install -U langchain-community "
                "langchain-text-splitters`."
            ),
            "caution": (
                "A zero here usually means the file path is wrong, not that the splitter is "
                "broken. Check the path before changing the chunk size."
            ),
        },
    ],
    "stage.rag.expose-retrieval-tool": [
        {
            "title": "Wrap the retriever as a tool",
            "action": "Write a function that searches the documents and returns text.",
            "command": (
                "cat > search.py <<'PY'\n"
                "from langchain.tools import tool\n\n"
                "CHUNKS: list[str] = []\n\n"
                "@tool\n"
                "def search_notes(query: str) -> str:\n"
                '    \\"\\"\\"Search the project notes and return matching text.\\"\\"\\"\n'
                "    hits = [c for c in CHUNKS if query.lower() in c.lower()]\n"
                '    return "\\n".join(hits[:3]) or "no match"\n'
                "PY"
            ),
            "expected_result": (
                '`python -c "import search"` exits 0. An import failure here is almost always '
                "an unclosed heredoc rather than bad Python."
            ),
            "caution": (
                "Returning an empty string makes the model believe the answer is 'nothing "
                "found'. Return an explicit 'no match' so it can say so."
            ),
        },
    ],
    "stage.rag.create-agent": [
        {
            "title": "Create the agent with the retrieval tool",
            "action": (
                "This imports search.py, written by the step 'Wrap the retriever as a tool'. The process order is what makes it exist; running this Stage on its own fails with ModuleNotFoundError, which means the step was skipped rather than that the code is wrong. "
                "Pass the search tool and a system prompt that permits using it."
            ),
            "command": (
                'python -c "from langchain.agents import create_agent; '
                "from langchain_openai import ChatOpenAI; from search import search_notes; "
                "a = create_agent(ChatOpenAI(model='gpt-4o-mini'), tools=[search_notes], "
                "system_prompt='Use search_notes for anything about the project notes.'); "
                "print('created')\""
            ),
            "expected_result": "The script prints `created`.",
            "caution": (
                "Without a system prompt the model often answers from its own knowledge instead "
                "of retrieving, and the agent looks broken when it is merely misdirected."
            ),
        },
    ],
    "stage.rag.invoke": [
        {
            "title": "Ask a question only the notes answer",
            "action": (
                "This imports search.py, written by the step 'Wrap the retriever as a tool'. The process order is what makes it exist; running this Stage on its own fails with ModuleNotFoundError, which means the step was skipped rather than that the code is wrong. "
                "Invoke with a question whose answer is not general knowledge."
            ),
            "command": (
                'python -c "from langchain.agents import create_agent; '
                "from langchain_openai import ChatOpenAI; from search import search_notes; "
                "a = create_agent(ChatOpenAI(model='gpt-4o-mini'), tools=[search_notes]); "
                "r = a.invoke({'messages': [{'role': 'user', 'content': "
                "'What does the notes file say about the retry limit?'}]}); "
                "[print(m.type) for m in r['messages']]\""
            ),
            "expected_result": "The list includes a `tool` message carrying the search result.",
            "caution": (
                "The retrieval must happen for a question the model cannot already answer. "
                "Testing with 'what is Python' proves nothing."
            ),
        },
    ],
    "stage.rag.verify-grounding": [
        {
            "title": "Check the answer is backed by a retrieved chunk",
            "action": (
                "This imports search.py, written by the step 'Wrap the retriever as a tool'. The process order is what makes it exist; running this Stage on its own fails with ModuleNotFoundError, which means the step was skipped rather than that the code is wrong. "
                "Confirm a tool message exists and the final answer quotes something from it."
            ),
            "command": (
                'python -c "from langchain.agents import create_agent; '
                "from langchain_openai import ChatOpenAI; from search import search_notes; "
                "a = create_agent(ChatOpenAI(model='gpt-4o-mini'), tools=[search_notes]); "
                "r = a.invoke({'messages': [{'role': 'user', 'content': "
                "'What do the notes say about the retry limit?'}]}); "
                "tool = [m for m in r['messages'] if m.type == 'tool']; "
                "assert tool, 'nothing was retrieved'; "
                "print('grounded in', len(tool[0].content), 'chars')\""
            ),
            "expected_result": "The script prints `grounded in N chars`.",
            "caution": (
                "Asserting on the presence of a tool message is the check that matters. "
                "Comparing the answer to an expected string tests the model, not the agent."
            ),
        },
    ],
    "stage.middleware.choose-control": [
        {
            "title": "Name the behaviour that needs controlling",
            "action": "Write down the specific failure being prevented before choosing middleware.",
            "command": (
                "python -c \"open('control.md','w').write("
                "'Failure to prevent: the agent calls the delete_project tool on a request that "
                "mentions removing something.\\n"
                "Required behaviour: refuse unless the request contains the word CONFIRM.\\n')\""
            ),
            "expected_result": (
                "`cat control.md` prints one line beginning `Failure to prevent:` and one "
                "beginning `Required behaviour:`."
            ),
            "caution": (
                "Choosing middleware first and looking for a use case afterwards produces a "
                "guardrail that guards nothing."
            ),
        },
    ],
    "stage.middleware.configure": [
        {
            "title": "Write the guardrail middleware",
            "action": "Hook the model call and raise unless the text carries the confirmation word.",
            "command": (
                "cat > guard.py <<'PY'\n"
                "from langchain.agents.middleware import AgentMiddleware\n\n"
                "class RequireConfirm(AgentMiddleware):\n"
                "    def before_model(self, state, runtime):\n"
                "        text = str(state['messages'][-1].content).upper()\n"
                "        if 'CONFIRM' not in text:\n"
                "            raise PermissionError('refused: request lacks CONFIRM')\n"
                "        return None\n"
                "PY"
            ),
            "expected_result": '`python -c "import guard"` exits 0, defining the class.',
            "caution": (
                "Raising from a hook stops the run. Returning None lets it continue, so a guard "
                "that returns None unconditionally guards nothing."
            ),
        },
    ],
    "stage.middleware.attach": [
        {
            "title": "Pass the middleware into create_agent",
            "action": (
                "This imports guard.py, written by the step 'Write the guardrail middleware'. The process order is what makes it exist; running this Stage on its own fails with ModuleNotFoundError, which means the step was skipped rather than that the code is wrong. "
                "Include the instance in the middleware list at construction."
            ),
            "command": (
                'python -c "from langchain.agents import create_agent; '
                "from langchain_openai import ChatOpenAI; from guard import RequireConfirm; "
                "a = create_agent(ChatOpenAI(model='gpt-4o-mini'), tools=[], "
                "middleware=[RequireConfirm()]); print('created')\""
            ),
            "expected_result": "The script prints `created`.",
            "caution": (
                "Order matters: an outer middleware sees the request first. Putting a logging "
                "middleware outside the guard means it records the refused attempts too."
            ),
        },
    ],
    "stage.middleware.verify": [
        {
            "title": "Assert the guard blocks and then allows",
            "action": (
                "This imports guard.py, written by the step 'Write the guardrail middleware'. The process order is what makes it exist; running this Stage on its own fails with ModuleNotFoundError, which means the step was skipped rather than that the code is wrong. "
                "Run one request without the word and one with it."
            ),
            "command": (
                'python -c "from langchain.agents import create_agent; '
                "from langchain_openai import ChatOpenAI; from guard import RequireConfirm; "
                "a = create_agent(ChatOpenAI(model='gpt-4o-mini'), tools=[], "
                "middleware=[RequireConfirm()]); "
                "blocked = False\n"
                "try:\n"
                "    a.invoke({'messages': [{'role': 'user', 'content': 'delete the project'}]})\n"
                "except PermissionError:\n"
                "    blocked = True\n"
                "assert blocked, 'the guard did not block'; print('guard works')\""
            ),
            "expected_result": "The script prints `guard works`.",
            "caution": (
                "Only testing the blocked case passes trivially. Also run an allowed request, or "
                "you have verified a middleware that refuses everything."
            ),
        },
    ],
}

EXAMPLES: dict[str, dict[str, str]] = {
    "stage.foundation.install": {
        "summary": "A fresh virtual environment with LangChain importable.",
        "input": "python3 -m venv .venv && source .venv/bin/activate && pip install -U langchain",
        "output": "Successfully installed langchain-1.x langchain-core-1.x ...",
        "note": "The version line is the check: no version means the install did not land here.",
    },
    "stage.foundation.model": {
        "summary": "The model answers without any agent involved.",
        "input": "ChatOpenAI(model='gpt-4o-mini').invoke('reply with the word ok')",
        "output": "ok",
        "note": "Isolating the model first means a later failure is never a key problem.",
    },
    "stage.basic.create-agent": {
        "summary": "An agent object exists with an empty tool set.",
        "input": "create_agent(ChatOpenAI(model='gpt-4o-mini'), tools=[])",
        "output": "created",
        "note": "No network call happens here, so this is safe to run offline.",
    },
    "stage.basic.invoke": {
        "summary": "A one-turn exchange returns a final message.",
        "input": "{'role': 'user', 'content': 'Name one benefit of agents.'}",
        "output": "Agents can choose which tool to call for a given request.",
        "note": "messages[-1] is the answer; messages[0] is what you sent.",
    },
    "stage.basic.inspect": {
        "summary": "The execution is two messages: the one sent and the one returned.",
        "input": "print each message's type",
        "output": "human 'hi' / ai 'Hello! How can I help you today?'",
        "note": "Reading types rather than text is what makes the tool loop legible later.",
    },
    "stage.tool.define": {
        "summary": "A typed function becomes a callable tool.",
        "input": "@tool def word_count(text: str) -> int",
        "output": "3",
        "note": "The docstring is the tool's description; without one it is rarely chosen.",
    },
    "stage.tool.create-agent": {
        "summary": "The constructed agent reports the tools it holds.",
        "input": "create_agent(model, tools=[word_count])",
        "output": "['word_count']",
        "note": "Tools bind at construction, so a later mutation has no effect.",
    },
    "stage.tool.invoke": {
        "summary": "A tool-requiring request produces four messages.",
        "input": "'How many words are in: the quick brown fox jumps'",
        "output": "human / ai(tool call) / tool(3) / ai(final answer)",
        "note": "Only human and ai means the model declined to call the tool.",
    },
    "stage.tool.verify-loop": {
        "summary": "The tool loop is confirmed by message types, not by wording.",
        "input": "assert 'tool' in [m.type for m in result['messages']]",
        "output": "['human', 'ai', 'tool', 'ai']",
        "note": "Asserting on wording tests the model's phrasing, which is not the point.",
    },
    "stage.state.configure-persistence": {
        "summary": "A checkpointer is constructed and usable.",
        "input": "InMemorySaver()",
        "output": "InMemorySaver",
        "note": "In-memory state does not survive a process restart; use SqliteSaver for that.",
    },
    "stage.state.create-agent": {
        "summary": "An agent holding a checkpointer is created.",
        "input": "create_agent(model, tools=[], checkpointer=InMemorySaver())",
        "output": "created",
        "note": "A missing thread_id fails at invoke, one Stage after the mistake.",
    },
    "stage.state.invoke-thread": {
        "summary": "Two turns under one thread_id form a conversation.",
        "input": "'My name is Sam.' then 'What is my name?'",
        "output": "Your name is Sam.",
        "note": "The same config object must be passed to both calls.",
    },
    "stage.state.verify-memory": {
        "summary": "The second turn demonstrably used the first.",
        "input": "assert len(result['messages']) >= 3",
        "output": "kept 3 messages: ['human', 'ai', 'human'] / remembered",
        "note": "The message count is the test; the name alone can be guessed.",
    },
    "stage.rag.prepare-knowledge-access": {
        "summary": "A document set is split into retrievable chunks.",
        "input": "TextLoader('notes.txt').load() then split at 500/50",
        "output": "17",
        "note": "Zero chunks means the path is wrong, not that the splitter failed.",
    },
    "stage.rag.expose-retrieval-tool": {
        "summary": "The retriever is callable from the agent.",
        "input": "search_notes('retry limit')",
        "output": "The retry limit is three attempts.",
        "note": "Return an explicit 'no match' rather than an empty string.",
    },
    "stage.rag.create-agent": {
        "summary": "The agent is told it may retrieve.",
        "input": "create_agent(model, tools=[search_notes], system_prompt='Use search_notes ...')",
        "output": "created",
        "note": "Without the system prompt the model often answers from memory instead.",
    },
    "stage.rag.invoke": {
        "summary": "A question only the notes can answer triggers retrieval.",
        "input": "'What does the notes file say about the retry limit?'",
        "output": "human / ai(tool call) / tool(...) / ai(final answer)",
        "note": "A question the model already knows will not trigger the tool.",
    },
    "stage.rag.verify-grounding": {
        "summary": "The final answer is backed by retrieved text.",
        "input": "assert a tool message exists",
        "output": "grounded in 82 chars",
        "note": "Asserting on presence of retrieval, not on the answer's exact wording.",
    },
    "stage.middleware.choose-control": {
        "summary": "One failure and one required behaviour, written down.",
        "input": "delete_project called without explicit confirmation",
        "output": "refuse unless the request contains CONFIRM",
        "note": "Middleware chosen before the failure is a guardrail that guards nothing.",
    },
    "stage.middleware.configure": {
        "summary": "The guard raises on an unconfirmed request.",
        "input": "before_model checks the last message for 'CONFIRM'",
        "output": "PermissionError: refused: request lacks CONFIRM",
        "note": "Returning None continues the run; raising is what stops it.",
    },
    "stage.middleware.attach": {
        "summary": "The guarded agent is constructed.",
        "input": "create_agent(model, tools=[], middleware=[RequireConfirm()])",
        "output": "created",
        "note": "An outer middleware sees the request first and the response last.",
    },
    "stage.middleware.verify": {
        "summary": "The guard blocks one request and allows another.",
        "input": "'delete the project' (blocked) then 'CONFIRM delete' (allowed)",
        "output": "guard works",
        "note": "Testing only the blocked case passes even for a middleware that refuses everything.",
    },
}

COMMON_FAILURES: dict[str, list[str]] = {
    "operation.install": [
        "Installed into the system interpreter, so the project's venv cannot see the package.",
        "A stale virtual environment from an earlier project shadows the new install.",
    ],
    "operation.configure": [
        "The setting is supplied but never read, because the component was already constructed.",
        "A value is set in one module and read in another that was never given it.",
    ],
    "operation.create": [
        "A string is passed where a model instance is expected, producing a type error.",
        "The component is created before its configuration is complete.",
    ],
    "operation.invoke": [
        "A thread_id or config is missing on a stateful agent, and the error names invoke "
        "rather than the missing config.",
        "The result is indexed as an object when it is a dict, so .content raises AttributeError.",
    ],
    "operation.inspect": [
        "messages[0] is read as the answer, but it is the message that was sent.",
        "Output is printed in full, so the one line that matters is lost in the volume.",
    ],
    "operation.define": [
        "A tool has no docstring, so the model has nothing to match the request against.",
        "The function's type hints do not describe the real input, so the generated schema lies.",
    ],
    "operation.attach": [
        "The tool or middleware is added to a list after the agent was constructed, so it is "
        "never bound.",
        "Middleware is ordered inside-out, so the outer guard never sees the request first.",
    ],
    "operation.verify": [
        "Only the passing case is tested, so a component that refuses everything looks correct.",
        "The assertion compares against model wording, which changes without any code change.",
    ],
    "operation.select": [
        "A capability is chosen before the failure it should prevent is written down.",
        "Two capabilities are added at once, so neither can be shown to work.",
    ],
    "operation.prepare": [
        "The document path is wrong, producing zero chunks and a retrieval tool that never fires.",
        "Chunks are too large to retrieve precisely, so every query returns most of the corpus.",
    ],
    "operation.retrieve": [
        "The tool returns an empty string, so the model reads it as 'nothing found' rather than "
        "as a failure.",
        "Retrieval is never triggered because the question is answerable from general knowledge.",
    ],
    "operation.persist": [
        "An in-memory checkpointer is used in a process that restarts, and the history is lost.",
        "A new thread_id is generated per request, so every call is a separate conversation.",
    ],
}


def _set(artifact: dict[str, Any], collection: str, entity_id: str, **fields: Any) -> None:
    for entity in artifact.get(collection, []):
        if entity.get("id") == entity_id:
            entity.update(fields)
            return
    raise KeyError(f"{entity_id} not found in {collection}")


def enrich(artifact: dict[str, Any]) -> dict[str, Any]:
    for stage_id, details in DETAILS.items():
        _set(
            artifact,
            "stages",
            stage_id,
            implementation_details=details,
            example=EXAMPLES[stage_id],
        )
    for operation_id, failures in COMMON_FAILURES.items():
        _set(artifact, "operations", operation_id, common_failures=failures)

    declared = set((artifact.get("metadata") or {}).get("source_ids") or [])
    for stage in artifact["stages"]:
        for ref in stage.get("evidence_refs") or []:
            if ref["source_id"] not in declared:
                raise ValueError(f"stage {stage['id']} cites undeclared source {ref['source_id']}")
    for goal in artifact["goals"]:
        for ref in goal.get("evidence_refs") or []:
            if ref["source_id"] not in declared:
                raise ValueError(f"goal {goal['id']} cites undeclared source {ref['source_id']}")
    return artifact


def sources() -> list[dict[str, Any]]:
    """The Source rows a seed must create for every citation to resolve."""
    return [
        {
            "id": source_id,
            "title": data["title"],
            "original_uri": data["uri"],
            "text": data["text"],
        }
        for source_id, data in SOURCES.items()
    ]


def main() -> None:
    with FIXTURE.open(encoding="utf-8") as handle:
        artifact = json.load(handle)
    enriched = enrich(artifact)

    from jsonschema import Draft202012Validator

    with SCHEMA.open(encoding="utf-8") as handle:
        errors = list(Draft202012Validator(json.load(handle)).iter_errors(enriched))
    if errors:
        for error in errors[:5]:
            location = "/".join(str(part) for part in error.absolute_path) or "(root)"
            print(f"schema error at {location}: {error.message}", file=sys.stderr)
        raise SystemExit("enriched artifact does not satisfy the canonical schema")

    # Written next to the artifact and read by the seed. A citation is only
    # traceable if the thing it points at exists, so the sources are part of the
    # fixture rather than an assumption about the user's project.
    SOURCES_OUT.write_text(
        json.dumps(sources(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    with FIXTURE.open("w", encoding="utf-8") as handle:
        json.dump(enriched, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(
        f"Wrote {len(DETAILS)} Stages with content, {len(COMMON_FAILURES)} Operations with "
        f"failures, and {len(SOURCES)} sources"
    )


if __name__ == "__main__":
    main()
