# RakkA.I(RAG) Project

## Overview
RakkA.I(RAG) is a FastAPI application designed to leverage Langchain functionalities for various AI-driven tasks. This project provides a structured approach to building and deploying AI applications with a focus on modularity and scalability.

## Project Structure
```
RakkA.I(RAG)
├── app
│   ├── main.py
│   ├── api
│   │   └── endpoints.py
│   ├── services
│   │   └── langchain_service.py
│   ├── models
│   │   └── __init__.py
│   └── utils
│       └── pdf_utils.py
├── .env
├── requirements.txt
└── README.md
```

## Installation
To get started with the RakkA.I(RAG) project, follow these steps:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd RakkA.I(RAG)
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
To run the application, execute the following command:
```
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` to access the interactive API documentation.

## Environment Variables
Create a `.env` file in the root directory and define your environment variables, such as API keys and configuration settings.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.