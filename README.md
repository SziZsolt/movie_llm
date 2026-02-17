# Movie LLM API

A FastAPI-based application that combines structured movie data with a large language model (LLM) to answer natural language queries, provide movie recommendations, and retrieve movie information.  

---

## Setup

1. Clone the repository and navigate to the project folder:
```
git clone <repository_url>
cd movie_llm
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Load the database from CSV files:
```python
from MovieDatabase import MovieDatabase

db = MovieDatabase()
db.load_data("path_to_csv_files")  # Include movies.csv, ratings.csv, tags.csv
```

4. Create Retrieval layer
```python
from Retrieval import Retrieval

retrieval = Retrieval(movie_database)
```

5. Create Model layer and give your input
```python
from MovieModel import MovieModel

movie_model = MovieModel(retrieval, "meta-llama/Llama-2-7b-hf")
generated_answer = movie_model.generate_answer("Can you suggest movies similar to Inception?")
```

6. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

- The API will be available at: [http://127.0.0.1:8000](http://127.0.0.1:8000)  
---

## 💻 API Usage

### POST /chat

- **Request Body** (JSON):
```json
{
  "query": "Recommend movies from 2020"
}
```

- **Sample Response**:
```json
{
  "response": "Here are some movies from 2020: Tenet (2020), Soul (2020), The Invisible Man (2020)..."
}
```
---

## 🛠 Approach

The system **combines structured data with LLM capabilities**:

1. **Structured Data**:  
   - SQLite database (movies.db) contains movies, ratings, and tags.  
   - MovieDatabase provides query methods: similar movies, year-based recommendations, top-rated movies, etc.

2. **LLM**:  
   - MovieModel uses LLaMA to generate natural language answers.  
   - Input to the LLM includes the user query + relevant database context retrieved by the system.

3. **Retrieval Layer** (Retrieval.py):  
   - Determines the intent of the user query (GENERAL, SIMILAR_MOVIES, RECOMMEND_BY_YEAR).  
   - Fetches relevant structured data from the database.  
   - Provides this data as context to the LLM for answer generation.


## Example Workflow

1. User asks: "Can you suggest movies similar to Inception?"
2. Retrieval identifies the intent (SIMILAR_MOVIES) and fetches relevant movies from the database.  
3. LLM generates a natural language response using the retrieved data.  