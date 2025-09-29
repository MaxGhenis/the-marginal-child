.PHONY: install run clean

# Install dependencies
install:
	pip install -r requirements.txt

# Run Streamlit app
run:
	streamlit run app.py

# Clean up
clean:
	rm -rf __pycache__ .streamlit/