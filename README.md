# 🖼️ Image Gallery

Image Gallery is a full-stack web application for managing and showcasing images, enhanced with AI-powered image generation tools. You can effortlessly upload, organize, and view your images, or create new ones using AI. It's built for developers, with a simple, extensible design.

---

## ✨ Key Features

### Core
- **Easy to Use:** Simple installation and maintenance with a responsive, accessible interface.  
- **Flexible Descriptions:** Supports plain text, Markdown, or raw markup for detailed image descriptions.  
- **User Management:** Comprehensive rights model for managing users and visitors.  
- **Fast UI:** A highly interactive and performant frontend built with React/Next.js.  

### Backend
- **RESTful API:** A robust API built with FastAPI.  
- **Comprehensive Management:** Handles all image-related tasks, including upload, storage, retrieval, and metadata.  
- **Database Support:** Works with MySQL, SQLite, and PostgreSQL.  
- **Secure:** Features secure authentication and user management.  

### AI Tools (`ai-tools/`)
- **Docker Integration:** Uses Docker Compose for a self-contained AI image generation service.  
- **Effortless Generation:** Generates new images to expand your gallery.  
- **Seamless Workflow:** Easily integrates with both frontend and backend operations.  

---

## 🛠️ Requirements

### Frontend
- Node.js, npm  

### Backend
- Python 3.10+  
- FastAPI and other required Python packages  

### AI Tools
- Docker, Docker Compose  
- **Replicate API token** (keep this secret and do not commit)  

### Database
- MySQL 5.7+, SQLite 3+, or PostgreSQL 10+  

---

## 🚀 Installation

Follow these steps to set up and run the entire application locally.

### 1. Frontend Setup
Navigate to the frontend directory to set up the client-side application.

```bash
cd frontend
npm install
npm run dev
The frontend will be available at:
http://localhost:3000

2. Backend Setup
Set up the backend API, which powers the image and user management.

bash
Copy code
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Linux/macOS
pip install -r requirements.txt
uvicorn main:app --reload
The backend API will run at:
http://localhost:8000

3. AI Tools Setup
Configure the AI-powered image generation service to expand your gallery.

bash
Copy code
cd ai-tools
i. Create a .env File
Create a .env file and populate it with environment variables. Do not commit real tokens.

env
Copy code
# Backend Base URL (frontend uses this to talk to backend)
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Redis connection (used by worker + backend)
REDIS_URL=redis://localhost:6379/0

# Database connection (default is SQLite for local dev)
DATABASE_URL=sqlite:///./backend/app.db

# Replicate API token (required for image generation)
REPLICATE_API_TOKEN=<YOUR_API_TOKEN_HERE>
Replace <YOUR_API_TOKEN_HERE> with your actual Replicate API token. Never commit it to GitHub.

ii. Run Everything with Docker
From inside the project directory, build the Docker images and start all services:

bash
Copy code
npm run dev:all
This command will start the frontend, backend, worker, Redis, and database services.

iii. Open the App
Once running, access the application locally:

Frontend (Next.js): http://localhost:3000

Backend (FastAPI): http://localhost:8000/docs

Redis: running on localhost:6379

4. Environment Variables
Create a .env file in the backend folder for secrets and configurations:

env
Copy code
# Example for backend
DATABASE_URL=<YOUR_DATABASE_URL>
REPLICATE_API_TOKEN=<YOUR_API_TOKEN_HERE>
Never commit secrets or API tokens to GitHub.

🙏 Contribution
We welcome contributions! Feel free to fork this repository and create pull requests. Ensure you do not include secrets when committing.

📝 License
This project is licensed under the MIT License.

🧑‍💻 Authors
(To be filled later)