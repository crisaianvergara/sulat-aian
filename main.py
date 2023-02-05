from blogproject import app, db

# Run Flask
if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
