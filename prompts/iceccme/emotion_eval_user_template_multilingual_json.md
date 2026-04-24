Task:
Read the literary text below and rate four reader-side emotions on a 0 to 100 integer scale.

Persona:
- persona_id: {persona_id}
- persona_name: {persona_name}
- persona_description: {persona_description}
- temperature: {temperature}

Output language:
{language_name}

Dimensions and definitions:
- interest: {interest_definition}
- surprise: {surprise_definition}
- sadness: {sadness_definition}
- anger: {anger_definition}

Scoring rules:
- use integers only
- 0 means the emotion is not felt at all
- 50 means moderately felt
- 100 means extremely strongly felt
- rate the text as a whole after reading it
- keep each reason brief and grounded in the text

Return exactly one JSON object matching the schema.

Text identifier: {story_id}
Title: {story_title}
Author: {story_author}
Language of this prompt: {language_code}

Text:
{text_body}
