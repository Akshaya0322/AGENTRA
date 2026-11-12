import sys, pathlib
root = pathlib.Path(r'C:/Users/ADMIN/.gemini/antigravity/scratch/AGENTRA')
sys.path.append(str(root))
from agents.orchestrator import WorkflowOrchestrator
state = {
    'session_id':'test',
    'uploaded_files':[],
    'new_files':[],
    'action':'none',
    'last_query':'',
    'chat_history':[],
    'summary':''
}
orc = WorkflowOrchestrator('test')
new_state = orc.run(state)
print('run ok, keys:', list(new_state.keys()))
