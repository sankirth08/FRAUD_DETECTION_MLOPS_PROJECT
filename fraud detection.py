
from pathlib import Path

root = Path(__file__).parent

folders = [
    "app",
    "backend/app/api/routes",
    "backend/app/config",
    "backend/app/schemas",
    "backend/app/services",
    "backend/app/database",
    "backend/app/ml",
    "backend/app/utils",
    "backend/tests",
    "ml/data",
    "ml/features",
    "ml/models",
    "ml/experiments",
    "data/raw",
    "data/processed",
    "data/reference",
    "models/production",
    "models/candidates",
    "mlops/monitoring/reports",
    "mlops/retraining",
    "notebooks",
    "tests/unit",
    "tests/integration",
    "scripts",
    "artifacts/metrics",
    "artifacts/plots",
    "artifacts/reports",
    "configs",
    ".github/workflows"
]

files = [
    "README.md",
    ".gitignore",
    ".env.example",
    "Dockerfile",
    "docker-compose.yml",
    "params.yaml",
    "dvc.yaml",
    "app/streamlit_app.py",
    "backend/requirements.txt",
    "backend/Dockerfile",
    "backend/app/__init__.py",
    "backend/app/main.py",
    "backend/app/config/settings.py",
    "backend/app/api/dependencies.py",
    "backend/app/api/routes/prediction.py",
    "backend/app/api/routes/transactions.py",
    "backend/app/api/routes/analytics.py",
    "backend/app/api/routes/monitoring.py",
    "backend/app/api/routes/model.py",
    "backend/app/schemas/prediction.py",
    "backend/app/schemas/transaction.py",
    "backend/app/services/prediction_service.py",
    "backend/app/services/transaction_service.py",
    "backend/app/services/monitoring_service.py",
    "backend/app/database/database.py",
    "backend/app/database/models.py",
    "backend/app/database/crud.py",
    "backend/app/ml/model_loader.py",
    "backend/app/ml/predictor.py",
    "backend/app/ml/preprocessor.py",
    "backend/app/utils/logger.py",
    "backend/app/utils/exceptions.py",
    "backend/tests/test_prediction.py",
    "backend/tests/test_api.py",
    "ml/data/ingestion.py",
    "ml/data/validation.py",
    "ml/data/preprocessing.py",
    "ml/features/feature_engineering.py",
    "ml/models/train.py",
    "ml/models/evaluate.py",
    "ml/models/tune.py",
    "ml/experiments/baseline.py",
    "ml/experiments/random_forest.py",
    "ml/experiments/xgboost.py",
    "mlops/monitoring/data_drift.py",
    "mlops/monitoring/prediction_drift.py",
    "mlops/monitoring/performance.py",
    "mlops/retraining/trigger.py",
    "mlops/retraining/retrain.py",
    "mlops/retraining/validation.py",
    "tests/unit/test_ml_pipeline.py",
    "tests/integration/test_integration.py",
    "scripts/train.py",
    "scripts/evaluate.py",
    "scripts/retrain.py",
    "configs/model.yaml",
    "configs/features.yaml",
    "configs/monitoring.yaml",
    ".github/workflows/ci.yml",
    ".github/workflows/training.yml"
]

for folder in folders:
    (root / folder).mkdir(parents=True, exist_ok=True)

for filename in files:
    path = root / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)

print("Fraud Detection MLOps project created successfully!")
print("Project location:", root)