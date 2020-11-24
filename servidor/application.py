import server

def main():
    # Running server
    server.flaskApp.secret_key = 'super secret key'
    server.flaskApp.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB
    server.flaskApp.config['SESSION_TYPE'] = 'filesystem'
    server.flaskApp.run(host='0.0.0.0', port='5000')

if __name__ == '__main__':
    main()


