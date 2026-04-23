<?php
/**
 * Plugin Name: Brndini Yoast REST (כותרת SEO + תיאור מטא)
 * Description: מאפשר עדכון _yoast_wpseo_title ו-_yoast_wpseo_metadesc דרך REST API לכל פוסט/עמוד — לעבודה המונית (AI, CSV, סקריפטים). העתק ל-wp-content/mu-plugins/ והפעל מחדש או רענן — אין צורך בהפעלה מלוח הבקרה.
 * Version: 1.0.0
 * Author: Brndini
 *
 * @package Brndini
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * חשיפת מפתחות Yoast ל-REST כדי ש־meta יופיע ב-context=edit ויתקבל ב-POST.
 * רץ במאוחר כדי לעדכן ארגומנטים אחרי ש-Yoast רושם את המטא.
 */
add_filter(
	'register_post_meta_args',
	static function ( $args, string $meta_key, string $post_type ) {
		$allowed_types = [ 'post', 'page' ];
		$yoast_keys    = [ '_yoast_wpseo_title', '_yoast_wpseo_metadesc' ];

		if ( ! in_array( $post_type, $allowed_types, true ) || ! in_array( $meta_key, $yoast_keys, true ) ) {
			return $args;
		}

		$args['show_in_rest'] = true;

		if ( empty( $args['auth_callback'] ) ) {
			$args['auth_callback'] = static function () {
				return current_user_can( 'edit_posts' );
			};
		}

		if ( empty( $args['sanitize_callback'] ) ) {
			$args['sanitize_callback'] = 'sanitize_text_field';
		}

		return $args;
	},
	99,
	3
);
