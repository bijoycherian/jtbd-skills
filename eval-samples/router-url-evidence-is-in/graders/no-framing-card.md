---
type: llm
---

The user gave only a website, plus which customers and which decision.
PASS if the reply does not ask the user to choose between a suggested research question and their own request (no framing question), and goes on to the evidence summary and the proposed framing (main goal, who, when) with numbered choices about that framing.
FAIL if it asks the user to switch to a different research question or to keep their own, or if job statements are drafted or a jobs.csv is written before the user answers the framing choices.
