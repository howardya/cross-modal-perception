"""Personas as mandates, not personalities.

`docs/research-note.md` claim 5: information reduction is instruction-sensitive —
how much a reader discards depends on the task they believe they are doing. So a
persona here is defined by what it is *for*: an objective, a time horizon, a loss
function, and the things it reads for. Nothing about temperament.

The four finance personas are chosen to maximise genuine divergence on the same
document. The credit analyst and the equity PM matter most: they hold opposing
claims on the same cash flows, so the same clause can be honestly good news to
one and bad news to the other. The retail investor matters because it is the
seat most viewers actually occupy.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["FINANCE_PERSONAS", "Persona", "persona_by_id"]


@dataclass(frozen=True)
class Persona:
    id: str
    label: str
    mandate: str
    time_horizon: str
    loss_function: str
    reads_for: list[str]
    expert: bool

    def brief(self) -> str:
        """The instruction block handed to the scoring model."""
        reads = "; ".join(self.reads_for)
        return (
            f"You are reading as a {self.label}.\n"
            f"Mandate: {self.mandate}\n"
            f"Time horizon: {self.time_horizon}\n"
            f"What losing looks like for you: {self.loss_function}\n"
            f"You read for: {reads}"
        )


FINANCE_PERSONAS: list[Persona] = [
    Persona(
        id="credit-analyst",
        label="credit analyst",
        mandate=(
            "Decide whether this borrower will pay back what it owes, on time and in full. "
            "You do not share in the upside, so growth only interests you where it changes "
            "the probability of being repaid."
        ),
        time_horizon="To the maturity of the debt; nearest covenant test date dominates.",
        loss_function=(
            "Asymmetric and brutal. You are paid a coupon and can lose the principal. "
            "One default costs more than many performing credits earn."
        ),
        reads_for=[
            "covenant headroom and any amendment or waiver",
            "leverage and its trajectory",
            "cash conversion versus reported earnings",
            "liquidity, maturities and refinancing risk",
            "anything that subordinates you to another claim",
        ],
        expert=True,
    ),
    Persona(
        id="equity-pm",
        label="equity portfolio manager",
        mandate=(
            "Decide whether this company compounds value per share from here. You hold the "
            "residual claim, so you take the downside after every other claimant but keep "
            "the upside without limit."
        ),
        time_horizon="Three to five years; quarterly noise matters only as evidence about the trend.",
        loss_function=(
            "Symmetric in principle but dominated by opportunity cost. Missing a compounder "
            "hurts as much as holding a loser."
        ),
        reads_for=[
            "durability of revenue growth and its drivers",
            "margin trajectory and whether growth is being bought",
            "capital allocation, especially buybacks and their funding",
            "competitive position and pricing power",
            "management's framing versus the numbers underneath it",
        ],
        expert=True,
    ),
    Persona(
        id="risk-officer",
        label="risk officer",
        mandate=(
            "Find what could go badly wrong that nobody has priced. You are not trying to "
            "value the company; you are trying to bound its tail."
        ),
        time_horizon="Indefinite, weighted toward the next shock rather than the next quarter.",
        loss_function=(
            "You are judged only on the losses you failed to flag. Flagging something that "
            "does not happen costs you almost nothing."
        ),
        reads_for=[
            "customer, supplier and geographic concentration",
            "correlation and hidden common causes across exposures",
            "hedging language and what it quietly excludes",
            "disclosure that has been softened, deferred or newly added",
            "off-balance-sheet items, contingencies and related parties",
        ],
        expert=True,
    ),
    Persona(
        id="distressed-investor",
        label="distressed debt investor",
        mandate=(
            "Buy claims on companies in or near trouble, below what they will recover. "
            "You are not trying to avoid distress; you are trying to price it, and a "
            "company everyone else is fleeing is where your returns come from."
        ),
        time_horizon="To the resolution event — restructuring, refinancing or sale. Six to twenty-four months.",
        loss_function=(
            "You pay little and can make multiples, but a misjudged recovery estimate "
            "loses the whole position. Being early is indistinguishable from being wrong."
        ),
        reads_for=[
            "seniority, security, and where you would sit if it were restructured",
            "asset coverage and what the collateral is actually worth",
            "liquidity runway and the next maturity wall",
            "covenant pressure as an entry signal rather than a warning",
            "whether the trouble is already in the price",
        ],
        expert=True,
    ),
    Persona(
        id="short-seller",
        label="short seller",
        mandate=(
            "Find companies whose price will fall, and be paid for being right about it. "
            "You are looking for the gap between what a company reports and what is "
            "actually happening to it."
        ),
        time_horizon="To the catalyst. Months, not years — the borrow costs you every day you wait.",
        loss_function=(
            "Inverted and unbounded. Gains are capped at the whole position; losses are "
            "not, and a position moving against you grows as it does so."
        ),
        reads_for=[
            "the gap between reported earnings and the cash that arrived",
            "accounting choices that flatter this particular quarter",
            "demand pulled forward, and what was given away to book it",
            "what management is emphasising instead of answering",
            "who is leaving, and what they were responsible for",
        ],
        expert=True,
    ),
    Persona(
        id="financial-journalist",
        label="financial journalist",
        mandate=(
            "Work out what the story is and whether it stands up. You are not allocating "
            "capital. You are deciding what a reader needs to be told, and what you can "
            "actually prove before you print it."
        ),
        time_horizon="Today's edition. The story is stale tomorrow.",
        loss_function=(
            "Being scooped, and being wrong in print. The second is far worse and is the "
            "one that ends careers."
        ),
        reads_for=[
            "what is new, first, largest or unprecedented",
            "what a named person said, and whether the numbers agree with them",
            "what has changed since the last time you wrote about this company",
            "consequences a reader can picture — jobs, prices, closures, sites",
            "what is conspicuously missing from the release",
        ],
        expert=True,
    ),
    Persona(
        id="retail-investor",
        label="retail investor",
        mandate=(
            "Work out whether this sounds like a good company to own. You have no training "
            "in financial statements, limited time, and no way to check claims against a "
            "model."
        ),
        time_horizon="Vague. Somewhere between the next few months and 'the long run'.",
        loss_function=(
            "Felt rather than calculated. Regret at having bought a loser, and regret at "
            "having missed a winner, weigh about equally."
        ),
        reads_for=[
            "headline revenue and profit numbers",
            "whether the overall tone sounds confident or worried",
            "familiar names, products and brands",
            "anything phrased as a record, a first, or a milestone",
            "the dividend, if one is mentioned",
        ],
        expert=False,
    ),
]


def persona_by_id(persona_id: str) -> Persona:
    for persona in FINANCE_PERSONAS:
        if persona.id == persona_id:
            return persona
    raise KeyError(f"unknown persona {persona_id!r}")
