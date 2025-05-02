# Cool Notes App

To run backend:

```bash
poetry run uvicorn app.main:app --reload
```

To run frontend:

```bash
poetry run streamlit run frontend/app.py
```

Check coverage:

```bash
poetry run pytest --cov=app --cov-report=term-missing
```