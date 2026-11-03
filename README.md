# Krishivaas Onboarding API Automation

## Setup (Windows PowerShell)

```powershell
cd C:\Users\ram\Downloads\api-automation
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

Add a fresh staging `API_TOKEN`, a valid `MAPINDIA_TOKEN`, and a unique approved `TEST_MOBILE_NUMBER`. Do not commit `.env`.

## Run

```powershell
.\.venv\Scripts\python.exe -m pytest --collect-only -v
.\.venv\Scripts\python.exe -m pytest tests/test_auth.py -v
.\.venv\Scripts\python.exe -m pytest tests/farmer -v -s
.\.venv\Scripts\python.exe -m pytest tests/farm -v -s
.\.venv\Scripts\python.exe -m pytest tests/crop -v -s
.\.venv\Scripts\python.exe -m pytest tests/boundary -v -s
.\.venv\Scripts\python.exe -m pytest tests/workflows -v -s
```

## Allure

```powershell
.\.venv\Scripts\python.exe -m pytest tests -v --alluredir=allure-results
allure serve allure-results
```

## Important implementation notes

- Use only an approved staging tenant and test records. Add tests create records; update tests mutate records.
- Requests automatically creates the multipart `Content-Type` boundary when `data`/`files` are used. Do not copy browser-generated multipart boundary headers.
- The bearer token is taken from `.env`. The API also included a `token` form field in the supplied cURLs, so the service payloads preserve that field where shown.
- Farmer/farm/crop response bodies and status codes were not included in the prompt. Tests currently accept HTTP 200 or 201; align this with the actual API contract.
- The JSON schemas are placeholders, not verified contracts. Replace them after capturing successful and error response examples.
- `farm_id` and `cfa_id` semantics for boundary create/update must be confirmed. Your boundary cURL supplies `farm_id` and `cfa_id`; this scaffold retains both.
- The provided cURLs do not include an add-boundary-specific request, crop cancel endpoint, or complete edit-crop response contract. Add-boundary currently uses the same endpoint as update, per your note. Cancel crop is skipped rather than guessing an endpoint.
- `flu_id` appears to identify a farm in the supplied requests, while `fmr_id` appears to identify a farmer; verify these names with the API contract.

------------------------------------------------------------------------

# Allure setup

Install adapter:
```powershell
.\.venv\Scripts\python.exe -m pip install allure-pytest
```

Install Allure CLI (Node.js/npm required):
```powershell
npm install -g allure-commandline
allure --version
```

Run one test:
```powershell
.\.venv\Scripts\python.exe -m pytest tests/farmer/test_add_farmer.py -v -s --alluredir=allure-results --clean-alluredir
allure serve allure-results
```

Run all tests:
```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -v -s --alluredir=allure-results --clean-alluredir
allure serve allure-results
```

Generate a persistent report:
```powershell
allure generate allure-results --clean -o allure-report
allure open allure-report
```

Important:
- Standalone tests follow the method signatures in the supplied examples:
  `FarmService.update_farm(fields)` and `CropService.update_crop(crop_allocation_id, fields)`.
  Check your service files and align calls if signatures differ.
- Confirm actual response ID fields. Workflow expects `fmr_id`, `flu_id`/`farm_id`, and one crop allocation ID field.
- Confirm whether the boundary endpoint supports creation and whether `cfa_id` is required.
- Review response attachments for personal or confidential data before using reports outside your machine.
- Never commit `.env`, tokens, or cookies.
