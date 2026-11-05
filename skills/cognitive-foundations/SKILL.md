---
name: cognitive-foundations
description: Build grounded, first-principles understanding of a subject without turning it into a step-by-step SOP. Use when someone asks what a field fundamentally is, how experts think about it, or which conceptual model should guide their work.
---

# Cognitive Foundations · 认知地基

## Purpose
Help a learner construct a useful understanding of a subject, anchored in a concrete starting point. This is a separate mode from COP's Goal → Process → Stage → Concept × Operation execution paths. Do not force a topic into the COP process schema.

## Core commitments
- **Start on the ground.** Identify an observable object, event, artifact, or minimal example the learner can inspect. Distinguish this pedagogical entry point from a claim about the field's ultimate foundation.
- **Seek explanatory power, not completeness.** Prefer a few central mechanisms over a long, symmetrical taxonomy.
- **Understanding is not procedure.** Explain why concepts exist, what relationships they describe, when they matter, and what breaks if assumptions change. Do not default to numbered implementation steps.
- **Do not fabricate consensus.** Separate established theory, synthesized interpretation, and speculation. If experts disagree, state the meaningful alternatives.
- **Use examples to test abstraction.** Return to a concrete case; show what the model explains and where it fails.
- **Admit unknowns.** State unresolved questions instead of filling a template.

## Interaction
Given a subject or question:
1. Propose a **concrete foothold** and a one-sentence claim about the nature of the activity. If the domain is ambiguous, ask a focused question.
2. Expose the **minimum essential concepts and their causal/logical relationships**, with a running example. Choose the concepts that actually explain the subject; no fixed number of dimensions.
3. Show the **expert's judgments**: what distinctions they notice, which trade-offs they weigh, and which assumptions change the conclusion.
4. Test understanding with a **counterexample or boundary case**. Revise the model when it fails.
5. Close with **one consequential open question** or a suggested experiment, not a generic SOP.

These are quality checks for the response, **not** mandatory output sections or a fixed sequence. Follow the user's inquiry organically.

## First pilot: software development
Starting point: a small order record with identity, attributes, state, and allowed transitions. This is one useful foothold, not the only possible foundation.
Central claim: software development constructs and revises an executable system of representations and behaviors to achieve a purpose.
Investigate how domain distinctions become data models, how rules become state transitions, how interfaces and components distribute responsibility, and how tests/observations challenge both implementation and original assumptions.
Boundary test: a creative game does not merely mirror existing business objects; software may create new rules and worlds.

## Second pilot: Agent applications
Starting point: a goal, an observable environment, a permitted action, and feedback.
Central question: when may a system choose actions based on observations instead of following only a predetermined path?
Investigate goals, state/observations, tool effects, planning, permissions, uncertainty, evaluation, and human control. Contrast with deterministic workflow automation; not every LLM-powered application is an agent.

## Output quality bar
A useful answer lets the learner explain **why** a concept matters and apply it to a novel example. Reject impressive but empty lists. Never imply that a model of a field guarantees success in practice.
