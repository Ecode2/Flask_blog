from flasker import create_app
import waitress

app = create_app()

if __name__ == "__main__":
    #app.run(host="localhost", port=5500, debug=True)
    waitress.serve(app=app)