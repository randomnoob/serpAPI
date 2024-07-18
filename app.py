# NOTE:
# Đầu tiên chạy python db_init.py để tạo database
# Sau đó chạy flask run --reload để chạy app chính
# Mở một screen khác chạy python constant_updater.py để check domain mới và get kết quả mỗi phút 2 lần,
# kết quả SERP sẽ được get lại mỗi 24h một lần
# TODO:
# - Cấu hình flask app và constant_updater thành service
# - Log các thứ lại để phát hiện lỗi


from flask import Flask, request, jsonify
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from models import db, SerpData
from utils import format_datetime_vietnamese


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
        urls = data['urllist'].splitlines()
        urls = [x.strip() for x in urls]
        print(urls)

        urls_added_to_db = []
        for url in urls:
            serp_in_db = SerpData.query.filter_by(url=url).first()
            if not serp_in_db:
                new_entry = SerpData(url=url, serp_page='', time=None)
                db.session.add(new_entry)
                urls_added_to_db.append(url)
            
            db.session.commit()
        
        return jsonify({'status': 'success', 'message': f'{len(urls_added_to_db)} urls queued'}), 201
    

    @app.route('/check', methods=['POST'])
    def check():
        data = request.get_json()
        url = data['url']
        if not url:
            return jsonify({'status': 'error', 'message': 'url parameter is required'}), 400
        
        serp_data = SerpData.query.filter_by(url=url).first()
        if not serp_data:
            return jsonify({'status': 'error', 'message': 'url not found'}), 404
        
        if serp_data.serp_page:
            the_time = serp_data.time
            vietnamese_datetime_str = format_datetime_vietnamese(the_time)
            return jsonify({'status': 'success', 'serp_page': serp_data.serp_page, 'time': vietnamese_datetime_str}), 200
        else:
            return jsonify({'status': 'success', 'serp_page': 'No SERP'}), 200



    return app



if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

    