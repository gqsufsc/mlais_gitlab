import servidor.server as server

def main():
    # Running server
    server.flaskApp.secret_key = 'super secret key'
    server.flaskApp.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    server.flaskApp.config['SESSION_TYPE'] = 'filesystem'
    server.flaskApp.run(host='0.0.0.0')

if __name__ == '__main__':
    main()


