USE crawler;

CREATE TABLE IF NOT EXISTS `crawler_history` (
  `id` bigint(20) NOT NULL auto_increment,
  `media_id` varchar(36) NOT NULL,
  `election_id` varchar(36) NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `last_crawl_at` datetime NOT NULL DEFAULT '2017-01-01 00:00:01',
  UNIQUE KEY `k_crawler_context` (`media_id`, `election_id`),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;;

CREATE TABLE IF NOT EXISTS `news` (
    `id` bigint(20) NOT NULL auto_increment,
    `media_id` varchar(36) NOT NULL,
    `election_id` varchar(36) NOT NULL,
    `title` varchar(255) collate utf8mb4_unicode_ci NOT NULL,
    `raw_content` text collate utf8mb4_unicode_ci NOT NULL,
    `url` varchar(255) collate utf8mb4_unicode_ci NOT NULL,
    `is_analyzed` bool DEFAULT false,
    `author_name` varchar(255) collate utf8mb4_unicode_ci,
    `published_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `inserted_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY `k_media_id` (`media_id`),
    KEY `k_election_id` (`election_id`),
    UNIQUE KEY `k_url` (`url`),
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `crawler_history` (`id`, `media_id`, `election_id`, `created_at`, `last_crawl_at`)
VALUES
  (1, 'detiknewscom', 'pilpres_2019', '2018-01-01 00:00:00', '2017-01-01 00:00:01'),
  (2, 'kompascom', 'pilpres_2019', '2018-01-01 00:00:00', '2017-01-01 00:00:01')
