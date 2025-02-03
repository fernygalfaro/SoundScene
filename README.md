# SoundScene

SoundScene is a streaming platform where users can enjoy movies, discover new music, and share their favorite content with their community.

## Features
- Access the latest movies and music, as well as timeless classics.
- A unique **"Don't Personalize"** feature that prevents content recommendations from being influenced by niche searches.
- User accounts to save preferences and favorite content.
- Secure data storage with **AEAD AES-256-CBC** encryption to protect user information.

## Getting Started

### Prerequisites
Make sure you have the following installed:
- **Python 3.x** – Check with `python --version` or `python3 --version`
- **pip** – Python package manager

### Installation
1. Clone the repository to your preferred directory:
   ```sh
   git clone https://github.com/yourusername/soundscene.git
   cd soundscene
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

### Running the Application
1. Navigate to the project folder in the terminal:
   ```sh
   cd soundscene
   ```
2. Set up environment variables (for Windows):
   ```sh
   set FLASK_APP=run.py
   set FLASK_ENV=development
   ```
   (For macOS/Linux, use `export` instead of `set`.)
3. Start the application:
   ```sh
   flask run
   ```
4. The application should now be running at: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## Technologies Used
- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **Database**: MongoDB

## Author
**Fernando Alfaro** – Original work

---
Feel free to contribute to this project by submitting issues or pull requests!

