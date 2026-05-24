import re
from typing import List, Tuple, Dict, Any

MAX_OPTIONS = 15

ANSWER_PATTERN = re.compile(r"^ans(?:wer)?\s*:", flags=re.IGNORECASE)
SOLUTION_PATTERN = re.compile(
    r"^(?:solution|explanation|exp|sol|reason|hint)\s*:", flags=re.IGNORECASE
)
OPTION_PATTERN = re.compile(r"^([A-Za-z])[).]\s+(.+)$")


def parse_quiz_file(content: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    questions = []
    errors = []

    blocks = re.split(r"\n\s*\n", content.strip())

    for block_num, block in enumerate(blocks, 1):
        block = block.strip()
        if not block:
            continue

        result, error = parse_question_block(block, block_num)
        if error:
            errors.append(f"Question {block_num}: {error}")
        elif result:
            questions.append(result)

    return questions, errors


def parse_question_block(
    block: str, block_num: int
) -> Tuple[Dict[str, Any] | None, str | None]:
    lines = [line.strip() for line in block.strip().splitlines() if line.strip()]

    if len(lines) < 3:
        return None, "Too few lines (need question + options + answer)"

    answer_line_idx = None
    answer_line = None
    for i, line in enumerate(lines):
        if ANSWER_PATTERN.match(line):
            answer_line_idx = i
            answer_line = line
            break

    if answer_line is None:
        return None, "No 'Answer:' line found"

    solution_text = None
    solution_start_idx = None

    for i in range(answer_line_idx + 1, len(lines)):
        if SOLUTION_PATTERN.match(lines[i]):
            sol_match = re.match(
                r"^(?:solution|explanation|exp|sol|reason|hint)\s*:\s*(.*)",
                lines[i],
                re.IGNORECASE,
            )
            if sol_match:
                sol_parts = [sol_match.group(1).strip()]
                for j in range(i + 1, len(lines)):
                    sol_parts.append(lines[j])
                solution_text = " ".join(p for p in sol_parts if p)
                solution_start_idx = i
            break
        else:
            sol_parts = []
            for j in range(i, len(lines)):
                sol_parts.append(lines[j])
            solution_text = " ".join(sol_parts)
            solution_start_idx = i
            break

    question_lines = []
    option_lines = []

    for i, line in enumerate(lines):
        if i == answer_line_idx:
            continue
        if solution_start_idx is not None and i >= solution_start_idx:
            continue
        if OPTION_PATTERN.match(line):
            option_lines.append(line)
        elif not option_lines:
            question_lines.append(line)

    if not question_lines:
        return None, "No question text found"

    question_text = " ".join(question_lines)

    if len(option_lines) < 2:
        return None, f"Too few options ({len(option_lines)}), need at least 2"

    if len(option_lines) > MAX_OPTIONS:
        return None, f"Too many options ({len(option_lines)}), maximum {MAX_OPTIONS} allowed"

    options = []
    option_letters = []
    for line in option_lines:
        m = OPTION_PATTERN.match(line)
        if m:
            letter = m.group(1).upper()
            text = m.group(2).strip()
            options.append(text)
            option_letters.append(letter)

    answer_match = re.search(
        r"^ans(?:wer)?\s*:\s*([A-Za-z])", answer_line, re.IGNORECASE
    )
    if not answer_match:
        return None, "Could not parse answer letter from 'Answer:' line"

    correct_letter = answer_match.group(1).upper()

    if correct_letter not in option_letters:
        return None, (
            f"Answer '{correct_letter}' does not match any option letter "
            f"({', '.join(option_letters)})"
        )

    correct_index = option_letters.index(correct_letter)

    question_text = question_text[:255]
    options = [opt[:100] for opt in options]

    if solution_text:
        solution_text = solution_text[:200]

    return {
        "question": question_text,
        "options": options,
        "correct_index": correct_index,
        "correct_letter": correct_letter,
        "solution": solution_text,
    }, None
