import openai
import re
from collections import deque
import os

from openai import OpenAI
client = OpenAI(api_key="")  # Replace with your API key

# -----------------------------------------------------------------
# 1. Logical Interpreter for Propositional Logic (with Negation)
# -----------------------------------------------------------------

class Formula:
    def __eq__(self, other):
        return isinstance(other, Formula) and self.__dict__ == other.__dict__
    
    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))
    
    def __str__(self):
        raise NotImplementedError

class Var(Formula):
    def __init__(self, name):
        self.name = name.strip()
    
    def __str__(self):
        return self.name

class Imp(Formula):
    def __init__(self, antecedent, consequent):
        self.antecedent = antecedent  # Formula
        self.consequent = consequent  # Formula
    
    def __str__(self):
        ant = f"({self.antecedent})" if isinstance(self.antecedent, Imp) else str(self.antecedent)
        return f"{ant} -> {self.consequent}"

class Not(Formula):
    def __init__(self, operand):
        self.operand = operand  # Formula
    
    def __str__(self):
        return "~" + str(self.operand)

def tokenize(s):
    # Include '~' as a token.
    token_pattern = r'\s*(->|\(|\)|~|[A-Za-z]+)\s*'
    tokens = re.findall(token_pattern, s)
    return [t.strip() for t in tokens if t.strip() != '']

def parse_formula(s):
    s = s.strip()
    tokens = tokenize(s)
    
    def parse_formula_tokens(i):
        lhs, i = parse_atom(i)
        if i < len(tokens) and tokens[i] == '->':
            i += 1  # consume '->'
            rhs, i = parse_formula_tokens(i)
            return Imp(lhs, rhs), i
        return lhs, i
    
    def parse_atom(i):
        # Handle negation: if token is '~', parse the next atom.
        if tokens[i] == "~":
            i += 1
            operand, i = parse_atom(i)
            return Not(operand), i
        if tokens[i] == '(':
            i += 1  # consume '('
            inner, i = parse_formula_tokens(i)
            if i >= len(tokens) or tokens[i] != ')':
                raise ValueError("Missing closing parenthesis")
            i += 1  # consume ')'
            return inner, i
        else:
            token = tokens[i]
            i += 1
            return Var(token), i
    
    formula, index = parse_formula_tokens(0)
    if index != len(tokens):
        raise ValueError("Extra tokens after parsing complete formula.")
    return formula

def prove(goal_str, premise_strs):
    """
    Given a goal (as a string) and a list of premises (each a string),
    attempts to prove the goal using forward chaining (modus ponens) and
    returns a string with the proof steps.
    
    Note: This simple prover does not perform proof by contradiction.
    """
    goal = parse_formula(goal_str)
    premises = [parse_formula(p) for p in premise_strs]
    
    known = {}  # maps formulas to their explanation string
    queue = deque()
    
    # Initialize known with premises.
    for p in premises:
        known[p] = f"Premise: {p}"
        queue.append(p)
    
    steps = []
    
    while queue:
        current = queue.popleft()
        # Only run inference if the goal isn't already derived.
        if current == goal:
            break
        for f in list(known.keys()):
            if isinstance(f, Imp):
                if f.antecedent in known and f.consequent not in known:
                    explanation = (
                        f"From '{known[f.antecedent]}' and the implication '{f}', "
                        f"by modus ponens we deduce '{f.consequent}'."
                    )
                    known[f.consequent] = explanation
                    steps.append(explanation)
                    queue.append(f.consequent)
                    if f.consequent == goal:
                        break
    if goal in known:
        result = f"Goal '{goal}' was proven.\nProof steps:\n" + "\n".join(steps)
    else:
        result = f"Unable to prove the goal '{goal}'. Known formulas: " + ", ".join(str(f) for f in known)
    return result

# -----------------------------------------------------------------
# 2. ChatGPT API Integration Functions
# -----------------------------------------------------------------

def convert_to_logic(natural_language):
    """
    Uses the ChatGPT API to convert a natural language argument into propositional logic.
    The output must be exactly in the following format (with no extra text):

    Mapping:
    p: [Meaning of p]
    q: [Meaning of q]
    r: [Meaning of r]
    ...

    Premises:
    1. [Formula1]
    2. [Formula2]
    3. [Any additional premise, including given facts]

    Goal: [Formula]

    Argument:
    [The formal derivation, if applicable]

    Argument:
    [The natural language argument]
    """
    prompt = (
        "Convert the following natural language argument into propositional logic. "
        "Assign propositional variables as needed and provide a mapping of each variable to its original meaning. "
        "Ensure that ALL premises (including given facts) are included in the 'Premises:' section. "
        "All negations should be represented with '~'. "
        "Use ASCII symbols for logical operators (e.g., '->' for implication). "
        "Output ONLY in the exact format below with no additional text:\n\n"
        "Mapping:\n"
        "p: [Meaning of p]\n"
        "q: [Meaning of q]\n"
        "...\n\n"
        "Premises:\n"
        "1. [Formula1]\n"
        "2. [Formula2]\n"
        "...\n\n"
        "Goal: [Formula]\n\n"
        "Argument:\n"
        "[The formal derivation, if applicable]\n\n"
        "Argument:\n" + natural_language
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    logic_text = response.choices[0].message.content
    return logic_text

def translate_proof(formal_proof, mapping):
    """
    Uses the ChatGPT API to translate a formal proof into a clear, step-by-step natural language explanation,
    replacing propositional variables with their original meanings as provided in the mapping.
    
    mapping: a dict, e.g., {'p': 'It is raining', 'q': 'The ground is wet', 'r': 'The roads are slippery'}
    """
    mapping_str = "\n".join(f"{var}: {meaning}" for var, meaning in mapping.items())
    
    prompt = (
        "Translate the following formal proof into a clear, step-by-step natural language explanation, "
        "replacing each propositional variable with its original meaning as provided in the mapping below. "
        "Include justifications for each inference.\n\n"
        "Mapping:\n" + mapping_str + "\n\n"
        "Formal Proof:\n" + formal_proof + "\n\n"
        "Provide a human-friendly explanation."
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    explanation = response.choices[0].message.content
    return explanation

# -----------------------------------------------------------------
# 3. File Input and Main Pipeline
# -----------------------------------------------------------------

def read_examples_from_file(file_path):
    """
    Reads natural language arguments from a text file.
    Each example should be separated by one or more blank lines.
    """
    try:
        with open(file_path, "r") as f:
            content = f.read()
            # Split on two or more newlines to separate examples.
            examples = [ex.strip() for ex in content.split("\n\n") if ex.strip()]
        return examples
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []

def process_examples(file_label, examples):
    """
    Processes a list of natural language arguments.
    """
    print(f"\n======== Processing {file_label} Examples ========")
    for idx, natural_argument in enumerate(examples, start=1):
        print(f"\n---------------------\nExample {idx}:")
        print("Natural Language Argument:")
        print(natural_argument)
        
        print("\n--- Converting to Propositional Logic via ChatGPT ---")
        logic_conversion = convert_to_logic(natural_argument)
        print("ChatGPT Logic Conversion:")
        print(logic_conversion)
        
        # Parse the ChatGPT output.
        mapping = {}
        premise_lines = []
        goal_line = None
        
        lines = logic_conversion.splitlines()
        lines = [line.strip() for line in lines if line.strip() != ""]
        
        section = None
        for line in lines:
            if line.startswith("Mapping:"):
                section = "mapping"
                continue
            elif line.startswith("Premises:"):
                section = "premises"
                continue
            elif line.startswith("Goal:"):
                section = "goal"
                content = line[len("Goal:"):].strip()
                if content:
                    goal_line = content
                continue
            # We ignore the "Argument:" sections.
            
            if section == "mapping":
                if ":" in line:
                    var, meaning = line.split(":", 1)
                    mapping[var.strip()] = meaning.strip()
            elif section == "premises":
                if re.match(r"^\d+\.", line):
                    parts = line.split('.', 1)
                    if len(parts) > 1:
                        premise_lines.append(parts[1].strip())
                else:
                    premise_lines.append(line)
            elif section == "goal":
                if not goal_line:
                    goal_line = line.strip()
        
        if not goal_line or not premise_lines or not mapping:
            print("Error: Unable to parse ChatGPT output. Please check the format.")
            continue

        print("\nParsed Mapping:")
        for var, meaning in mapping.items():
            print(f"{var}: {meaning}")
        print("\nParsed Premises:")
        for p in premise_lines:
            print(p)
        print("Parsed Goal:")
        print(goal_line)
        
        print("\n--- Running Local Prover ---")
        formal_proof = prove(goal_line, premise_lines)
        print("Formal Proof Output:")
        print(formal_proof)
        
        # Optionally, you can uncomment the following lines to translate the formal proof to natural language.
        # print("\n--- Translating Formal Proof to Natural Language Explanation ---")
        # nl_explanation = translate_proof(formal_proof, mapping)
        # print("Natural Language Explanation:")
        # print(nl_explanation)

def main():
    # Files with examples.
    valid_file = "examples.txt"
    fallacious_file = "fallacious_examples.txt"
    polymarket_file = "polymarket_getrich_scheme.txt"
    
    valid_examples = read_examples_from_file(valid_file)
    fallacious_examples = read_examples_from_file(fallacious_file)
    polymarket_examples = read_examples_from_file(polymarket_file)
    
    if not valid_examples:
        print(f"No valid examples found in {valid_file}. Please add examples to the file.")
    else:
        process_examples("Valid", valid_examples)
    
    if not fallacious_examples:
        print(f"No fallacious examples found in {fallacious_file}. Please add examples to the file.")
    else:
        process_examples("Fallacious", fallacious_examples)
    
    if not polymarket_examples:
        print(f"No Polymarket GetRich Scheme examples found in {polymarket_file}. Please add examples to the file.")
    else:
        process_examples("Polymarket GetRich Scheme", polymarket_examples)

if __name__ == "__main__":
    main()
