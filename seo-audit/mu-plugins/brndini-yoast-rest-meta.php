<?php
/**
 * Plugin Name: Brndini Yoast REST (כותרת SEO + תיאור מטא)
 * Description: שדות REST ברמת הפוסט/עמוד: yoast_seo_title ו-yoast_seo_metadesc — נכתבים ל-_yoast_wpseo_title ו-_yoast_wpseo_metadesc. מתאים לייבוא CSV ואוטומציה.
 * Version: 1.1.0
 * Author: Brndini
 *
 * @package Brndini
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * ניסיון לאחד show_in_rest למפתחות Yoast אם WordPress מאפשר (תלוי סדר טעינה).
 *
 * @param array<string,mixed> $args
 * @return array<string,mixed>
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
	99999,
	3
);

/**
 * @param mixed $object Prepared post as array או WP_Post — תלוי בגרסת WP.
 */
add_action(
	'rest_api_init',
	static function () {
		$get_id = static function ( $object ): int {
			if ( $object instanceof WP_Post ) {
				return (int) $object->ID;
			}
			if ( is_array( $object ) && isset( $object['id'] ) ) {
				return (int) $object['id'];
			}

			return 0;
		};

		$types = [ 'post', 'page' ];

		foreach ( $types as $post_type ) {
			register_rest_field(
				$post_type,
				'yoast_seo_title',
				[
					'schema'          => [
						'description' => 'Yoast SEO title (נשמר ב-_yoast_wpseo_title)',
						'type'        => 'string',
						'context'     => [ 'view', 'edit' ],
					],
					'get_callback'    => static function ( $object ) use ( $get_id ) {
						$id = $get_id( $object );

						return $id ? (string) get_post_meta( $id, '_yoast_wpseo_title', true ) : '';
					},
					'update_callback' => static function ( $value, $object ) {
						if ( ! $object instanceof WP_Post ) {
							return false;
						}
						if ( ! current_user_can( 'edit_post', $object->ID ) ) {
							return false;
						}
						$value = is_string( $value ) ? sanitize_text_field( $value ) : '';
						update_post_meta( $object->ID, '_yoast_wpseo_title', $value );

						return true;
					},
				]
			);

			register_rest_field(
				$post_type,
				'yoast_seo_metadesc',
				[
					'schema'          => [
						'description' => 'Yoast meta description (נשמר ב-_yoast_wpseo_metadesc)',
						'type'        => 'string',
						'context'     => [ 'view', 'edit' ],
					],
					'get_callback'    => static function ( $object ) use ( $get_id ) {
						$id = $get_id( $object );

						return $id ? (string) get_post_meta( $id, '_yoast_wpseo_metadesc', true ) : '';
					},
					'update_callback' => static function ( $value, $object ) {
						if ( ! $object instanceof WP_Post ) {
							return false;
						}
						if ( ! current_user_can( 'edit_post', $object->ID ) ) {
							return false;
						}
						$value = is_string( $value ) ? sanitize_text_field( $value ) : '';
						update_post_meta( $object->ID, '_yoast_wpseo_metadesc', $value );

						return true;
					},
				]
			);
		}
	},
	11
);
