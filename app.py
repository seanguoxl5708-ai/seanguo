import os
from flask import Flask, render_template, request, redirect, url_for, flash

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

    @app.route('/')
    def home():
        return render_template('home.html', title='首页')

    @app.route('/about')
    def about():
        return render_template('about.html', title='关于我们')

    @app.route('/services')
    def services():
        return render_template('services.html', title='服务')

    @app.route('/products')
    def products():
        return render_template('products.html', title='产品')

    @app.route('/careers')
    def careers():
        return render_template('careers.html', title='加入我们')

    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            message = request.form.get('message')
            print(f"[CONTACT] name={name} email={email} message={message}")
            flash('已收到您的留言，我们会尽快联系您。', 'success')
            return redirect(url_for('contact'))
        return render_template('contact.html', title='联系')

    @app.route('/privacy')
    def privacy():
        return render_template('privacy.html', title='隐私政策')

    @app.route('/terms')
    def terms():
        return render_template('terms.html', title='服务条款')

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html', title='页面未找到'), 404

    return app

# Module-level app for local development convenience
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)