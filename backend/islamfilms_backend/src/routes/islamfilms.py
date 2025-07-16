from flask import Blueprint, request, jsonify
import requests
import json
import re
from openai import OpenAI

islamfilms_bp = Blueprint('islamfilms', __name__)

# إعداد DeepSeek API (سيتم استخدام OpenAI SDK مع DeepSeek)
# يمكن للمستخدم إضافة مفتاح API الخاص به هنا
DEEPSEEK_API_KEY = "your-deepseek-api-key-here"  # يجب استبدال هذا بمفتاح API حقيقي
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# إعداد عميل OpenAI للعمل مع DeepSeek
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL
)

# قاعدة بيانات مؤقتة للأفلام (في التطبيق الحقيقي، يجب استخدام قاعدة بيانات حقيقية)
MOVIES_DATABASE = {
    "تايتانيك": {
        "id": "titanic_1997",
        "title": "تايتانيك",
        "year": "1997",
        "type": "فيلم",
        "genre": "رومانسي، دراما"
    },
    "الأسد الملك": {
        "id": "lion_king_1994",
        "title": "الأسد الملك",
        "year": "1994",
        "type": "فيلم رسوم متحركة",
        "genre": "عائلي، مغامرات"
    },
    "أفاتار": {
        "id": "avatar_2009",
        "title": "أفاتار",
        "year": "2009",
        "type": "فيلم",
        "genre": "خيال علمي، مغامرات"
    },
    "فروزن": {
        "id": "frozen_2013",
        "title": "فروزن",
        "year": "2013",
        "type": "فيلم رسوم متحركة",
        "genre": "عائلي، موسيقي"
    },
    "الرجل العنكبوت": {
        "id": "spiderman_2002",
        "title": "الرجل العنكبوت",
        "year": "2002",
        "type": "فيلم",
        "genre": "أكشن، مغامرات"
    }
}

def is_movie_query(query):
    """التحقق من أن الاستعلام يتعلق بفيلم أو مسلسل"""
    movie_keywords = [
        'فيلم', 'مسلسل', 'سينما', 'أفلام', 'مسلسلات', 'movie', 'film', 'series', 'tv show'
    ]
    
    # البحث عن كلمات مفتاحية في الاستعلام
    query_lower = query.lower()
    
    # إذا كان الاستعلام يحتوي على كلمات مفتاحية للأفلام
    for keyword in movie_keywords:
        if keyword in query_lower:
            return True
    
    # إذا كان الاستعلام يطابق أسماء أفلام معروفة
    for movie_name in MOVIES_DATABASE.keys():
        if movie_name in query or query in movie_name:
            return True
    
    return False

def search_movies(query):
    """البحث عن الأفلام في قاعدة البيانات"""
    results = []
    query_lower = query.lower()
    
    for movie_name, movie_data in MOVIES_DATABASE.items():
        if query_lower in movie_name.lower() or movie_name.lower() in query_lower:
            results.append(movie_data)
    
    return results

def get_movie_evaluation_prompt(movie_title, movie_year, movie_genre):
    """إنشاء prompt لتقييم الفيلم"""
    return f"""
أنت خبير في الشريعة الإسلامية ومتخصص في تقييم الأفلام والمسلسلات وفقاً للمعايير الإسلامية.

قم بتقييم الفيلم التالي:
العنوان: {movie_title}
السنة: {movie_year}
النوع: {movie_genre}

يرجى تقييم الفيلم بناءً على المعايير التالية وإعطاء تقييم شامل:

1. الأغاني والموسيقى
2. السب والألفاظ البذيئة
3. المشاهد غير اللائقة (التقبيل، العناق)
4. الشذوذ الجنسي
5. التعري والمشاهد الفاضحة
6. تمثيل الملابس الإسلامية
7. الأفكار الخاطئة المخالفة للإسلام

أريد منك:
- تقييم عام من 100 (كلما قل الرقم، كلما كان الفيلم أقل مناسبة للمسلمين)
- تفصيل لكل معيار مع الحكم (مقبول/غير مقبول)
- نصيحة عامة بعدم مشاهدة الأفلام لأنها مضيعة للوقت
- تذكير بعدم الالتهاء عن الصلاة والسنن
- فتوى شرعية مفصلة حول حكم مشاهدة هذا الفيلم

يرجى الرد بتنسيق JSON كالتالي:
{{
    "overallScore": رقم من 0 إلى 100,
    "criteria": [
        {{
            "name": "اسم المعيار",
            "status": "pass" أو "fail",
            "description": "وصف مفصل للمعيار وحالته في الفيلم"
        }}
    ],
    "generalAdvice": "نصيحة عامة بعدم مشاهدة الأفلام",
    "religiousReminder": "تذكير ديني بعدم الالتهاء عن الصلاة والسنن",
    "fatwa": "فتوى شرعية مفصلة حول حكم مشاهدة هذا الفيلم"
}}
"""

@islamfilms_bp.route('/search', methods=['POST'])
def search_movie():
    """البحث عن فيلم أو مسلسل"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'يرجى إدخال اسم الفيلم أو المسلسل'}), 400
        
        # التحقق من أن الاستعلام يتعلق بفيلم
        if not is_movie_query(query):
            return jsonify({'error': 'لا توجد نتائج عن هذا الفيلم'}), 404
        
        # البحث عن الأفلام
        results = search_movies(query)
        
        if not results:
            return jsonify({'error': 'لا توجد نتائج عن هذا الفيلم'}), 404
        
        # إذا كان هناك نتيجة واحدة فقط
        if len(results) == 1:
            return jsonify({
                'multiple': False,
                'movie': results[0]
            })
        
        # إذا كان هناك عدة نتائج
        return jsonify({
            'multiple': True,
            'movies': results
        })
        
    except Exception as e:
        return jsonify({'error': 'حدث خطأ أثناء البحث'}), 500

@islamfilms_bp.route('/evaluate', methods=['POST'])
def evaluate_movie():
    """تقييم فيلم وفقاً للمعايير الإسلامية"""
    try:
        data = request.get_json()
        movie_id = data.get('movieId')
        
        if not movie_id:
            return jsonify({'error': 'معرف الفيلم مطلوب'}), 400
        
        # البحث عن الفيلم في قاعدة البيانات
        movie = None
        for movie_data in MOVIES_DATABASE.values():
            if movie_data['id'] == movie_id:
                movie = movie_data
                break
        
        if not movie:
            return jsonify({'error': 'الفيلم غير موجود'}), 404
        
        # إنشاء prompt للتقييم
        prompt = get_movie_evaluation_prompt(
            movie['title'], 
            movie['year'], 
            movie['genre']
        )
        
        # استدعاء DeepSeek API (محاكاة - يجب استبدالها بالاستدعاء الحقيقي)
        # في الوقت الحالي، سنقوم بإرجاع نتيجة مؤقتة
        evaluation_result = get_mock_evaluation(movie['title'])
        
        return jsonify(evaluation_result)
        
    except Exception as e:
        return jsonify({'error': 'حدث خطأ أثناء التقييم'}), 500

def get_mock_evaluation(movie_title):
    """نتيجة تقييم مؤقتة (يجب استبدالها بالاستدعاء الحقيقي لـ DeepSeek)"""
    
    # تقييمات مختلفة حسب الفيلم
    if "تايتانيك" in movie_title:
        return {
            "title": movie_title,
            "year": "1997",
            "type": "فيلم",
            "overallScore": 25,
            "criteria": [
                {
                    "name": "الأغاني والموسيقى",
                    "status": "fail",
                    "description": "يحتوي الفيلم على موسيقى تصويرية مكثفة وأغاني، وهذا مخالف لآراء جمهور العلماء في تحريم الموسيقى."
                },
                {
                    "name": "السب والألفاظ البذيئة",
                    "status": "fail",
                    "description": "يحتوي على بعض الألفاظ غير اللائقة والسب، وهذا مخالف للآداب الإسلامية."
                },
                {
                    "name": "المشاهد غير اللائقة",
                    "status": "fail",
                    "description": "يحتوي على مشاهد تقبيل وعناق ومشاهد رومانسية غير لائقة بين الرجل والمرأة الأجنبية."
                },
                {
                    "name": "الشذوذ الجنسي",
                    "status": "pass",
                    "description": "لا يحتوي على مشاهد شذوذ جنسي."
                },
                {
                    "name": "التعري والمشاهد الفاضحة",
                    "status": "fail",
                    "description": "يحتوي على مشاهد تعري جزئي ومشاهد فاضحة، وهذا محرم شرعاً."
                },
                {
                    "name": "الملابس الإسلامية",
                    "status": "pass",
                    "description": "لا يسيء لتمثيل الملابس الإسلامية لأنه لا يتناول هذا الموضوع."
                },
                {
                    "name": "الأفكار الخاطئة",
                    "status": "fail",
                    "description": "يروج لأفكار الحب الرومانسي خارج إطار الزواج الشرعي."
                }
            ],
            "generalAdvice": "ننصح بعدم مشاهدة الأفلام عموماً لأنها مضيعة للوقت الثمين الذي يجب أن يُستغل في طاعة الله وتعلم العلم النافع والعمل الصالح. الوقت أمانة وسنُسأل عنه يوم القيامة.",
            "religiousReminder": "احرص على عدم الالتهاء عن الصلاة وأداء السنن والأذكار. اجعل وقتك في طاعة الله وتلاوة القرآن وطلب العلم الشرعي، فهذا خير لك في الدنيا والآخرة.",
            "fatwa": "بناءً على التقييم الشرعي لهذا الفيلم، فإن مشاهدته لا تجوز شرعاً لاحتوائه على عدة مخالفات شرعية منها: الموسيقى والأغاني، والمشاهد غير اللائقة، والتعري الجزئي، والترويج لأفكار مخالفة للشريعة. قال الله تعالى: 'قل للمؤمنين يغضوا من أبصارهم ويحفظوا فروجهم ذلك أزكى لهم إن الله خبير بما يصنعون'. والأولى للمسلم أن يشغل وقته بما ينفعه في دينه ودنياه."
        }
    
    elif "الأسد الملك" in movie_title:
        return {
            "title": movie_title,
            "year": "1994",
            "type": "فيلم رسوم متحركة",
            "overallScore": 60,
            "criteria": [
                {
                    "name": "الأغاني والموسيقى",
                    "status": "fail",
                    "description": "يحتوي على أغاني وموسيقى مكثفة، وهذا مخالف لآراء جمهور العلماء في تحريم الموسيقى."
                },
                {
                    "name": "السب والألفاظ البذيئة",
                    "status": "pass",
                    "description": "لا يحتوي على سب أو ألفاظ بذيئة، وهو مناسب للأطفال من هذا الجانب."
                },
                {
                    "name": "المشاهد غير اللائقة",
                    "status": "pass",
                    "description": "لا يحتوي على مشاهد غير لائقة أو رومانسية فاضحة."
                },
                {
                    "name": "الشذوذ الجنسي",
                    "status": "pass",
                    "description": "لا يحتوي على مشاهد شذوذ جنسي."
                },
                {
                    "name": "التعري والمشاهد الفاضحة",
                    "status": "pass",
                    "description": "لا يحتوي على مشاهد تعري أو فاضحة."
                },
                {
                    "name": "الملابس الإسلامية",
                    "status": "pass",
                    "description": "لا يتناول الموضوع الإسلامي فلا يسيء إليه."
                },
                {
                    "name": "الأفكار الخاطئة",
                    "status": "fail",
                    "description": "قد يحتوي على بعض المفاهيم المخالفة للعقيدة الإسلامية مثل تأليه الطبيعة وبعض المعتقدات الوثنية."
                }
            ],
            "generalAdvice": "رغم أن هذا الفيلم أقل ضرراً من غيره، إلا أننا ننصح بعدم مشاهدة الأفلام عموماً لأنها مضيعة للوقت الثمين. استغل وقتك في طاعة الله وتعلم العلم النافع.",
            "religiousReminder": "لا تنس أداء الصلاة في وقتها والمحافظة على الأذكار والسنن. اجعل الأولوية لتلاوة القرآن وطلب العلم الشرعي.",
            "fatwa": "هذا الفيلم وإن كان أقل ضرراً من الأفلام الأخرى، إلا أنه يحتوي على الموسيقى والأغاني التي يرى جمهور العلماء تحريمها، كما قد يحتوي على بعض المفاهيم المخالفة للعقيدة. والأولى للمسلم تجنب مشاهدته واستغلال الوقت فيما ينفع في الدين والدنيا."
        }
    
    # تقييم افتراضي للأفلام الأخرى
    return {
        "title": movie_title,
        "year": "غير محدد",
        "type": "فيلم",
        "overallScore": 30,
        "criteria": [
            {
                "name": "الأغاني والموسيقى",
                "status": "fail",
                "description": "معظم الأفلام تحتوي على موسيقى وأغاني، وهذا مخالف لآراء جمهور العلماء."
            },
            {
                "name": "السب والألفاظ البذيئة",
                "status": "fail",
                "description": "قد يحتوي على ألفاظ غير لائقة."
            },
            {
                "name": "المشاهد غير اللائقة",
                "status": "fail",
                "description": "قد يحتوي على مشاهد غير لائقة."
            },
            {
                "name": "الشذوذ الجنسي",
                "status": "pass",
                "description": "لا معلومات متاحة حول هذا المعيار."
            },
            {
                "name": "التعري والمشاهد الفاضحة",
                "status": "fail",
                "description": "قد يحتوي على مشاهد غير مناسبة."
            },
            {
                "name": "الملابس الإسلامية",
                "status": "pass",
                "description": "لا معلومات متاحة حول هذا المعيار."
            },
            {
                "name": "الأفكار الخاطئة",
                "status": "fail",
                "description": "قد يحتوي على أفكار مخالفة للشريعة الإسلامية."
            }
        ],
        "generalAdvice": "ننصح بعدم مشاهدة الأفلام عموماً لأنها مضيعة للوقت الثمين. استغل وقتك في طاعة الله وتعلم العلم النافع والعمل الصالح.",
        "religiousReminder": "احرص على عدم الالتهاء عن الصلاة وأداء السنن والأذكار. اجعل وقتك في طاعة الله وتلاوة القرآن وطلب العلم الشرعي.",
        "fatwa": "الأصل في مشاهدة الأفلام التي تحتوي على مخالفات شرعية هو التحريم. ننصح بتجنب مشاهدة هذا الفيلم والاستعاضة عنه بما ينفع في الدين والدنيا. والله أعلم."
    }

