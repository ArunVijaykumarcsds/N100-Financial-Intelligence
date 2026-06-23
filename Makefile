load:
	python src/etl/loader.py

validate:
	python src/etl/validator.py

pipeline:
	python src/etl/run_pipeline.py

test:
	pytest tests/

clean:
	del /Q output\*

dashboard:
	streamlit run src/dashboard/app.py

api:
	uvicorn src.api.main:app --reload