Task:
Read the literary text below and rate four emotions on a 0 to 100 integer scale.

Evaluation target:
- target_mode: {target_mode}
- target_label: {target_label}
- focus: {target_focus}

Output language:
{language_name}

Dimensions and definitions:
- interest: {interest_definition}
- surprise: {surprise_definition}
- sadness: {sadness_definition}
- anger: {anger_definition}

Scoring rules:
- use integers only
- 0 means the emotion is not present at all
- 50 means moderately present
- 100 means extremely strongly present
- rate the text as a whole after reading it
- keep each reason brief and grounded in the text

Return exactly one JSON object matching the schema.
Use persona_id "p0" and language "{language_code}" in the JSON object.

Text identifier: {story_id}
Title: {story_title}
Author: {story_author}
Language of this prompt: {language_code}

Text:
{text_body}
