import os
import io
from flask import Flask, render_template, request, redirect, url_for, make_response, flash
import i18n

# app.py 顶部（import 后）
ACHIEVEMENTS = [
    {
        "id": "clients",
        "title_key": "home.achievement_cards.clients.title",
        "description_key": "home.achievement_cards.clients.description"
    },
    {
        "id": "aum",
        "title_key": "home.achievement_cards.aum.title",
        "description_key": "home.achievement_cards.aum.description"
    },
    {
        "id": "years",
        "title_key": "home.achievement_cards.years.title",
        "description_key": "home.achievement_cards.years.description"
    }
]

# 建议：放在文件顶部（import 之后）
PEOPLE = [
    {
        "slug": "alice-zhang",                  # 用于URL：/people/alice-zhang
        "name": {                            # 列表页的一句话简介（可选）
            "en": "Wang Yuqi",
            "zh-CN": "王宇琪",
            "zh-TW": "王宇琪"
        },
        "title": {                            # 列表页的一句话简介（可选）
            "en": "Chief Executive Officer",
            "zh-CN": "首席执行官",
            "zh-TW": "首席執行長"
        },
        "photo": "img/people/wyq.jpeg",        # 相对 static/ 路径
        "summary": {                            # 列表页的一句话简介（可选）
            "en": "Chief Executive Officer",
            "zh-CN": "首席执行官",
            "zh-TW": "首席執行長"
        },
        "bio": {                                # 详情页正文简介（可选）
            "en": """Mr. Wang Yuqi has over 20 years of experience in wealth management. Before founding Quantum Cornerstone, he served as a Board Advisor and Senior Partner at HuaRui, where he was responsible for the firm’s Hong Kong operations. With more than two decades in the banking industry, he brings extensive knowledge and expertise to this role. Mr. Wang has a solid background in finance and trust services, making him a trusted advisor.\n
Mr. Wang began his career at Goldman Sachs in 2002, where his passion and dedication quickly led to his advancement. He has held leadership positions at Avanta Assets Investment Management Ltd., China International Capital Corporation (CICC), Barclays Wealth Management/Bank of Singapore, and Credit Suisse. He successfully led teams managing multi-billion-dollar assets, demonstrating his ability to deliver outstanding results.\n
Mr. Wang holds a Bachelor’s degree in Engineering from Tsinghua University, an MBA from the University of Chicago, and is a Chartered Financial Analyst (CFA).""",

            "zh-CN": """王宇琪先生在财富管理方面拥有超过20年的经验。创立量子基石之前，他曾担任华瑞的董事顾问和高级合伙人，并负责香港分公司的业务。凭借超过20年的银行业经验，他为该职位带来了广泛的知识和专业技能。王先生在金融和信托事务方面有着扎实的背景，使他成为一名值得信赖的顾问。\n
王先生于2002年在高盛开始了他的职业生涯，并凭借他的工作热情和奉献精神迅速晋升。他曾在Avanta Assets Investment Management Ltd.、中国国际金融股份有限公司、巴克莱财富管理/新加坡银行和瑞士信贷担任领导职务，成功领导了管理数十亿美元资产的团队，展示了他提供卓越成果的能力。\n
王宇琪先生拥有清华大学的工程学学士学位、芝加哥大学的工商管理硕士学位以及特许金融分析师（CFA）资格。""",

            "zh-TW": """王宇琪先生在財富管理方面擁有超過20年的經驗。 創立量子基石前, 他曾擔任華瑞的董事顧問和高級合夥人, 並負責香港分公司的業務。憑藉超過20年的銀行業經驗，他為該職位帶來了廣泛的知識和專業技能。王先生在金融和信託事務方面有著扎實的背景，使他成為一名值得信賴的顧問。\n
王先生於2002年在高盛開始了他的職業生涯，並憑藉他的工作熱情和奉獻精神迅速晉升。他曾在Avanta Assets Investment Management Ltd.、中國國際金融股份有限公司、巴克萊財富管理/新加坡銀行和瑞士信貸擔任領導職務，成功領導了管理數十億美元資產的團隊，展示了他提供卓越結果的能力。\n
王宇琪先生擁有清華大學的工程學學士學位、芝加哥大學的工商管理碩士學位以及特許金融分析師（CFA）資格。"""
        }
    },
    # {
    #     "slug": "bob-lee",
    #     "name": "Bob Lee",
    #     "title": "Engineering Lead",
    #     "photo": "img/people/bob.jpeg",
    #     "summary": {
    #         "en": "Engineering & platform",
    #         "zh-CN": "工程与平台",
    #         "zh-TW": "工程與平台"
    #     },
    #     "bio": {
    #         "en": "Bob builds reliable systems and teams...",
    #         "zh-CN": "负责工程与平台可靠性……",
    #         "zh-TW": "負責工程與平台可靠性……"
    #     }
    # },
    # …继续按这个格式添加更多成员
]

def _latest_news(limit=3):
    """可选：读取 content/news 下的 Markdown 文章，取最近 N 篇。
       若未安装 frontmatter/markdown 或无目录，返回空列表。"""
    try:
        import os, glob, datetime
        import frontmatter
        NEWS_DIR = os.path.join(os.path.dirname(__file__), "content", "news")
        
        # 确保目录存在
        if not os.path.exists(NEWS_DIR):
            print(f"[DEBUG] News directory not found: {NEWS_DIR}")
            return []
        
        posts = []
        md_files = glob.glob(os.path.join(NEWS_DIR, "*.md"))
        print(f"[DEBUG] Found {len(md_files)} markdown files in {NEWS_DIR}")
        
        for path in md_files:
            try:
                with open(path, 'r', encoding='utf-8') as fh:
                    content = fh.read()
                    if hasattr(frontmatter, 'load'):
                        post = frontmatter.load(io.StringIO(content))
                    elif hasattr(frontmatter, 'Frontmatter'):
                        raw = frontmatter.Frontmatter.read(content)
                        post = raw.get('attributes', {})
                        post['content'] = raw.get('body', '')
                    else:
                        raise ImportError('Unsupported frontmatter package')
                slug = os.path.splitext(os.path.basename(path))[0]
                date = post.get("date")
                try:
                    date = datetime.date.fromisoformat(str(date)) if date else None
                except Exception as e:
                    print(f"[DEBUG] Date parsing error for {slug}: {e}")
                    date = None
                posts.append({
                    "slug": slug,
                    "title": post.get("title", slug),
                    "summary": post.get("summary", ""),
                    "date": date
                })
                print(f"[DEBUG] Loaded post: {slug}")
            except Exception as e:
                print(f"[DEBUG] Error loading {path}: {e}")
                continue
        
        posts.sort(key=lambda p: p["date"] or datetime.date.min, reverse=True)
        print(f"[DEBUG] Returning {len(posts)} posts, limited to {limit}")
        return posts[:limit]
    except Exception as e:
        print(f"[DEBUG] Error in _latest_news: {e}")
        import traceback
        traceback.print_exc()
        return []


def _render_markdown(text):
    try:
        import markdown
        return markdown.markdown(text, extensions=['extra', 'sane_lists', 'smarty'])
    except Exception as e:
        print(f"[DEBUG] Markdown render failed: {e}")
        return text


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

    @app.before_request
    def _set_lang():
        lang = request.cookies.get("lang") or i18n.get_lang_from_request()
        i18n.set_current_lang(lang)

    @app.context_processor
    def _inject_t():
        return {"t": i18n.t, "current_lang": i18n.get_current_lang()}

    @app.route('/set-lang/<lang>')
    def set_lang(lang):
        nxt = request.args.get('next') or request.referrer or url_for('home')
        if lang not in i18n.SUPPORTED:
            lang = i18n.DEFAULT
        resp = make_response(redirect(nxt))
        resp.set_cookie('lang', lang, max_age=60*60*24*365, httponly=False, samesite="Lax")
        return resp

    @app.route('/')
    def home():
        latest_posts = _latest_news(limit=3)
        return render_template('home.html', title='Home', latest_posts=latest_posts, achievements=ACHIEVEMENTS)

    @app.route('/about')
    def about():
        # i18n 衔接：你之前已集成多语言，会有 current_lang 注入模板
        return render_template('about.html', title='About', people=PEOPLE)

    @app.route('/people/<slug>')
    def person_detail(slug):
        person = next((p for p in PEOPLE if p["slug"] == slug), None)
        if not person:
            return render_template('404.html', title='Not found'), 404
        return render_template('person_detail.html', title=person["name"], person=person)

    @app.route('/services')
    def services():
        return render_template('services.html', title='Services')
    
    @app.route('/services/consulting')
    def services_consulting():
        return render_template('services_consulting.html', title='Consulting')

    @app.route('/services/implementation')
    def services_implementation():
        return render_template('services_implementation.html', title='Implementation')

    @app.route('/services/operations')
    def services_operations():
        return render_template('services_operations.html', title='Operations')


    @app.route('/insight')
    def insight():
        return render_template('insight.html', title='Insight')

    @app.route('/careers')
    def careers():
        return render_template('careers.html', title='Careers')

    @app.route('/contact', methods=['GET','POST'])
    def contact():
        if request.method == 'POST':
            flash('Thanks! This is a demo; no emails are sent.', 'success')
            return redirect(url_for('contact'))
        return render_template('contact.html', title='Contact')

    @app.route('/privacy')
    def privacy():
        return render_template('privacy.html', title='Privacy')

    @app.route('/news')
    def news():
        all_posts = _latest_news(limit=100)
        return render_template('news.html', title='News', posts=all_posts)

    @app.route('/news/<slug>')
    def news_detail(slug):
        all_posts = _latest_news(limit=100)
        post = next((p for p in all_posts if p["slug"] == slug), None)
        if not post:
            return render_template('404.html', title='Not found'), 404
        # 读取完整的markdown内容
        try:
            import os, frontmatter
            NEWS_DIR = os.path.join(os.path.dirname(__file__), "content", "news")
            path = os.path.join(NEWS_DIR, f"{slug}.md")
            with open(path, 'r', encoding='utf-8') as fh:
                text = fh.read()
                if hasattr(frontmatter, 'load'):
                    md_file = frontmatter.load(io.StringIO(text))
                    raw_content = md_file.content
                elif hasattr(frontmatter, 'Frontmatter'):
                    raw = frontmatter.Frontmatter.read(text)
                    raw_content = raw.get("body", "")
                else:
                    raise ImportError('Unsupported frontmatter package')
            post["content"] = _render_markdown(raw_content)
        except Exception as e:
            print(f"[DEBUG] Error loading post content: {e}")
            post["content"] = _render_markdown(post.get("summary", ""))
        return render_template('news_detail.html', title=post["title"], post=post)

    @app.route('/terms')
    def terms():
        return render_template('terms.html', title='Terms')

    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html', title='Not found'), 404

    return app

app = create_app()

def _get_ssl_context():
    """Return SSL context for development.

    If SSL_CERT_FILE and SSL_KEY_FILE are provided, use them.
    If USE_HTTPS is enabled, use Werkzeug adhoc self-signed certificate.
    """
    cert_file = os.environ.get("SSL_CERT_FILE")
    key_file = os.environ.get("SSL_KEY_FILE")
    if cert_file and key_file:
        return (cert_file, key_file)

    use_https = os.environ.get("USE_HTTPS", "").lower()
    if use_https in ("1", "true", "yes", "on"):
        return "adhoc"

    return None

if __name__ == "__main__":
    ssl_context = _get_ssl_context()
    if ssl_context:
        print("Running HTTPS development server on https://127.0.0.1:5000")
    else:
        print("Running HTTP development server on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True, ssl_context=ssl_context)