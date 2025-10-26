from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title='DuckLearn', version='1.0')


# ----------------------------------------------------------
# 🧠 Common API routes (active in all modes)
# ----------------------------------------------------------
@app.get('/api/hello')
def read_root() -> Dict[str, str]:
    """Return a simple hello message for API health checks."""
    return {'message': 'Hello from Tomosius FastAPI!'}


# ----------------------------------------------------------
# 💻 DEVELOPMENT MODE (currently active)
# ----------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

print('⚙️  Running in DEVELOPMENT mode (no static files mounted).')
