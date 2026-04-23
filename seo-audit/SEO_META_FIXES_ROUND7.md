# Yoast meta descriptions — 3 posts over 160 characters (manual fallback)

If `apply_plan_round7.py` cannot persist `_yoast_wpseo_metadesc` via REST (Yoast often does not register that meta as REST-writable), paste these into **wp-admin → each post → Yoast → Meta description** (under ~155 characters).

| Post ID | Use this meta description (Hebrew) |
|--------|--------------------------------------|
| 322835 | לא כל שאלה צריכה עמוד משלה — איך לבחור נושאים לקידום אורגני בתחום הביטוח ומתי לאחד תכנים לעמוד אחד חזק יותר. |
| 322826 | בחירת נושאים לקידום עוברת משכפול מונחים להבנת צורך — איך זה משפיע על תוכן בתחום הביטוח ואיך להתאים את האסטרטגיה לתוצאות יציבות. |
| 322505 | אתר שנבחן גם לפי תגובה, גילוי ויכולות מתקדמות — מה שינו ב-web.dev, למה זה חשוב ומה צריך לעדכן כדי להמשיך לקבל ציון גבוה. |

After saving each post, purge **FlyingPress** cache and re-check `yoast_head_json.description` via:

`python3 seo-audit/verify_plan_round7.py`
