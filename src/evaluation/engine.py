from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class EvaluationMetric:
    metric_name: str
    score: float # între 0.0 și 1.0
    reasoning: str

@dataclass
class EvaluationReport:
    task_prompt: str
    actual_output: str
    expected_output: Optional[str] = None
    metrics: List[EvaluationMetric] = field(default_factory=list)
    overall_score: float = 0.0

class EvaluationEngine:
    @staticmethod
    def evaluate_response(prompt: str, output: str, expected: Optional[str] = None) -> EvaluationReport:
        """
        Evaluează calitatea răspunsului generat folosind euristici inteligente 
        și pregătind terenul pentru LLM Judge.
        """
        metrics = []
        
        # 1. Metrică de lungime / substanță (evită răspunsurile goale sau prea scurte)
        words_count = len(output.split())
        substance_score = min(1.0, words_count / 20.0) if words_count > 5 else 0.2
        metrics.append(EvaluationMetric(
            metric_name="substance_and_length",
            score=substance_score,
            reasoning=f"Response contains {words_count} words."
        ))

        # 2. Metrică de relevanță simplificată față de prompt
        prompt_keywords = set(prompt.lower().split())
        output_lower = output.lower()
        matched_keywords = sum(1 for kw in prompt_keywords if kw in output_lower)
        relevance_score = min(1.0, matched_keywords / max(1, len(prompt_keywords) * 0.3))
        metrics.append(EvaluationMetric(
            metric_name="prompt_relevance",
            score=relevance_score,
            reasoning=f"Matched {matched_keywords} keywords from prompt."
        ))

        # 3. Scor general mediu
        overall = sum(m.score for m in metrics) / max(1, len(metrics))

        return EvaluationReport(
            task_prompt=prompt,
            actual_output=output,
            expected_output=expected,
            metrics=metrics,
            overall_score=overall
        )
