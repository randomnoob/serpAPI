# NOTE:
# Đầu tiên chạy python db_init.py để tạo database
# Sau đó chạy flask run --reload để chạy app chính
# Mở một screen khác chạy python constant_updater.py để check domain mới và get kết quả mỗi phút 2 lần,
# kết quả SERP sẽ được get lại mỗi 24h một lần
# TODO:
# - Cấu hình flask app và constant_updater thành service
# - Log các thứ lại để phát hiện lỗi


from flask import Flask, request, jsonify, render_template, Response
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from models import db, SerpData
from utils import format_datetime_vietnamese
from constant_updater import db_work as force_update_serp, session_scope, delete_some
import csv, io, json


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

    db.init_app(app)

    @app.route('/')
    def index():
        return 'Hello, World!'
    
    @app.route('/send-queue')
    def send_queue():
        return render_template('send_queue.html')
    
    @app.route('/delete-some')
    def delete_page():
        return render_template('delete.html')
    @app.route('/delete-api-call', methods=['POST'])
    def delete_api_call():
        data = request.get_json()
        urls_to_delete = data['urllist'].splitlines()
        try:
            with session_scope() as session:
                delete_some(session, urls_to_delete=urls_to_delete)
                return jsonify({'status': 'success', 'message': f'{len(urls_to_delete)} urls đã được xóa'}), 201
        except Exception as e:
            return jsonify({'status': 'error', 'message': e}), 201

        
    @app.route('/force-update-all', methods=['PUT'])
    def force_update_all():
        with session_scope() as session:
            force_update_serp(session, force_all=True)
            return ''


    @app.route('/force-update-some', methods=['POST'])
    def force_update_some():
        data = request.get_json()
        urls_to_update = data['urllist'].splitlines()
        with session_scope() as session:
            force_update_serp(session, urls_to_update=urls_to_update)
            return ''

    @app.route('/queue', methods=['POST'])
    def queue():
        data = request.get_json()
        urls = data['urllist'].splitlines()
        urls = [x.strip() for x in urls if x]

        urls_added_to_db = []
        for url in urls:
            serp_in_db = SerpData.query.filter_by(url=url).first()
            if not serp_in_db:
                new_entry = SerpData(url=url, serp_page='', time=None)
                db.session.add(new_entry)
                urls_added_to_db.append(url)
            
            db.session.commit()
        
        return jsonify({'status': 'success', 'message': f'{len(urls_added_to_db)} urls đã được thêm vào hệ thống'}), 201
    

    @app.route('/check', methods=['POST'])
    def check():
        data = request.get_json()
        url = data['url']
        if not url:
            return jsonify({'status': 'error', 'message': 'url parameter is required'}), 200
        
        serp_data = SerpData.query.filter_by(url=url).first()
        if not serp_data:
            return jsonify({'status': 'error', 'message': 'url not found'}), 200
        
        if serp_data.serp_page:
            the_time = serp_data.time
            vietnamese_datetime_str = format_datetime_vietnamese(the_time)
            return jsonify({'status': 'success', 'serp_page': serp_data.serp_page, 'time': vietnamese_datetime_str, 'top1match': serp_data.top1_match}), 200
        else:
            return jsonify({'status': 'success', 'serp_page': 'No SERP'}), 200



    @app.route('/getcsv')
    def get_csv():
        serp_data = SerpData.query.all()
        # Create an in-memory buffer to store the CSV data
        output = io.StringIO()
        writer = csv.writer(output)
        # Write the header
        writer.writerow(['id', 'url', 'top1_url', 'time', 'top1_match'])
        # Write the data
        for data in serp_data:
            try:
                serp_page = json.loads(data.serp_page)
                top1_url = serp_page['organic'][0]['link']
            except IndexError:
                top1_url = "SERP 0 kết quả"
            except Exception as e:
                top1_url = e
            writer.writerow([data.id, data.url, top1_url, data.time, data.top1_match])

        # Seek to the start of the stream
        output.seek(0)

        # Create a response with the CSV data
        return Response(output, mimetype='text/csv')




    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

    