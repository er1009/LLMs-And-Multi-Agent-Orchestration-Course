# PRD Creation Prompt

## Initial Prompt Used to Create PRD

The following prompt was used to generate the Product Requirements Document (PRD) for this project:

```
I need to create a PRD for a chat application project with the following requirements:

Assignment Goal: Understand and implement work with local models, API connection, GUI creation, and professional documentation.

Assignment Topic:
- Building a chat application (Desktop/GUI App) that works with a local model.

Technical Requirements:
- Goal: Create a simple GUI (similar to Claude, Gemini, ChatGPT) for local Ollama environment.
- Model: Can choose any model, but recommended to start with the smallest available (e.g., 20MB model for quick tests).
- Technology: Programming language of choice (HTML, JavaScript, Python, etc.). No limitation except must use venv and requirements.txt.
- API: Must connect to local model via API (not via Web interface).

Submission Requirements (mandatory - industrial level):
- Submission location: Public GitHub repository.
- Documentation (README.md): Must include:
  - Screenshots of running interface.
  - Detailed and accurate installation instructions (so project can be run).
  - Unit tests - must include expected results of tests.
- Work process documentation:
  - Must add Documentation folder in repository.
  - In this folder, must present the initial prompt used to create the PRD (Product Requirements Document) and build the project. Must show how the AI was prompted and tuned.

Please create a comprehensive PRD that includes:
1. Project overview and objectives
2. Technical requirements
3. Implementation details
4. Testing requirements
5. Documentation requirements
6. Success criteria

The PRD should be clear, actionable, and suitable for an LLM coding agent to implement.
```

## Prompt Refinements

### Initial Version
The initial prompt was based directly on the assignment requirements in Hebrew, translated to English.

### Refinements Made
1. **Clarified API requirement**: Emphasized that connection must be via API, not web interface
2. **Added structure**: Organized requirements into clear sections
3. **Emphasized documentation**: Made documentation requirements explicit
4. **Added success criteria**: Included measurable outcomes

## What Worked Well

1. **Clear structure**: Breaking down requirements into sections made it easier for the AI to understand
2. **Explicit constraints**: Stating "must use venv and requirements.txt" was clear
3. **Examples**: Mentioning "similar to Claude, Gemini, ChatGPT" provided visual context
4. **Documentation emphasis**: Making documentation requirements explicit ensured they were included

## Notes

- The PRD was generated from the translated assignment requirements
- The SPEC.md file contains the full PRD that was created from this prompt
- The prompt was effective in generating a comprehensive specification document

