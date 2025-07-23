from app import create_app

app= create_app()

@app.route('/')
def hello():
    return "Hello from Flask in production!"

if __name__ == "__main__":
    app.run(debug=True)
    
