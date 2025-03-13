# PonensPal

**PonensPal** is an extremely, almost laughably simple, simple proof of concept logic combining AI-powered language understanding with classic propositional logic.  

Intention of this is not to produce another logic tool.  I think plenty of these tools exist and how useful they actually are is something I'm not entirely sure of (who cares if something is true.  More interesting is why it's true imo).  This is just a simple experiment in aligning language model behavior with "truthfulness". Large language models (LLMs) frequently produce plausible-sounding but incorrect claims. By translating ambiguous natural language into explicit propositional logic, automatically verifying conclusions with Modus Ponens, and translating structured proofs back into intuitive explanations, PonensPal tests whether structured logical reasoning can act as a safeguard against the confident hallucinations inherent to modern LLMs.

This project serves as a starting point for exploring more rigorous automated reasoning systems and formal specification languages. In future experiments, I plan to integrate tools such as Lean, Coq, Isabelle, and formal specification languages like TLA+ and Alloy, to investigate whether increased logical rigor can further enhance LLM accuracy, reliability, and interpretability.


Note: Initially I set out to write a simple REPL interpreter capable of parsing basic matrices and vector notation and do some funky linear algebra stuff. However, I got distracted.  

Addtional notes: Create an llm from scratch where entire training set is missing one letter.  E maybe?  What would happen, would it still be able to "understand" lanuage?  IDK another rabbit hole.

---

## Overview

PonensPal is designed to showcase how easy it can be to reason logically using:

- **ChatGPT API** for translating natural language into formal logic.
- **Local logical interpreter** to parse and represent logical statements.
- **Forward chaining (modus ponens)** algorithm to generate logical proofs.

Whether you're studying logic, philosophy, AI, or just enjoy puzzles, PonensPal makes logical reasoning fun and accessible!

---

## Project Structure

- **Logical Interpreter:** Defines logical structures (`Var`, `Imp`, `Not`) and parsing functions.
- **Prover**: Implements forward chaining reasoning to derive conclusions.
- **ChatGPT Integration**:
  - Converts natural language to propositional logic.
  - Translates formal proofs into readable natural language.

---

## Dependencies

- Python 3.x
- OpenAI Python SDK:

```bash
pip install openai
```

---

## Setup

1. **OpenAI API Key**:

Set your OpenAI API key in your environment:

```bash
export OPENAI_API_KEY='your-api-key-here'
```

2. **Run the script:**

```bash
python your_script_name.py
```

---

## Code Explanation

### Logical Interpreter

**Classes:**

- **`Formula`**: Base class for logic formulas.
- **`Var`**: Logical variables (e.g., `p`).
- **`Imp`**: Logical implications (`p -> q`).
- **`Not`**: Logical negation (`~p`).

**Parser:**

- Converts strings to structured logical formulas using tokens (`->`, `~`, parentheses).

**Prover (`prove` function):**

- Implements a forward chaining (modus ponens) algorithm:
  - Starts from premises.
  - Applies implications to derive conclusions.
  - Tracks each step for clear proof explanations.

### ChatGPT Integration

- **`convert_to_logic`**: Sends arguments in natural language to ChatGPT, receives propositional logic representation.
- **`translate_proof`**: (Optional)
  - Converts formal proofs back into natural language explanations using ChatGPT.

### Main Pipeline

- **Natural argument ➡ Formal logic** (ChatGPT)
- **Formal logic ➡ Proof** (Local prover)
- **Proof ➡ Natural language explanation** (optional) wip

---

##  Usage

- Update `natural_argument` in the `main()` function to test your arguments.
- Run the script:

```bash
python your_script_name.py
```

- Review the step-by-step logic proof directly in the terminal.

---

##  Notes and Limitations

- The local prover only uses simple forward chaining and does not handle complex proofs.
- ChatGPT responses must follow the exact format to be parsed correctly.

