import server

import turma_service as ts
import model_service as ms

def main():

    # ts.train('087aae')

    # ms.test()

    # Running server
    server.flaskApp.secret_key = 'super secret key'
    server.flaskApp.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    server.flaskApp.config['SESSION_TYPE'] = 'filesystem'
    server.flaskApp.run(host='0.0.0.0', port='5000')

if __name__ == '__main__':
    main()


