# ChatGPT Pro Review Packet for ICECCME 2026

Use this packet by attaching `paper/iceccme2026/main.pdf` to ChatGPT Pro and pasting the prompt below.

## Prompt to ChatGPT Pro

You are acting as an award-level reviewer for ICECCME 2026. Please review the attached six-page IEEE conference paper as if the goal were not only acceptance, but making the paper competitive for a best paper award.

Paper title:
`A Japanese-Human-Grounded Benchmark for Literary Emotion Understanding with Multilingual Robustness Tests`

Review context:
- This is a compact engineering conference paper.
- The primary endpoint is Japanese human alignment against student-reader Visual Analogue Scale (VAS) reference data.
- English and Chinese conditions are robustness tests for cross-language drift, not co-equal human-grounded endpoints.
- The paper should remain within the six-page IEEE format.
- Do not assume that new experiments, new model runs, or new human data can be added in the immediate revision cycle.
- The desired revision should improve reviewer robustness, claim precision, and presentation quality without overclaiming.

Please provide a severe, concrete, and actionable review with the following structure:

1. Overall judgment
   - State whether the paper is currently weak accept, accept, strong accept, or award-competitive.
   - Explain the main reason in 3 to 5 sentences.

2. Severity-ranked findings
   - List findings in descending severity.
   - For each finding, include:
     - severity: critical, major, moderate, or minor;
     - location: title, abstract, introduction, methods, results, discussion, figures, tables, or references;
     - problem;
     - why it matters to reviewers;
     - concrete revision recommendation.

3. Novelty and contribution assessment
   - Assess whether the contribution is sufficiently distinct from general LLM emotion benchmarks and prior VAS/human-alignment work.
   - Identify the strongest possible framing for this paper.
   - Identify any novelty claims that should be weakened or made more precise.

4. Methodological risk assessment
   - Evaluate the main risks in:
     - three-text design;
     - Japanese student-reader reference;
     - six-model panel;
     - translated English and Chinese conditions;
     - descriptive rather than inferential analysis;
     - use of current model display names and API-mediated execution.
   - For each risk, say whether it can be handled by wording, a limitation paragraph, a table/caption change, or whether it would require new experiments.

5. Missing citations or related-work gaps
   - Identify only citation categories or specific references that are genuinely important for reviewer confidence.
   - Do not invent citations.
   - Distinguish must-add citations from optional citations.

6. Overclaim and ambiguity audit
   - Quote or paraphrase any sentence-level claims that may be too strong, ambiguous, or vulnerable.
   - Suggest safer replacement wording.

7. Figure and table audit
   - Assess whether each figure and table earns its space in a six-page paper.
   - Identify any caption, label, or metric-definition issue that could confuse reviewers.
   - Recommend compression only if it improves the paper.

8. Must fix before submission
   - Provide a short checklist of changes that should be made before submission.

9. Nice to improve if space remains
   - Provide a separate short checklist of improvements that are useful but not required.

10. Rebuttal guidance
   - Give the response strategy the authors should use after revision.
   - Include the likely reviewer concerns and the strongest concise author responses.

Important constraints:
- Keep your review in English.
- Be direct and rigorous.
- Do not recommend unsupported claims.
- Do not ask for new experiments unless you explicitly mark them as beyond the immediate revision cycle.
- Prefer edits that preserve the six-page limit.

## Codex Follow-up Procedure

After ChatGPT Pro returns the review, paste the full review back into Codex. Codex will:

1. Triage every finding as accepted, partially accepted, rejected/deferred, or clarification needed.
2. Edit only the ICECCME manuscript and ICECCME revision notes unless explicitly instructed otherwise.
3. Preserve the endpoint hierarchy: Japanese human alignment is primary; English and Chinese are robustness tests.
4. Avoid adding experiments, model runs, fake references, or unsupported claims.
5. Rebuild `paper/iceccme2026/main.pdf` and verify that it remains six pages.
6. Draft an English rebuttal back to ChatGPT Pro.
