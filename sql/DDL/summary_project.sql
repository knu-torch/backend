-- torch.summary_project definition

CREATE TABLE `summary_project` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `create_at` timestamp NOT NULL,
  `title` varchar(1000) DEFAULT NULL,
  `libs` varchar(10000) DEFAULT NULL,
  `deploy_info` varchar(1000) DEFAULT NULL,
  `req_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `summary_project_request_FK` (`req_id`),
  CONSTRAINT `summary_project_request_FK` FOREIGN KEY (`req_id`) REFERENCES `request` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;