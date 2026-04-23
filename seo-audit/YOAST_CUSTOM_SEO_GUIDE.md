# כותרות SEO מותאמות אישית לכל עמוד ופוסט (קידום אורגני)

מטרה: **כותרת SEO (Yoast)** ו־**תיאור מטא** ייחודיים לכל URL — לא רק תבנית גלובלית.

## שלב 1 — קובץ PHP באתר (חד־פעמי)

1. צור תיקייה `wp-content/mu-plugins/` אם אין.
2. העתק את הקובץ מהריפו:  
   `seo-audit/mu-plugins/brndini-yoast-rest-meta.php`  
   ל־`wp-content/mu-plugins/brndini-yoast-rest-meta.php`
3. אין צורך “להפעיל” תוסף — קבצי mu-plugins נטענים אוטומטית.

הקובץ גורם ל־WordPress לקבל עדכונים ל־`_yoast_wpseo_title` ו־`_yoast_wpseo_metadesc` דרך REST (Application Password).

## שלב 2 — ייצוא תבנית CSV

```bash
export WORDPRESS_USERNAME='...'
export WORDPRESS_APP_PASSWORD='...'
python3 seo-audit/export_yoast_csv_template.py > seo-custom-template.csv
```

הקובץ כולל עמודות: `type`, `id`, `url`, `post_title`, המצב הנוכחי ב־Yoast, ועמודות ריקות `seo_title`, `meta_desc` למילוי.

## שלב 3 — מילוי כללים לקידום אורגני (מומלץ)

**כותרת SEO (`seo_title`)**

- **ייחודית** לכל URL; אל תכפיל אותה טקסטואלית על עשרות עמודים.
- **מילת מפתח ראשית** קרובה לתחילת הכותרת (אם רלוונטי לכוונת החיפוש).
- אורך מעשי ל־Google: בערך **50–60 תווים** (עברית לפעמים נחתכת אחרי ~580 פיקסלים).
- אפשר סיומת מותג קצרה: `| ברנדיני` רק אם נשאר מקום ולא “דוחף” החוצה את המפתח.
- התאמה ל־**כוונת חיפוש** (מידע / השוואה / רכישה) — לא רק שם גנרי של השירות.

**תיאור מטא (`meta_desc`)**

- **120–155 תווים**; משפט מלא עם ערך ברור (למה ללחוץ).
- **לא** לשכפל את הכותרת; להרחיב ב־benefit או הבטחה ספציפית.
- קריאה לפעולה עדינה בסוף אם מתאים (“מדריך מלא”, “בדיקה חינם” וכו’).

## שלב 4 — ייבוא חזרה לאתר

```bash
python3 seo-audit/apply_seo_titles_from_csv.py seo-custom-filled.csv
```

אחרי זה: **ניקוי מטמון FlyingPress** ובדיקה ב־2–3 URLs ב־`yoast_head_json` או ב־“תצוגה מקדימה” ב־Yoast.

## אלטרנטיבה בלי קוד

בכל עמוד/פוסט: Yoast → **תצוגה מקדימה של גוגל** → עריכת כותרת SEO ותיאור — הכי איטי אבל הכי ויזואלי.

## הערות

- אם הייבוא מדפיס `WARN ... title may not persist` — ה־mu-plugin לא הועלה או יש תוסף שחוסם.
- ל־**Custom Post Types** (אם יש): אפשר להרחיב את מערך `$allowed_types` בקובץ ה־PHP.
