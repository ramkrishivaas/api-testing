import pytest
from clients.api_client import APIClient
import subprocess
from pathlib import Path

@pytest.fixture(scope="function")
def api_client():
    client = APIClient()

    yield client

    client.close()

def pytest_sessionfinish(session, exitstatus):
    project_root = Path(str(session.config.rootpath))

    results_dir = project_root / "allure-results"
    report_dir = project_root / "allure-report"

    # Exact Allure executable path confirmed from your terminal
    allure_executable = Path(
        r"C:\Users\ram\allure-2.33.0\bin\allure.bat"
    )

    if not allure_executable.exists():
        print("ERROR: Allure executable not found:", allure_executable)
        return

    if not results_dir.exists() or not any(results_dir.iterdir()):
        print("ERROR: No Allure result files found.")
        return

    print("\nGenerating Allure HTML report...")

    try:
        result = subprocess.run(
            [
                "cmd.exe",
                "/c",
                str(allure_executable),
                "generate",
                str(results_dir),
                "--clean",
                "-o",
                str(report_dir)
            ],
            cwd=str(project_root),
            check=False
        )

        if result.returncode != 0:
            print("ERROR: Allure report generation failed.")
            return

        print("Allure HTML report generated successfully!")

        # Start Allure report server and open browser
        subprocess.Popen(
            [
                "cmd.exe",
                "/c",
                str(allure_executable),
                "open",
                str(report_dir)
            ],
            cwd=str(project_root)
        )

        print("Opening Allure report in browser...")

    except Exception as error:
        print(f"Allure execution error: {error}")
