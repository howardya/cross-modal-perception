# Objective

## The statement

> Build an interactive visual experience that lets an ordinary person briefly perceive a
> familiar stimulus the way someone else perceives it — and, in doing so, understand that
> their own way of seeing is one option among many rather than the neutral default.
>
> The mechanism is **cross-modal rendering**: translating meaning, salience and expertise into
> colour, weight, texture, grouping and time, so that difference registers pre-verbally, before
> it can be argued with. The variable is **the viewer**: the same stimulus, rendered through
> several different minds, shown as a live morph between them.
>
> The work must be honest as well as beautiful. Every perceptual difference shown is derived
> from published research on perceptual expertise and cross-modal correspondence, quantified
> with a stated model, calibrated against measured effect sizes, and accompanied by an explicit
> account of what is measured versus what is modelled.

## The problem

People assume they see what others see.

Two professionals read the identical paragraph and walk away with incompatible conclusions,
each certain the text plainly said what they took from it. Neither is lying and neither is
careless. They are running different perceptual machinery over the same input.

This is invisible from the inside. You cannot perceive your own perceptual filter, because it
is the thing doing the perceiving. The filter presents its output as simply *what is there*.

Synesthesia is the most vivid available proof that this is false — that perception is
constructed rather than received. But almost nobody will experience it. This project builds the
closest legitimate substitute: a way to briefly wear someone else's filter and notice the seam.

## What it must achieve

Three things, in priority order.

**1. A felt shift, not an explanation.**
Success is a viewer saying *"oh — that's what she sees"* while looking at the screen, not after
reading a caption. The transition between perspectives is what carries the meaning, so it must
be animated and continuous. A static side-by-side comparison is the failure mode: it invites
analysis, and analysis is exactly the mode we are trying to bypass.

**2. Personal implication.**
The viewer must find themselves in it. They mark up the stimulus first, with their own reading,
before seeing anyone else's. Their own baseline is what turns the comparison from an interesting
fact about other people into a fact about themselves.

**3. Defensible rigour.**
It must survive a hostile question. *"Where did those numbers come from?"* needs a real answer,
including an honest one about the limits.

## What it is not

- Not a claim to simulate synesthesia clinically.
- Not a claim to have measured real experts' eye movements.
- Not a personality quiz.
- Not an argument that all readings are equally valid. Differences in perception are **shown**,
  not adjudicated.

## The conceptual join (load-bearing)

The project's title and its case studies name two genuinely distinct phenomena:

| | Cross-modal perception | Perceptual expertise |
|---|---|---|
| Nature | Sensory | Learned |
| Examples | Synesthesia, bouba/kiki, pitch–brightness | Chunking, schema-driven salience, information reduction |
| Acquired | Involuntary, present in infancy | Over years of practice |
| Scope | Largely universal in direction | Domain-bound |

These are separate literatures. This project deliberately joins them, and **the join is the
contribution** rather than a confusion to be tidied away:

> **Cross-modal correspondence supplies the rendering language. Expertise supplies the
> difference being rendered.**

The bridge between them is **learned pop-out**. A grapheme–colour synesthete finds a `2` hidden
in a field of `5`s instantly, because for them it is coloured. A credit analyst finds the
covenant risk in a paragraph instantly, because for them it is salient. Structurally the same
phenomenon; different origin — one innate, one earned.

This distinction must be stated openly in the work rather than blurred. Blurring it is the
weakest point of the whole idea. Stating it is the strongest.

## Case studies

Built in order. Depth beats breadth: a finished first case is worth more than three unfinished ones.

1. **Finance** — how a credit analyst, an equity PM, a risk officer and a retail investor read
   the same analyst note. Built to full depth.
2. **Music notation** — how a professional and an amateur see the same score.
3. **Poetry** — how a poet, a critic and a casual reader read the same poem.

## Scope decisions

| Decision | Choice |
|---|---|
| Framing | Two acts — cross-modal perception established literally, then applied to expertise |
| Grounding | Literature-anchored priors + LLM personas, calibrated to published effect sizes |
| First case study | Finance, to full depth |
| Audio | Out of scope. Visual only |
| Runtime | Precomputed calibrated hero stimuli, plus a separate clearly-labelled live mode |
| Delivery | Built locally, exported as a self-contained shareable page |
| Time budget | 1–2 weeks |

## Definition of done

The demo answers *"where did these numbers come from?"* on its own, without the author present.
