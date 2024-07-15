from flask import Flask, request, jsonify
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from models import db, SerpData

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

    db.init_app(app)

    @app.route('/')
    def index():
        return 'Hello, Flask!'

    @app.route('/queue', methods=['POST'])
    def queue():
        data = request.get_json()
        domains = data['domainlist'].splitlines()
        print(domains)

        for domain in domains:
            new_entry = SerpData(domain=domain, serp_page='', time=None)
            db.session.add(new_entry)
        
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': f'{len(domains)} domains queued'}), 201
    

    @app.route('/check', methods=['GET'])
    def check():
        domain = request.args.get('domain')
        if not domain:
            return jsonify({'status': 'error', 'message': 'Domain parameter is required'}), 400
        
        serp_data = SerpData.query.filter_by(domain=domain).first()
        if not serp_data:
            return jsonify({'status': 'error', 'message': 'Domain not found'}), 404
        
        if serp_data.serp_page:
            return jsonify({'status': 'success', 'serp_page': serp_data.serp_page}), 200
        else:
            return jsonify({'status': 'success', 'serp_page': 'No SERP'}), 200


    return app



if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)