"""Run the personas over a stimulus and report whether the result is defensible.

The report is the published artefact of Phase 3: per-persona reliability, the L1
acceptance verdict against the author-assigned relevance masks, and every
pairwise divergence. A failing check is recorded and rendered, never suppressed —
the point of building the acceptance layer was to be able to fail.

The lay persona (retail investor) is the novice baseline every expert field is
measured against, so it is not itself subject to the expertise check.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from cmp.field import PerceptualField, StimulusFieldSet
from cmp.personas import FINANCE_PERSONAS, persona_by_id
from cmp.reliability import ReliabilityDiagnosis, ReliabilityVerdict, diagnose_reliability
from cmp.scoring import ScoringClient, score_persona
from cmp.stimuli import LoadedStimulus
from cmp.targets import SUPPRESSION_ASYMMETRY, SignatureCheck, check_expertise_signature

__all__ = ["CalibrationReport", "build_report", "run_calibration"]


@dataclass(frozen=True)
class CalibrationReport:
    stimulus_id: str
    stimulus_title: str
    field_set: StimulusFieldSet
    reliabilities: dict[str, ReliabilityVerdict]
    diagnoses: dict[str, ReliabilityDiagnosis]
    signature_checks: dict[str, SignatureCheck]
    baseline_persona: str

    @property
    def comparisons(self) -> list[dict]:
        return self.field_set.comparisons()

    @property
    def passed(self) -> bool:
        checks_ok = all(c.passed for c in self.signature_checks.values())
        # Reliability is judged by the diagnosis, not by alpha alone: a persona
        # attending near-uniformly has too little between-clause signal for alpha
        # to mean anything, and failing it on that basis would be wrong.
        reliability_ok = all(d.reliable for d in self.diagnoses.values())
        return checks_ok and reliability_ok

    def to_markdown(self) -> str:
        verdict = "PASS" if self.passed else "FAIL"
        lines = [
            f"# Calibration report — {self.stimulus_title}",
            "",
            f"**Verdict: {verdict}**",
            "",
            f"Stimulus `{self.stimulus_id}`, "
            f"{len(self.field_set.stimulus.texts)} clauses, "
            f"{len(self.field_set.fields)} personas. "
            f"Novice baseline: `{self.baseline_persona}`.",
            "",
            "## Reliability (agreement of each persona with itself)",
            "",
            "Alpha is read alongside concentration. Krippendorff's alpha divides by the",
            "spread of scores across clauses, so a persona attending near-uniformly can",
            "score near zero even when its runs agree — which is the expected shape for a",
            "lay reader, not a defect. A low alpha with *concentrated* attention is the",
            "real failure: the persona is picking different clauses each run.",
            "",
            "| Persona | alpha | Concentration | Reading |",
            "|---|---|---|---|",
        ]
        for persona_id, diag in sorted(self.diagnoses.items()):
            if diag.erratic:
                reading = "**erratic**"
            elif diag.diffuse:
                reading = "diffuse (alpha uninformative)"
            else:
                reading = "reliable"
            lines.append(
                f"| `{persona_id}` | {diag.alpha:.3f} | {diag.concentration:.3f} | {reading} |"
            )

        notable = {p: d for p, d in self.diagnoses.items() if d.diffuse or d.erratic}
        if notable:
            lines += ["", "### Reliability notes", ""]
            for persona_id, diag in sorted(notable.items()):
                lines.append(f"- `{persona_id}`: {diag.summary}")

        lines += [
            "",
            "## Literature acceptance (L1)",
            "",
            f"Target asymmetry from the research note: {SUPPRESSION_ASYMMETRY:.2f} "
            f"(reported, not gated — see docs/calibration.md section 2).",
            "",
            "| Persona | Enhancement | Suppression | Asymmetry | Concentration vs novice | Result |",
            "|---|---|---|---|---|---|",
        ]
        for persona_id, check in sorted(self.signature_checks.items()):
            s = check.signature
            lines.append(
                f"| `{persona_id}` | {s.enhancement:.2f}x | {s.suppression:.2f}x | "
                f"{s.asymmetry:.2f} | {s.expert_concentration:.3f} vs "
                f"{s.novice_concentration:.3f} | {'pass' if check.passed else '**FAIL**'} |"
            )

        failures = {p: c for p, c in self.signature_checks.items() if not c.passed}
        if failures:
            lines += ["", "### Why these failed", ""]
            for persona_id, check in sorted(failures.items()):
                for reason in check.reasons:
                    lines.append(f"- `{persona_id}`: {reason}")

        lines += [
            "",
            "## Pairwise divergence",
            "",
            "| Persona A | Persona B | Perceptual overlap | Valence conflicts | Chunk agreement |",
            "|---|---|---|---|---|",
        ]
        for c in self.comparisons:
            a, b = c["personas"]
            lines.append(
                f"| `{a}` | `{b}` | {c['overlap']:.1%} | "
                f"{len(c['valence_conflicts'])} | {c['chunk_agreement']:.2f} |"
            )

        return "\n".join(lines) + "\n"


def build_report(
    loaded: LoadedStimulus,
    fields: Sequence[PerceptualField],
    reliabilities: Mapping[str, ReliabilityVerdict],
) -> CalibrationReport:
    """Assemble the report, running every expert field against the novice baseline."""
    by_id = {f.persona_id: f for f in fields}

    lay = [p.id for p in FINANCE_PERSONAS if not p.expert and p.id in by_id]
    if not lay:
        raise ValueError(
            "no lay persona present to serve as the novice baseline; the expertise "
            "check is a comparison and needs something to compare against"
        )
    baseline_id = lay[0]
    baseline = by_id[baseline_id]

    checks: dict[str, SignatureCheck] = {}
    for persona_id, field in by_id.items():
        if persona_id == baseline_id:
            continue
        if not persona_by_id(persona_id).expert:
            continue
        checks[persona_id] = check_expertise_signature(
            expert=field.salience(),
            novice=baseline.salience(),
            relevant=loaded.relevance[persona_id],
        )

    diagnoses = {
        persona_id: diagnose_reliability(
            alpha=reliabilities[persona_id].alpha,
            concentration=field.concentration(),
        )
        for persona_id, field in by_id.items()
        if persona_id in reliabilities
    }

    return CalibrationReport(
        stimulus_id=loaded.stimulus.id,
        stimulus_title=loaded.stimulus.title,
        field_set=StimulusFieldSet(stimulus=loaded.stimulus, fields=list(fields)),
        reliabilities=dict(reliabilities),
        diagnoses=diagnoses,
        signature_checks=checks,
        baseline_persona=baseline_id,
    )


def run_calibration(
    client: ScoringClient,
    loaded: LoadedStimulus,
    k: int = 5,
) -> CalibrationReport:
    """Score every persona k times over one stimulus and report the result."""
    fields: list[PerceptualField] = []
    reliabilities: dict[str, ReliabilityVerdict] = {}

    for persona in FINANCE_PERSONAS:
        run = score_persona(client, persona, loaded.stimulus, k=k)
        fields.append(run.field)
        reliabilities[persona.id] = run.reliability

    return build_report(loaded, fields, reliabilities)
