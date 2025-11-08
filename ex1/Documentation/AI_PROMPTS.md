# AI Prompting and Tuning Documentation

## Overview

This document tracks all prompts used with AI assistants during the development of this project, including iterations, refinements, and lessons learned.

## Prompt Categories

### 1. PRD Creation Prompts

**Initial Prompt:**
```
I need to create a PRD for a chat application project with the following requirements:
[Assignment requirements in English]
Please create a comprehensive PRD that includes:
1. Project overview and objectives
2. Technical requirements
3. Implementation details
4. Testing requirements
5. Documentation requirements
6. Success criteria
```

**Result:** Generated SPEC.md with complete project specification.

**What Worked:**
- Clear structure with numbered requirements
- Explicit sections requested
- Context provided upfront

### 2. Implementation Prompts

**Code Generation Prompt:**
```
implement the project. i want clean, concise implementation.
```

**Refinements:**
- Initial implementation created basic structure
- Follow-up: "make sure its robust and that we can have a conversation there. i want it clean and simple."
- Fixed conversation history handling
- Switched from `/api/generate` to `/api/chat` endpoint

**Results:**
- Clean, modular code structure
- Proper conversation history management
- Robust error handling

**What Worked:**
- Simple, direct requests
- Iterative refinement based on issues
- Focus on specific problems (conversation history, API endpoint)

**What Didn't Work Initially:**
- Using `/api/generate` endpoint didn't support conversation history properly
- Conversation history format was incorrect
- Had to switch to `/api/chat` endpoint

### 3. Setup and Configuration Prompts

**Environment Setup:**
```
create the conda v env and run the project i want top test it
```

**Result:** Created conda environment, installed dependencies, verified setup.

**Ollama Setup:**
```
lets download olama and run it so the apllication can use it. i want also to use the simplest model i can.
```

**Result:** Installed Ollama via Homebrew, started service, pulled tinyllama model (637MB).

**What Worked:**
- Step-by-step approach
- Verification after each step
- Clear feedback on status

### 4. Code Quality Prompts

**Cleanup Request:**
```
great now please clean up the project from unesessary files.
```

**Result:** Removed temporary files, cache files, unused directories.

**What Worked:**
- Simple, clear request
- AI identified and removed unnecessary files automatically

### 5. Bug Fixing Prompts

**Chat Functionality:**
```
seems like the chat is not working so well. make sure its robust and that we can have a conversation there. i want it clean and simple.
```

**Refinements Made:**
1. Switched from `/api/generate` to `/api/chat` endpoint
2. Fixed conversation history format
3. Improved error handling
4. Cleaned up UI

**What Worked:**
- Identifying specific issues (conversation history, API endpoint)
- Iterative fixes
- Testing after each fix

## Prompt Engineering Strategies

### Effective Patterns

1. **Clear Structure**: Use numbered lists and clear sections
   - Example: "1. Create API client, 2. Create GUI, 3. Integrate"

2. **Context First**: Provide background before asking for action
   - Example: "The chat is not working well. Make sure it's robust..."

3. **Specific Requests**: Be specific about what you want
   - Example: "clean, concise implementation" vs "make it better"

4. **Iterative Refinement**: Fix issues one at a time
   - Example: First implement, then fix conversation history, then clean up

### Less Effective Patterns

1. **Vague Requests**: "Make it better" without specifics
2. **Too Many Requirements at Once**: Overwhelming prompts
3. **Lack of Context**: Not providing enough background

## Key Learnings

1. **API Endpoint Matters**: Using the correct Ollama API endpoint (`/api/chat` vs `/api/generate`) is crucial for conversation history
2. **Message Format**: Conversation history must be in the correct format: `[{"role": "user", "content": "..."}, ...]`
3. **Iterative Development**: Starting simple and refining works better than trying to get everything perfect at once
4. **Clear Communication**: Simple, direct prompts work better than complex instructions

## Best Practices Identified

1. **Start Simple**: Begin with basic implementation, then refine
2. **Test Incrementally**: Test after each major change
3. **Document Issues**: Note what doesn't work and why
4. **Use Correct APIs**: Research API documentation before implementation
5. **Clean Code**: Keep code clean and simple from the start

## Prompt Templates

### For Code Generation:
```
implement [feature]. i want [quality attributes: clean, concise, robust, etc.]
```

### For Bug Fixing:
```
[describe the issue]. make sure [expected behavior]. i want [quality attributes].
```

### For Setup:
```
[action: create, install, setup] [component]. [additional requirements]
```

### For Cleanup:
```
please clean up the project from [what to remove: unnecessary files, etc.]
```

## Effectiveness Summary

**Most Effective Prompts:**
- Simple, direct requests: "implement the project"
- Specific quality requirements: "clean, concise implementation"
- Problem-focused: "chat is not working so well, make sure it's robust"

**Less Effective:**
- Vague requests without context
- Too many requirements in one prompt
- Missing context about current state

