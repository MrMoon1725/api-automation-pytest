# API Test Automation — Pytest + Requests + Pydantic

[![API Automation Tests](https://github.com/MrMoon1725/api-automation-pytest/actions/workflows/api-tests.yml/badge.svg)](https://github.com/MrMoon1725/api-automation-pytest/actions/workflows/api-tests.yml)

Automated REST API test suite built with **Python**, **Pytest**, **Requests**, and **Pydantic** contract validation. Covers authentication, full CRUD lifecycle, HTTP status codes, response time SLA assertions (`< 500ms`), and negative testing.

---

## Running Locally

```bash
git clone https://github.com/MrMoon1725/api-automation-pytest.git && cd api-automation-pytest
python -m venv .venv
pip install -r requirements.txt
pytest -v --html=reports/api-report.html --self-contained-html
```
