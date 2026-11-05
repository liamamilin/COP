# Learning-unit acceptance worksheet

This worksheet is for a **person who did not author the lesson**. It is not a
model self-assessment, a code review, or a substitute for the contract tests.

Status: **PENDING**. Do not mark it passed from tests, a successful offline run,
clicks on navigation, or the author's opinion. One real learner attempt is one
data point, not proof that automatic production works across domains.

## Unit under test

- Unit: `unit.langchain-basic.private-agent`
- Bound artifact: `fixtures/langchain-basic-cop.json` at the manifest hash.
- Path attempted: `offline` / `provider` (circle one).
- If provider: whose credentials, rough budget, and explicit permission to spend.
  Record only "own paid account" or similar; never write a key here.
- Date, machine, OS, Python version, terminal. Keep the lesson unchanged during
  the attempt; record every page or command you had to leave it to consult.

## Before the attempt

The learner must meet the declared starting point: can edit files and run Python
in a terminal, has Python 3.10+, and does not need to know LangChain already.
The learner must **not** read the hidden checklist below or this document's
expectations before finishing. The facilitator may read the setup section aloud.

- [ ] The learner has never completed this unit and did not help write it.
- [ ] The learner knows they may ask for help and that asking is recorded.
- [ ] No one tells them the answers, corrective steps, or the transfer task.
- [ ] They know the page does not run commands or save project progress.
- [ ] They know to stop before anything that may cost money and to ask first.
- [ ] Notes will contain no keys, tokens, private endpoints, or personal data.

## Attempt log

Record observable events, quotes, and timestamps. "They seemed to understand"
is not evidence. "They asked where `config.py` should be saved" is.

| # | What the learner did or said | Help given (exact words) | Did it unblock them? | Evidence |
|---|---|---|---|---|

Minimum observations to record, not prompts to feed:

1. Where they looked to find the next action.
2. Any concept they re-read or asked about, and what they thought it meant.
3. Any command or value they had to get from outside the unit.
4. Whether they checked the result themselves or declared success.
5. Whether they noticed that a planned input was not proven complete.
6. Where they stopped and why.

## Task 1 — complete the declared path

- [ ] They reached an actual result using the unit, without facilitator typing.
- [ ] For `offline`, they state that the fixed reply proves the pipeline only.
- [ ] For `provider`, they made **one** call with explicit cost consent and did
      not retry blindly.
- [ ] They saved the result file and inspected that same file rather than
      invoking again to "see" it.
- [ ] They did **not** paste secrets into notes, chat, or the worksheet.

Facilitator note: a run that succeeded by copying the author's private `.env` or
by skipping checks is not this task. Record what actually happened.

## Task 2 — explain a choice (no hints first)

Ask: "Why does `config.py` refuse a base URL containing `/chat/completions` or a
key?" Then, if needed: "What would go into a log or a shared screenshot?" Do not
supply the answer.

- [ ] Names the request-path vs base-URL confusion.
- [ ] Names credential exposure/logging risk.
- [ ] Connects it to a consequence in this lesson.
- [ ] Uses their own words; no verbatim page recital required.
- Hints used (count and which): ____
- Outside sources used: ____

## Task 3 — diagnose a failure

Present, without fixing it: "The terminal says `AuthenticationError (HTTP 401)`
and `first-run.json` was not created. What do you check next, and what must you
not do?" Do not say whether their answer is right yet.

- [ ] Separates "request failed" from "inspection failed".
- [ ] Checks key validity/ownership and the provider, not a random retry loop.
- [ ] Does not reuse an old or offline report as this run's success.
- [ ] Avoids exposing the key in terminal history, screenshots, or notes.
- [ ] Can say what evidence would show the problem is resolved.
- Hints used: ____

## Task 4 — near transfer

Ask the learner to change the system instruction to "Answer in Chinese, with one
specific benefit" and to judge the change without paying twice for the same
result. Do not dictate the file or flag names.

- [ ] Finds the configuration entry rather than editing `agent.py`'s formatting.
- [ ] Chooses a new output filename and preserves the earlier record.
- [ ] Keeps inspection on the saved file and states that semantics need human
      judgement.
- [ ] Explains why an unrelated change (e.g. editing only the prompt text in the
      console) would not test the configuration path.
- Hints used: ____

If they cannot do this, record the smallest prompt that was needed. That prompt is
a lesson defect candidate, not a learner failure.

## Delayed recheck (next day or later)

- [ ] Reconstructs the path from the unit without repeating every step.
- [ ] Explains the three evidence layers (construction, structure, semantics).
- [ ] Names one thing they would verify before trusting a generated lesson.
- [ ] Performs one nearby variation without a walkthrough.

## Stop rules

Stop and record a defect if any of these occur. Do not "help through" them and
then count the unit as passed.

- A load-bearing concept has no in-unit explanation or example.
- A required file, value, permission, or service is missing from the declared
  starting point or resources.
- A step cannot be completed from its declared inputs, or a prior planned output
  is treated as verified work.
- The only way forward is guessing, an external tutorial the unit did not name,
  or a paid call without explicit consent.
- A check can pass while the stated outcome is false.
- The learner cannot distinguish their own result from a worked illustration.
- Completing navigation is presented as learning or mastery.
- Credentials or private data appear in notes, screenshots, logs, or exports.

## Result (facilitator completes)

- Outcome: PASS / PARTIAL / FAIL (delete two).
- What the learner could do unaided:
- What needed help, with exact prompts:
- Defects with file/step references:
- Evidence retained (paths, not pasted secrets):
- Explicit limits of this evidence:
- Next action: fix the unit / re-test with another learner / do not generalize yet.

A PASS here supports only that this unit helped this learner on this attempt. It
does not establish stable automatic generation, cross-domain quality, or that the
generator will produce equally sound lessons. Those require separate held-out
generation and review with explicit budget.
