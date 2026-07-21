from src.planner.engine import PlanGenerator
from src.planner.simulator import PlannerSimulator
from src.telemetry.instrumentation import RuntimeInstrumenter, CorrelationContext
from src.events.bus import EventType
from src.replay.engine import global_trace_store, global_replay_engine
from src.evaluation.engine import EvaluationEngine

def run_nicmar_os_demo():
    print("=== NICMAR OS INTEGRATED TEST START ===")
    
    # 1. Definim un task real pentru NicMar
    prompt = "Analizeaza istoricul si cauta informatii despre produs pentru partenera mea"
    user_role = "admin"
    
    # 2. Generare Plan & Simulare
    plan = PlanGenerator.generate_plan(prompt, user_role)
    simulation_report = PlannerSimulator.simulate(plan)
    print(simulation_report)
    
    # 3. Instrumentare si Emitere Evenimente
    correlation = CorrelationContext()
    RuntimeInstrumenter.emit(EventType.PLAN_CREATED, correlation, {"prompt": prompt})
    
    for node in plan.nodes:
        correlation.node_id = node.node_id
        RuntimeInstrumenter.emit(EventType.NODE_STARTED, correlation, {"node": node.description})
        RuntimeInstrumenter.emit(EventType.NODE_FINISHED, correlation, {"node": node.node_id})
        
    RuntimeInstrumenter.emit(EventType.WORKFLOW_FINISHED, correlation, {"status": "success"})
    
    # 4. Replay pe baza Request ID-ului generat
    request_id = correlation.request_id
    print(f"\n[Replay Verification] Fetching trace for Request ID: {request_id}")
    replay_report = global_replay_engine.replay_trace(request_id)
    print(replay_report)
    
    # 5. Evaluare Automata a Rezultatului
    output_sample = "Am analizat istoricul si am gasit informatiile cerute despre produsul din portofoliul NicMar."
    eval_report = EvaluationEngine.evaluate_response(prompt, output_sample)
    print(f"\n[Evaluation Report] Overall Score: {eval_report.overall_score:.2f}")
    for m in eval_report.metrics:
        print(f"  - {m.metric_name}: score={m.score} ({m.reasoning})")
        
    print("=== NICMAR OS INTEGRATED TEST COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_nicmar_os_demo()
