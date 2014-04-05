from backdrop.webapp import app


def main():
    app.debug = True
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    main()
